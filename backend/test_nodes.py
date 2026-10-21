import asyncio
from app.services.agent.nodes import generate_answer

async def test():
    state = {
        "original_question": "Explain artificial intelligence in simple words.",
        "chat_history": [],
        "require_retrieval": False
    }
    res = await generate_answer(state)
    print("SUCCESS")
    print(res["answer"]["content"][:100])

if __name__ == "__main__":
    asyncio.run(test())
