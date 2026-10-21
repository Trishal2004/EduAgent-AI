from google import genai
from pydantic import BaseModel
from typing import List
import json
import os
import sys

# Load API key from env file
from dotenv import load_dotenv
load_dotenv()

key = os.environ.get("GEMINI_API_KEY")
if not key:
    print("NO KEY")
    sys.exit(1)

class AIFlashcard(BaseModel):
    question: str
    answer: str
    difficulty: str

class AIFlashcardList(BaseModel):
    cards: List[AIFlashcard]

client = genai.Client(api_key=key)
system_prompt = "You are an expert tutor. Create exactly 2 high-quality flashcards for the given topic. The target difficulty is medium."
try:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=f"System: {system_prompt}\n\nUser: Topic: deadlock\nCard Type: definition",
        config={"response_mime_type": "application/json", "response_schema": AIFlashcardList}
    )
    print("RESPONSE TEXT:")
    print(response.text)
    ai_response = AIFlashcardList(**json.loads(response.text))
    print(ai_response)
except Exception as e:
    print(f"ERROR: {e}")
