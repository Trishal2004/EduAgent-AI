import asyncio
from app.services.gemini_service import GeminiService
from pydantic import BaseModel
from typing import List

class TestCard(BaseModel):
    question: str
    answer: str

class TestResponse(BaseModel):
    cards: List[TestCard]

def run():
    svc = GeminiService()
    res = svc.generate_json("You are an expert. Return exactly 2 cards.", "Topic: Math", TestResponse)
    print("Success:", res)

if __name__ == "__main__":
    run()
