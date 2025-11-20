"""
POC Demo: Neo4j Embeddings
"""
import json
import time
from pathlib import Path
from src.embeddings import EmbeddingGenerator
from src.neo4j_manager import Neo4jEmbeddingsManager
from src.search import EmbeddingSearch
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_sample_documents(filepath: str = "data/sample_docs.json"):
    """Load sample documents from JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data['documents']


def populate_database(
    documents: list,
    embeddings: EmbeddingGenerator,
    neo4j: Neo4jEmbeddingsManager
):
    """
    Populate Neo4j with documents and embeddings
    
    Args:
        documents: List of document dictionaries
        embeddings: Embedding generator
        neo4j: Neo4j manager
    """
    logger.info(f"Populating database with {len(documents)} documents...")
    
    for doc in documents:
        # Generate embedding
        logger.info(f"Processing: {doc['title']}")
        embedding = embeddings.generate_embedding(doc['content'])
        
        # Create document node
        neo4j.create_document(
            doc_id=doc['id'],
            title=doc['title'],
            content=doc['content'],
            embedding=embedding,
            metadata=doc.get('metadata', {})
        )
        
        time.sleep(0.1)  # Rate limiting
    
    logger.info("Database population complete")


def demo_vector_search(search: EmbeddingSearch):
    """Demonstrate vector similarity search"""
    logger.info("\n" + "="*80)
    logger.info("DEMO 1: Vector Similarity Search")
    logger.info("="*80)
    
    queries = [
        "neural networks and deep learning",
        "language models and text processing",
        "image recognition systems"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 80)
        
        results = search.search(query, top_k=3, include_context=False)
        
        for i, result in enumerate(results, 1):
            node = result['node']
            score = result['score']
            
            print(f"\n{i}. {node['title']}")
            print(f"   Similarity: {score:.3f}")
            print(f"   Category: {node['metadata'].get('category', 'N/A')}")
            print(f"   Preview: {node['content'][:100]}...")


def demo_graph_context(search: EmbeddingSearch):
    """Demonstrate graph-based context retrieval"""
    logger.info("\n" + "="*80)
    logger.info("DEMO 2: Graph Context Retrieval")
    logger.info("="*80)
    
    query = "machine learning algorithms"
    print(f"\n🔍 Query: '{query}'")
    print("-" * 80)
    
    results = search.search(query, top_k=2, include_context=True)
    
    for i, result in enumerate(results, 1):
        node = result['node']
        score = result['score']
        related = result.get('related', [])
        
        print(f"\n{i}. {node['title']} (Score: {score:.3f})")
        
        if related:
            print(f"   Related documents:")
            for rel_doc in related[:3]:
                print(f"   - {rel_doc['title']} (Relevance: {rel_doc['score']:.3f})")


def demo_hybrid_search(search: EmbeddingSearch):
    """Demonstrate hybrid search (vector + keywords)"""
    logger.info("\n" + "="*80)
    logger.info("DEMO 3: Hybrid Search (Vector + Keywords)")
    logger.info("="*80)
    
    query = "artificial intelligence"
    keywords = ["neural", "learning", "models"]
    
    print(f"\n🔍 Query: '{query}'")
    print(f"   Keywords: {keywords}")
    print("-" * 80)
    
    results = search.hybrid_search(query, keywords=keywords, top_k=3)
    
    for i, result in enumerate(results, 1):
        node = result['node']
        score = result['score']
        
        print(f"\n{i}. {node['title']}")
        print(f"   Combined Score: {score:.3f}")
        print(f"   Category: {node['metadata'].get('category', 'N/A')}")


def demo_statistics(neo4j: Neo4jEmbeddingsManager):
    """Show database statistics"""
    logger.info("\n" + "="*80)
    logger.info("Database Statistics")
    logger.info("="*80)
    
    stats = neo4j.get_statistics()
    
    print(f"\nDocuments: {stats['documents']}")
    print(f"Chunks: {stats['chunks']}")
    print(f"Similarity Relationships: {stats['similarity_relationships']}")


def main():
    """Main POC demonstration"""
    print("\n" + "="*80)
    print("Neo4j Embeddings POC - Demo")
    print("="*80)
    
    # Initialize components
    logger.info("Initializing components...")
    embeddings = EmbeddingGenerator(provider="openai")
    
    with Neo4jEmbeddingsManager() as neo4j:
        # Setup schema
        logger.info("Setting up schema...")
        neo4j.setup_schema(vector_dimensions=embeddings.dimensions)
        
        # Check if database is empty
        stats = neo4j.get_statistics()
        if stats['documents'] == 0:
            # Load and populate sample data
            logger.info("Loading sample documents...")
            documents = load_sample_documents()
            
            populate_database(documents, embeddings, neo4j)
            
            # Create similarity relationships
            logger.info("Creating similarity relationships...")
            neo4j.create_similarity_relationships(
                node_label="Document",
                similarity_threshold=0.7,
                max_connections=3
            )
        else:
            logger.info("Using existing data in database")
        
        # Initialize search
        search = EmbeddingSearch(embeddings, neo4j)
        
        # Run demonstrations
        demo_vector_search(search)
        demo_graph_context(search)
        demo_hybrid_search(search)
        demo_statistics(neo4j)
        
        print("\n" + "="*80)
        print("POC Demo Complete!")
        print("="*80)
        print("\nNext steps:")
        print("1. Open Neo4j Browser: http://localhost:7474")
        print("2. Run: MATCH (d:Document)-[r:SIMILAR_TO]->(d2:Document) RETURN d, r, d2")
        print("3. Visualize the knowledge graph")


if __name__ == "__main__":
    main()