"""
Google GenAI wrapper used by the historical prototype and controlled benchmark.
"""

from typing import Dict
from google import genai
from google.genai import types


def get_client(api_key: str):
    return genai.Client(api_key=api_key)


def call_model(model_name: str, prompt: str, api_key: str, temperature: float = 0.0) -> Dict:
    client = get_client(api_key)
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature),
        )
        return {
            "model": model_name,
            "output": response.text or "",
            "success": True,
            "error": None,
        }
    except Exception as e:
        return {
            "model": model_name,
            "output": "",
            "success": False,
            "error": str(e),
        }
