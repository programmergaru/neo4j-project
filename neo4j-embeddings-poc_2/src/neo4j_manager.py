"""
Neo4j database manager for embeddings - FIXED VERSION
"""
import os
import json
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jEmbeddingsManager:
    """Manage embeddings in Neo4j graph database"""
    
    def __init__(
        self,
        uri: str = None,
        user: str = None,
        password: str = None,
        database: str = "neo4j"
    ):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j connection URI
            user: Database user
            password: Database password
            database: Database name
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password123")
        self.database = database
        
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
        
        logger.info(f"Connected to Neo4j at {self.uri}")
    
    def close(self):
        """Close database connection"""
        self.driver.close()
        logger.info("Neo4j connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def setup_schema(self, vector_dimensions: int = 1536):
        """
        Create indexes and vector indexes for embeddings
        
        Args:
            vector_dimensions: Dimensionality of embedding vectors
        """
        logger.info("Setting up Neo4j schema...")
        
        with self.driver.session(database=self.database) as session:
            # Create constraints
            session.run("""
                CREATE CONSTRAINT document_id IF NOT EXISTS
                FOR (d:Document)
                REQUIRE d.id IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT chunk_id IF NOT EXISTS
                FOR (c:Chunk)
                REQUIRE c.id IS UNIQUE
            """)
            
            # Create regular indexes
            session.run("""
                CREATE INDEX document_title IF NOT EXISTS
                FOR (d:Document)
                ON (d.title)
            """)
            
            # Create vector index for Document embeddings
            session.run(f"""
                CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
                FOR (d:Document)
                ON (d.embedding)
                OPTIONS {{
                    indexConfig: {{
                        `vector.dimensions`: {vector_dimensions},
                        `vector.similarity_function`: 'cosine'
                    }}
                }}
            """)
            
            # Create vector index for Chunk embeddings
            session.run(f"""
                CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
                FOR (c:Chunk)
                ON (c.embedding)
                OPTIONS {{
                    indexConfig: {{
                        `vector.dimensions`: {vector_dimensions},
                        `vector.similarity_function`: 'cosine'
                    }}
                }}
            """)
            
            logger.info("Schema setup complete")
    
    def create_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a document node with embedding
        
        Args:
            doc_id: Unique document ID
            title: Document title
            content: Document content
            embedding: Embedding vector
            metadata: Additional metadata (will be stored as JSON string)
            
        Returns:
            Created document properties
        """
        with self.driver.session(database=self.database) as session:
            # Convert metadata to JSON string
            metadata_json = json.dumps(metadata) if metadata else "{}"
            
            result = session.run("""
                MERGE (d:Document {id: $doc_id})
                SET d.title = $title,
                    d.content = $content,
                    d.embedding = $embedding,
                    d.created_at = datetime(),
                    d.metadata_json = $metadata_json
                RETURN d
            """, {
                "doc_id": doc_id,
                "title": title,
                "content": content,
                "embedding": embedding,
                "metadata_json": metadata_json
            })
            
            record = result.single()
            logger.info(f"Created document: {doc_id}")
            
            # Parse metadata back for return
            node = dict(record["d"])
            if "metadata_json" in node:
                node["metadata"] = json.loads(node["metadata_json"])
                del node["metadata_json"]
            
            return node
    
    def create_chunk(
        self,
        chunk_id: str,
        doc_id: str,
        text: str,
        embedding: List[float],
        chunk_index: int,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a text chunk node with embedding
        
        Args:
            chunk_id: Unique chunk ID
            doc_id: Parent document ID
            text: Chunk text
            embedding: Embedding vector
            chunk_index: Position in document
            metadata: Additional metadata
            
        Returns:
            Created chunk properties
        """
        with self.driver.session(database=self.database) as session:
            metadata_json = json.dumps(metadata) if metadata else "{}"
            
            result = session.run("""
                MATCH (d:Document {id: $doc_id})
                CREATE (c:Chunk {
                    id: $chunk_id,
                    text: $text,
                    embedding: $embedding,
                    chunk_index: $chunk_index,
                    metadata_json: $metadata_json,
                    created_at: datetime()
                })
                CREATE (d)-[:HAS_CHUNK]->(c)
                RETURN c
            """, {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "text": text,
                "embedding": embedding,
                "chunk_index": chunk_index,
                "metadata_json": metadata_json
            })
            
            record = result.single()
            logger.info(f"Created chunk: {chunk_id} for document: {doc_id}")
            
            # Parse metadata back
            node = dict(record["c"])
            if "metadata_json" in node:
                node["metadata"] = json.loads(node["metadata_json"])
                del node["metadata_json"]
            
            return node
    
    def vector_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        node_label: str = "Document",
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            node_label: Node label to search (Document or Chunk)
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar nodes with scores
        """
        index_name = f"{node_label.lower()}_embeddings"
        
        with self.driver.session(database=self.database) as session:
            result = session.run(f"""
                CALL db.index.vector.queryNodes($index_name, $top_k, $query_embedding)
                YIELD node, score
                WHERE score >= $threshold
                RETURN node, score
                ORDER BY score DESC
            """, {
                "index_name": index_name,
                "top_k": top_k,
                "query_embedding": query_embedding,
                "threshold": similarity_threshold
            })
            
            results = []
            for record in result:
                node = dict(record["node"])
                
                # Parse metadata if present
                if "metadata_json" in node:
                    node["metadata"] = json.loads(node["metadata_json"])
                    del node["metadata_json"]
                
                score = record["score"]
                results.append({
                    "node": node,
                    "score": score
                })
            
            logger.info(f"Found {len(results)} results for vector search")
            return results
    
    def create_similarity_relationships(
        self,
        node_label: str = "Document",
        similarity_threshold: float = 0.8,
        max_connections: int = 5
    ):
        """
        Create SIMILAR_TO relationships between similar nodes
        
        Args:
            node_label: Node label to process
            similarity_threshold: Minimum similarity to create relationship
            max_connections: Maximum connections per node
        """
        logger.info(f"Creating similarity relationships for {node_label} nodes...")
        
        with self.driver.session(database=self.database) as session:
            # Get all nodes with embeddings
            nodes = session.run(f"""
                MATCH (n:{node_label})
                WHERE n.embedding IS NOT NULL
                RETURN n.id as id, n.embedding as embedding
            """)
            
            node_list = [dict(record) for record in nodes]
            
            # For each node, find similar nodes
            relationships_created = 0
            for node in node_list:
                result = session.run(f"""
                    MATCH (n:{node_label} {{id: $node_id}})
                    CALL db.index.vector.queryNodes(
                        $index_name,
                        $max_connections + 1,
                        n.embedding
                    )
                    YIELD node as similar, score
                    WHERE similar.id <> $node_id
                        AND score >= $threshold
                    WITH n, similar, score
                    MERGE (n)-[r:SIMILAR_TO]->(similar)
                    SET r.score = score
                    RETURN count(r) as relationships_created
                """, {
                    "node_id": node["id"],
                    "index_name": f"{node_label.lower()}_embeddings",
                    "max_connections": max_connections,
                    "threshold": similarity_threshold
                })
                
                count = result.single()["relationships_created"]
                relationships_created += count
                logger.info(f"Created {count} similarity relationships for {node['id']}")
            
            logger.info(f"Total relationships created: {relationships_created}")
    
    def hybrid_search(
        self,
        query_embedding: List[float],
        keywords: List[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search: vector similarity + keyword matching
        
        Args:
            query_embedding: Query embedding
            keywords: Keywords to match
            top_k: Number of results
            
        Returns:
            Combined search results
        """
        with self.driver.session(database=self.database) as session:
            if keywords:
                result = session.run("""
                    CALL db.index.vector.queryNodes('document_embeddings', $top_k * 2, $query_embedding)
                    YIELD node, score as vector_score
                    WHERE any(keyword IN $keywords WHERE node.content CONTAINS keyword)
                    WITH node, vector_score,
                         size([keyword IN $keywords WHERE node.content CONTAINS keyword]) as keyword_matches
                    WITH node, 
                         vector_score * 0.7 + (toFloat(keyword_matches) / size($keywords)) * 0.3 as combined_score
                    RETURN node, combined_score as score
                    ORDER BY combined_score DESC
                    LIMIT $top_k
                """, {
                    "query_embedding": query_embedding,
                    "keywords": keywords,
                    "top_k": top_k
                })
            else:
                # Fall back to pure vector search
                result = session.run("""
                    CALL db.index.vector.queryNodes('document_embeddings', $top_k, $query_embedding)
                    YIELD node, score
                    RETURN node, score
                    ORDER BY score DESC
                """, {
                    "query_embedding": query_embedding,
                    "top_k": top_k
                })
            
            results = []
            for record in result:
                node = dict(record["node"])
                
                # Parse metadata if present
                if "metadata_json" in node:
                    node["metadata"] = json.loads(node["metadata_json"])
                    del node["metadata_json"]
                
                results.append({
                    "node": node,
                    "score": record["score"]
                })
            
            logger.info(f"Hybrid search found {len(results)} results")
            return results
    
    def get_document_with_context(
        self,
        doc_id: str,
        max_hops: int = 2
    ) -> Dict[str, Any]:
        """
        Get document with related documents through graph traversal
        
        Args:
            doc_id: Document ID
            max_hops: Maximum relationship hops
            
        Returns:
            Document with related context
        """
        with self.driver.session(database=self.database) as session:
            # Use SIMILAR_TO relationships for context
            result = session.run("""
                MATCH (d:Document {id: $doc_id})
                OPTIONAL MATCH (d)-[r:SIMILAR_TO]-(related:Document)
                WITH d, collect(DISTINCT {
                    id: related.id,
                    title: related.title,
                    score: COALESCE(r.score, 0.0)
                }) as related_docs
                RETURN d as document, related_docs as related
            """, {"doc_id": doc_id})
            
            record = result.single()
            
            if record:
                doc = dict(record["document"])
                if "metadata_json" in doc:
                    doc["metadata"] = json.loads(doc["metadata_json"])
                    del doc["metadata_json"]
                
                # Filter out null entries
                related = [r for r in record["related"] if r.get('id') is not None]
                
                return {
                    "document": doc,
                    "related": related
                }
            else:
                return {
                    "document": None,
                    "related": []
                }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (d:Document)
                OPTIONAL MATCH (c:Chunk)
                OPTIONAL MATCH ()-[r:SIMILAR_TO]->()
                RETURN count(DISTINCT d) as documents,
                       count(DISTINCT c) as chunks,
                       count(DISTINCT r) as similarity_relationships
            """)
            
            record = result.single()
            return dict(record)


# Example usage
if __name__ == "__main__":
    with Neo4jEmbeddingsManager() as manager:
        manager.setup_schema(vector_dimensions=1536)
        stats = manager.get_statistics()
        print(f"Database stats: {stats}")