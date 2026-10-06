from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Any, Dict
from .metrics import aggregate

def read_raw_results(results_root: str | Path) -> list[Dict[str, Any]]:
    root = Path(results_root)
    rows: list[Dict[str, Any]] = []
    for path in sorted(root.rglob("raw_results.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows

def evaluate_results(results_root: str | Path) -> list[Dict[str, Any]]:
    return aggregate(read_raw_results(results_root))

def write_summary(results_root: str | Path) -> tuple[Path, Path]:
    root = Path(results_root)
    summary = evaluate_results(root)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "summary.json"
    csv_path = root / "summary.csv"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        if summary:
            writer = csv.DictWriter(handle, fieldnames=list(summary[0].keys()))
            writer.writeheader()
            writer.writerows(summary)
    return json_path, csv_path
