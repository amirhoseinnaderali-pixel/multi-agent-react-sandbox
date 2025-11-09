"""
Google AI API client for ReAct Docker Sandbox
Simple wrapper for calling Google Gemini models
"""

from google import genai
from typing import Dict


def get_client(api_key: str):
    """Initialize Google AI client"""
    return genai.Client(api_key=api_key)


def call_model(model_name: str, prompt: str, api_key: str) -> Dict:
    """
    Call a single Google Gemini model and return result
    
    Args:
        model_name: Name of the model (e.g., "gemini-2.5-pro")
        prompt: The prompt to send to the model
        api_key: Google AI API key
        
    Returns:
        Dictionary with keys:
            - model: Model name
            - output: Generated text output
            - success: Boolean indicating success
            - error: Error message if failed, None if successful
    """
    client = get_client(api_key)
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        return {
            "model": model_name,
            "output": response.text,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "model": model_name,
            "output": "",
            "success": False,
            "error": str(e)
        }

