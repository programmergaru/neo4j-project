"""
Embeddings generation module
"""
import os
from typing import List, Union
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()


class EmbeddingGenerator:
    """Generate embeddings using OpenAI or local models"""
    
    def __init__(self, provider: str = "openai", model: str = None):
        """
        Initialize embedding generator
        
        Args:
            provider: 'openai' or 'sentence-transformers'
            model: Model name
        """
        self.provider = provider
        
        if provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = model or "text-embedding-3-small"
            self.dimensions = 1536
        elif provider == "sentence-transformers":
            self.model = model or "all-MiniLM-L6-v2"
            self.st_model = SentenceTransformer(self.model)
            self.dimensions = self.st_model.get_sentence_embedding_dimension()
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        if self.provider == "openai":
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        
        elif self.provider == "sentence-transformers":
            embedding = self.st_model.encode(text)
            return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if self.provider == "openai":
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [item.embedding for item in response.data]
        
        elif self.provider == "sentence-transformers":
            embeddings = self.st_model.encode(texts)
            return embeddings.tolist()


# Example usage
if __name__ == "__main__":
    # Test with OpenAI
    generator = EmbeddingGenerator(provider="openai")
    
    test_text = "This is a sample document about machine learning."
    embedding = generator.generate_embedding(test_text)
    
    print(f"Provider: {generator.provider}")
    print(f"Model: {generator.model}")
    print(f"Dimensions: {generator.dimensions}")
    print(f"Embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")