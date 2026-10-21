import json
from fastapi import HTTPException
from google import genai
from app.config.config import settings

class GeminiService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise HTTPException(status_code=400, detail="Gemini API Key is missing. Please configure it in .env.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.default_model = settings.GEMINI_MODEL

    def generate_json(self, system_prompt: str, user_prompt: str, response_schema: type, model: str = None) -> dict:
        """
        Generates structured JSON using Gemini.
        Returns the parsed dictionary.
        """
        try:
            response = self.client.models.generate_content(
                model=model or self.default_model,
                contents=f"System: {system_prompt}\n\nUser: {user_prompt}",
                config={
                    "response_mime_type": "application/json", 
                    "response_schema": response_schema
                }
            )
            return json.loads(response.text)
        except Exception as e:
            error_str = str(e)
            print(f"Gemini API Generation Failed: {error_str}")
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota exceeded" in error_str:
                raise HTTPException(status_code=429, detail="Gemini API rate limit exceeded. Please wait a moment and try again.")
            raise HTTPException(status_code=500, detail=f"AI generation failed: {error_str}")
