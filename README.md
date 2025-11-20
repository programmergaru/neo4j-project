# Neo4j Embeddings POC - Graph-Based RAG System

A proof-of-concept demonstrating how to store and query embeddings in Neo4j for building knowledge graphs with semantic search capabilities. This project showcases graph-based Retrieval-Augmented Generation (RAG) architecture with vector similarity search and relationship traversal.

## 🎯 Project Overview

This POC demonstrates:
- **Vector embeddings storage** in Neo4j graph database
- **Semantic similarity search** using Neo4j vector indexes
- **Graph-based context retrieval** through relationship traversal
- **Hybrid search** combining vector similarity and keyword matching
- **Knowledge graph visualization** of document relationships
- **Automatic similarity relationship creation** between related documents

## 🏗️ Architecture

```
Documents → OpenAI Embeddings → Neo4j Graph Database
                ↓                       ↓
         Vector Index          Similarity Relationships
                ↓                       ↓
         Semantic Search  ←→  Graph Traversal
                ↓
          RAG Context
```

## ✨ Features

- ✅ **Vector Similarity Search** - Find semantically similar documents using cosine similarity
- ✅ **Graph Relationships** - Automatic `SIMILAR_TO` relationships between documents
- ✅ **Hybrid Search** - Combine vector similarity with keyword matching
- ✅ **Context Enrichment** - Retrieve related documents through graph traversal
- ✅ **Knowledge Graph** - Visualize document connections in Neo4j Browser
- ✅ **Multiple Embedding Providers** - Support for OpenAI and local models (Sentence Transformers)

## 📺 Demo Output

Here's what you'll see when running the POC:

```
================================================================================
Neo4j Embeddings POC - Demo
================================================================================

🔍 Query: 'neural networks and deep learning'
--------------------------------------------------------------------------------
1. Deep Learning Fundamentals
   Similarity: 0.811
   Category: AI
   Preview: Deep learning uses artificial neural networks with multiple layers...

2. Introduction to Machine Learning
   Similarity: 0.720
   Category: AI

3. Transfer Learning in Practice
   Similarity: 0.709
   Category: AI

🔍 Query: 'language models and text processing'
--------------------------------------------------------------------------------
1. Natural Language Processing Basics
   Similarity: 0.741
   Category: NLP

2. Transfer Learning in Practice
   Similarity: 0.670
   Category: AI

🔍 Query: 'machine learning algorithms' (with Graph Context)
--------------------------------------------------------------------------------
1. Introduction to Machine Learning (Score: 0.841)
   Related documents:
   - Transfer Learning in Practice (Relevance: 0.734)
   - Data Preprocessing Techniques (Relevance: 0.736)
   - Reinforcement Learning Overview (Relevance: 0.737)

🔍 Hybrid Search: 'artificial intelligence' + keywords: ['neural', 'learning']
--------------------------------------------------------------------------------
1. Introduction to Machine Learning
   Combined Score: 0.722
   Category: AI

2. Deep Learning Fundamentals
   Combined Score: 0.652
   Category: AI

Database Statistics:
- Documents: 8
- Similarity Relationships: 20
- Chunks: 0
```

The demo showcases:
- ✅ **Vector similarity search** - Finding semantically similar documents
- ✅ **Graph context retrieval** - Related documents through SIMILAR_TO relationships
- ✅ **Hybrid search** - Combining vector similarity with keyword matching
- ✅ **Knowledge graph statistics** - 8 documents with 20 relationship connections

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker (for Neo4j)
- OpenAI API key (or use local embeddings)

### 1. Clone Repository

```bash
git clone <repository-url>
cd neo4j-embeddings-poc
```

### 2. Install Dependencies

```bash
# Create virtual environment
conda create -p ./.venv python=3.12
conda activate ./.venv

# Install packages
pip install -r requirements.txt
```

### 3. Start Neo4j

```bash
# Using Docker
docker run \
    --name neo4j-embeddings \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password123 \
    -e NEO4J_PLUGINS='["graph-data-science"]' \
    -v $(pwd)/neo4j-data:/data \
    -d neo4j:latest

# Verify it's running
docker ps | grep neo4j
```

### 4. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env with your credentials
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=password123
# OPENAI_API_KEY=sk-your-api-key-here
```

### 5. Run Demo

```bash
# Run the complete POC demo
python src/demo_poc.py
```

### 6. Visualize in Neo4j Browser

Open http://localhost:7474 in your browser and run:

```cypher
MATCH (d:Document)-[r:SIMILAR_TO]-(d2:Document)
RETURN d, r, d2
```

## 📁 Project Structure

```
neo4j-embeddings-poc/
├── .env                    # Environment variables (create from .env.example)
├── .gitignore             # Git ignore file
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── config/
│   └── config.yaml       # Application configuration
├── data/
│   ├── sample_docs.json  # Sample documents for POC
│   └── results/          # Query results (gitignored)
├── src/
│   ├── __init__.py
│   ├── embeddings.py     # Embedding generation (OpenAI/local)
│   ├── neo4j_manager.py  # Neo4j database operations
│   ├── search.py         # Search functionality
│   └── demo_poc.py       # Main demo script
├── notebooks/
│   └── exploration.ipynb # Jupyter notebook for exploration
└── tests/
    └── test_neo4j.py     # Unit tests
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Alternative: Use local embeddings
USE_LOCAL_EMBEDDINGS=false
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Application Configuration (config/config.yaml)

```yaml
embeddings:
  provider: openai  # Options: openai, sentence-transformers
  model: text-embedding-3-small
  dimensions: 1536

search:
  top_k: 5
  similarity_threshold: 0.7

graph:
  document_label: Document
  similarity_threshold: 0.7
  max_connections: 5
```

## 💻 Usage Examples

### Basic Vector Search

```python
from src.embeddings import EmbeddingGenerator
from src.neo4j_manager import Neo4jEmbeddingsManager
from src.search import EmbeddingSearch

# Initialize
embeddings = EmbeddingGenerator(provider="openai")
neo4j = Neo4jEmbeddingsManager()

# Create search interface
search = EmbeddingSearch(embeddings, neo4j)

# Search for similar documents
results = search.search("machine learning algorithms", top_k=5)

for result in results:
    print(f"{result['node']['title']} - Score: {result['score']:.3f}")
```

### Hybrid Search (Vector + Keywords)

```python
results = search.hybrid_search(
    query="artificial intelligence",
    keywords=["neural", "learning", "models"],
    top_k=5
)
```

### Graph Context Retrieval

```python
results = search.search(
    query="deep learning", 
    top_k=3, 
    include_context=True
)

for result in results:
    print(f"\nDocument: {result['node']['title']}")
    print(f"Related documents: {len(result.get('related', []))}")
    for related in result.get('related', [])[:3]:
        print(f"  - {related['title']} (score: {related['score']:.3f})")
```

### Create Document with Embedding

```python
from src.embeddings import EmbeddingGenerator
from src.neo4j_manager import Neo4jEmbeddingsManager

embeddings = EmbeddingGenerator(provider="openai")
neo4j = Neo4jEmbeddingsManager()

# Generate embedding
text = "Your document content here"
embedding = embeddings.generate_embedding(text)

# Create document in Neo4j
neo4j.create_document(
    doc_id="doc_123",
    title="My Document",
    content=text,
    embedding=embedding,
    metadata={
        "category": "AI",
        "author": "Your Name",
        "date": "2025-01-15"
    }
)

# Create similarity relationships
neo4j.create_similarity_relationships(
    node_label="Document",
    similarity_threshold=0.7,
    max_connections=5
)
```

## 🔍 Neo4j Browser Queries

### View All Documents
```cypher
MATCH (d:Document)
RETURN d
LIMIT 25
```

### Visualize Knowledge Graph
```cypher
MATCH (d:Document)-[r:SIMILAR_TO]-(d2:Document)
RETURN d, r, d2
```

### Find Similar Documents
```cypher
MATCH (d:Document {id: 'doc_001'})-[r:SIMILAR_TO]-(similar:Document)
RETURN d.title as original,
       similar.title as similar_document,
       r.score as similarity_score
ORDER BY r.score DESC
```

### Most Connected Documents
```cypher
MATCH (d:Document)-[r:SIMILAR_TO]-()
RETURN d.title, count(r) as connections
ORDER BY connections DESC
LIMIT 10
```

See [NEO4J_QUERIES.md](docs/NEO4J_QUERIES.md) for more query examples.

## 📊 Performance & Scalability

### Vector Index Performance
- **Search speed:** ~50-100ms for top-5 similarity search
- **Index build:** ~1-2 seconds per 1000 documents
- **Memory:** ~1KB per 1536-dimension embedding

### Recommendations
- **Small datasets** (< 10K docs): Single Neo4j instance works well
- **Medium datasets** (10K-100K docs): Consider Neo4j clustering
- **Large datasets** (> 100K docs): Hybrid approach with specialized vector DB

## 🆚 Neo4j vs PostgreSQL pgvector

| Feature | Neo4j | PostgreSQL pgvector |
|---------|-------|---------------------|
| Vector Search Speed | Fast | Very Fast |
| Graph Relationships | Native & Excellent | Complex JOINs |
| Explainability | Excellent | Limited |
| Multi-hop Queries | Easy | Difficult |
| Setup Complexity | Medium | Low |
| Scalability | Good | Excellent |
| **Best For** | Knowledge Graphs, Complex Relationships | Simple Vector Search, High Throughput |

**Use Neo4j when:**
- Document relationships and context matter
- You need explainability (why documents are related)
- Building knowledge graphs
- Multi-hop reasoning required

**Use PostgreSQL pgvector when:**
- Simple vector search is sufficient
- High throughput is critical
- Existing PostgreSQL infrastructure
- Lower operational complexity desired

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_neo4j.py::test_vector_search -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📦 Dependencies

### Core Dependencies
- `neo4j` - Neo4j Python driver
- `openai` - OpenAI API client
- `sentence-transformers` - Local embedding models
- `python-dotenv` - Environment variable management
- `pandas` - Data manipulation
- `numpy` - Numerical operations

### Development Dependencies
- `pytest` - Testing framework
- `jupyter` - Notebook environment
- `black` - Code formatting
- `flake8` - Linting

See [requirements.txt](requirements.txt) for complete list.

## 🚧 Troubleshooting

### Neo4j Connection Issues

```bash
# Check if Neo4j is running
docker ps | grep neo4j

# View Neo4j logs
docker logs neo4j-embeddings

# Restart Neo4j
docker restart neo4j-embeddings
```

### Import Errors

```python
# If you get "ModuleNotFoundError: No module named 'src'"
# Make sure you have __init__.py in src/ directory
# Run from project root directory
```

### Memory Issues

```bash
# Increase Neo4j memory (edit docker command)
-e NEO4J_dbms_memory_heap_max__size=4G
-e NEO4J_dbms_memory_pagecache_size=2G
```

### OpenAI API Rate Limits

```python
# Adjust rate limiting in parameters
openai_processing:
  max_requests_per_minute: 20  # Reduce from default
  retry_delay_seconds: 5       # Increase delay
```

## 🗺️ Roadmap

- [ ] Add support for document chunking
- [ ] Implement incremental updates
- [ ] Add multi-modal embeddings (images, audio)
- [ ] Create REST API wrapper
- [ ] Add authentication and authorization
- [ ] Implement caching layer
- [ ] Add monitoring and metrics
- [ ] Create web UI for visualization
- [ ] Support for multiple languages
- [ ] Integration with LangChain

## 📚 Documentation

- [Neo4j Queries Guide](docs/NEO4J_QUERIES.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Neo4j](https://neo4j.com/) - Graph database platform
- [OpenAI](https://openai.com/) - Embedding models
- [Sentence Transformers](https://www.sbert.net/) - Local embedding models
- Inspired by graph-based RAG architectures

## 📧 Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/neo4j-embeddings-poc](https://github.com/yourusername/neo4j-embeddings-poc)

## 🎓 Use Cases

This POC is designed for:
- **Knowledge Management Systems** - Organize and retrieve related documents
- **Research Paper Analysis** - Find related research and citations
- **Content Recommendation** - Suggest related articles or documents
- **Question Answering Systems** - Retrieve relevant context for RAG
- **Document Classification** - Cluster similar documents automatically
- **Semantic Search Applications** - Go beyond keyword matching

## 💡 Key Learnings

This POC demonstrates:
1. **Graph databases** can enhance vector search with relationship context
2. **Hybrid approaches** (vector + graph) provide better retrieval than either alone
3. **Explainability** through relationships helps understand why documents are related
4. **Multi-hop reasoning** enables discovering indirect connections
5. **Visualization** of knowledge graphs aids in understanding document relationships

---

**Built with ❤️ as a proof-of-concept for graph-based RAG systems**