#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vmar_ps.evaluation import write_summary

def main():
    parser = argparse.ArgumentParser(description="Aggregate VMAR-PS raw results.")
    parser.add_argument("--results", default="results")
    args = parser.parse_args()
    json_path, csv_path = write_summary(args.results)
    print(f"summary_json={json_path}")
    print(f"summary_csv={csv_path}")

if __name__ == "__main__":
    main()
