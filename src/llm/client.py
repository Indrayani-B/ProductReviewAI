import requests
from src.utils.config import GEMINI_API_KEY

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def call_llm(prompt, temperature=0.3, max_tokens=1500, retries=3):
    """
    Single entry point for all LLM calls in this project.
    Calls Gemini REST API directly using requests.
    thinkingBudget=0 disables internal reasoning tokens so max_tokens 
    is fully available for the actual response.
    """
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }
    
    response = requests.post(GEMINI_URL, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()