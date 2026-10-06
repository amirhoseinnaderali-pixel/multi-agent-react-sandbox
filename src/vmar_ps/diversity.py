from __future__ import annotations
import re
from itertools import combinations
from typing import Any, Dict, Iterable

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+")

def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text or ""))

def jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)

def summarize(candidates: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    candidates = list(candidates)
    codes = [str(c.get("first_code", "")) for c in candidates]
    pair_count = len(codes) * (len(codes) - 1) // 2
    pairs = [jaccard(a, b) for a, b in combinations(codes, 2)]
    return {
        "num_agents": len(candidates),
        "unique_models": len({c.get("model") for c in candidates}),
        "unique_providers": len({c.get("provider") for c in candidates}),
        "unique_prompt_variants": len({c.get("prompt_variant") for c in candidates}),
        "pairwise_code_jaccard_mean": round(sum(pairs) / len(pairs), 4) if pairs else None,
        "pairwise_code_jaccard_min": round(min(pairs), 4) if pairs else None,
        "pairwise_code_jaccard_max": round(max(pairs), 4) if pairs else None,
        "exact_first_code_agreement_rate": (
            sum(1 for a, b in combinations(codes, 2) if a == b) / pair_count
            if pair_count else None
        ),
    }
