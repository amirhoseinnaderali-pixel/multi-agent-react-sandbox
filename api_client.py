from __future__ import annotations

"""Backward-compatible API wrapper.

The research framework uses src/vmar_ps/llm.py internally.
"""

from pathlib import Path
import sys
from typing import Dict

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from vmar_ps.llm import GeminiClient


def get_client(api_key: str):
    return GeminiClient(api_key=api_key)


def call_model(model_name: str, prompt: str, api_key: str) -> Dict:
    result = GeminiClient(api_key=api_key).generate(
        model=model_name,
        prompt=prompt,
        temperature=0.2,
        max_output_tokens=2048,
    )
    return {
        "model": result.model,
        "output": result.text,
        "success": result.success,
        "error": result.error,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "total_tokens": result.total_tokens,
    }
