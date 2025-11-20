"""
Search functionality for Neo4j embeddings
"""
from typing import List, Dict, Any
from src.embeddings import EmbeddingGenerator
from src.neo4j_manager import Neo4jEmbeddingsManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingSearch:
    """Search interface for Neo4j embeddings"""
    
    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        neo4j_manager: Neo4jEmbeddingsManager
    ):
        """
        Initialize search
        
        Args:
            embedding_generator: Embedding generator instance
            neo4j_manager: Neo4j manager instance
        """
        self.embeddings = embedding_generator
        self.neo4j = neo4j_manager
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        node_type: str = "Document",
        include_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents/chunks
        
        Args:
            query: Search query text
            top_k: Number of results
            node_type: "Document" or "Chunk"
            include_context: Include graph context
            
        Returns:
            Search results with scores
        """
        logger.info(f"Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embeddings.generate_embedding(query)
        
        # Perform vector search
        results = self.neo4j.vector_search(
            query_embedding=query_embedding,
            top_k=top_k,
            node_label=node_type
        )
        
        # Optionally add graph context
        if include_context and node_type == "Document":
            for result in results:
                doc_id = result["node"]["id"]
                context = self.neo4j.get_document_with_context(doc_id, max_hops=1)
                result["related"] = context["related"]
        
        return results
    
    def hybrid_search(
        self,
        query: str,
        keywords: List[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (vector + keyword)
        
        Args:
            query: Search query
            keywords: Additional keywords
            top_k: Number of results
            
        Returns:
            Search results
        """
        logger.info(f"Hybrid search for: '{query}' with keywords: {keywords}")
        
        query_embedding = self.embeddings.generate_embedding(query)
        
        results = self.neo4j.hybrid_search(
            query_embedding=query_embedding,
            keywords=keywords,
            top_k=top_k
        )
        
        return results


# Example usage
if __name__ == "__main__":
    embeddings = EmbeddingGenerator(provider="openai")
    
    with Neo4jEmbeddingsManager() as neo4j:
        search = EmbeddingSearch(embeddings, neo4j)
        
        results = search.search(
            query="machine learning algorithms",
            top_k=3
        )
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['node']['title']}")
            print(f"   Score: {result['score']:.3f}")