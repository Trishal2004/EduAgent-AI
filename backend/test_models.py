from google import genai
from app.config.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)
try:
    res = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Hello"
    )
    print("gemini-3.5-flash works!")
except Exception as e:
    print("3.5-flash:", e)

try:
    res = client.models.generate_content(
        model="gemini-3.0-flash",
        contents="Hello"
    )
    print("gemini-3.0-flash works!")
except Exception as e:
    print("3.0-flash:", e)
