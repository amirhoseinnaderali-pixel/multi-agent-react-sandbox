from __future__ import annotations
import copy
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict
import yaml

_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)(?::-(.*?))?\}")

def _expand_env(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    if isinstance(value, str):
        def repl(match: re.Match[str]) -> str:
            name, default = match.group(1), match.group(2)
            return os.environ.get(name, default if default is not None else match.group(0))
        return _ENV_PATTERN.sub(repl, value)
    return value

def load_config(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    config = _expand_env(raw)
    config["_config_path"] = str(path)
    return config

def resolve_agents(config: Dict[str, Any]) -> list[Dict[str, Any]]:
    pool = copy.deepcopy(config.get("agents", []))
    if not pool:
        raise ValueError("Configuration must define at least one agent profile.")
    requested = int(config.get("num_agents", len(pool)))
    if requested <= len(pool):
        return pool[:requested]
    if not bool(config.get("cycle_agent_pool", True)):
        raise ValueError("num_agents exceeds agent profiles and cycle_agent_pool=false.")
    expanded = []
    for index in range(requested):
        profile = copy.deepcopy(pool[index % len(pool)])
        base_id = str(profile.get("agent_id", f"agent_{index + 1:02d}"))
        profile["agent_id"] = f"{base_id}__instance_{index + 1:02d}"
        profile["pool_index"] = index % len(pool)
        expanded.append(profile)
    return expanded

def canonical_config(config: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = copy.deepcopy(config)
    cleaned.pop("_config_path", None)
    return cleaned

def experiment_id(config: Dict[str, Any], benchmark_digest: str) -> str:
    payload = {"config": canonical_config(config), "benchmark_digest": benchmark_digest,
               "seed": int(config.get("seed", 0))}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]

def benchmark_digest(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
