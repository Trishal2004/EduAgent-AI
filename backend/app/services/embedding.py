from typing import List
from openai import AsyncOpenAI
from app.config.config import settings
import random

class EmbeddingService:
    def __init__(self):
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-placeholder-replace-with-real-key":
            pass # We will mock it later
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Sends a batch of texts to OpenAI and returns their vector embeddings.
        Batches save significant time over sending them one-by-one.
        """
        if not texts:
            return []
            
        # OpenAI historically recommended replacing newlines with spaces for better results
        clean_texts = [text.replace("\n", " ") for text in texts]
        
        if settings.OPENAI_API_KEY == "YOUR_REAL_OPENAI_API_KEY":
            # Return dummy vectors for mocking without an API key
            import random
            return [[random.random() for _ in range(1536)] for _ in texts]
            
        try:
            response = await self.client.embeddings.create(
                input=clean_texts,
                model=self.model
            )
            
            # OpenAI returns them in order, but it's safe to sort by the given index
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            # Handle API errors gracefully
            print(f"OpenAI Embedding Error: {e}")
            raise
