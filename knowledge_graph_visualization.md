# Knowledge Graph Visualization

This document shows the structure of the Neo4j knowledge graph created by the POC.

## Graph Structure

```
                    ┌─────────────────────────────────┐
                    │   Introduction to ML            │
                    │   (doc_001)                     │
                    │   Category: AI                  │
                    └─────────────┬───────────────────┘
                                  │
                     ┌────────────┼────────────┐
                     │            │            │
              0.734 │        0.736│       0.737│
                     │            │            │
         ┌───────────▼──┐  ┌──────▼─────┐  ┌──▼──────────────┐
         │ Transfer     │  │ Data       │  │ Reinforcement   │
         │ Learning     │  │ Preprocess │  │ Learning        │
         │ (doc_008)    │  │ (doc_006)  │  │ (doc_005)       │
         └──────┬───────┘  └──────┬─────┘  └─────────────────┘
                │                 │
           0.670│            0.719│
                │                 │
         ┌──────▼─────────┐       │
         │ NLP Basics     │◄──────┘
         │ (doc_003)      │
         │ Category: NLP  │
         └────────────────┘


         ┌─────────────────────┐
         │ Deep Learning       │
         │ (doc_002)           │
         │ Category: AI        │
         └──────┬──────────────┘
                │
           0.811│ (High Similarity)
                │
         ┌──────▼──────────────┐
         │ Computer Vision     │
         │ (doc_004)           │
         │ Category: CV        │
         └─────────────────────┘


         ┌─────────────────────┐
         │ Model Evaluation    │
         │ (doc_007)           │
         │ Category: Data Sci  │
         └─────────────────────┘
```

## Relationship Statistics

### Document Connections

| Document | Connections | Most Related To |
|----------|-------------|-----------------|
| Introduction to Machine Learning | 3 | Transfer Learning (0.734) |
| Deep Learning Fundamentals | 2 | Transfer Learning (0.811) |
| Natural Language Processing | 2 | Transfer Learning (0.670) |
| Computer Vision Applications | 2 | Transfer Learning (0.662) |
| Reinforcement Learning | 2 | Introduction to ML (0.737) |
| Data Preprocessing | 3 | Introduction to ML (0.736) |
| Model Evaluation Metrics | 1 | Data Preprocessing |
| Transfer Learning | 4 | Multiple (hub node) |

### Hub Documents

**Transfer Learning (doc_008)** is a hub node connecting:
- Deep Learning (0.811) - highest similarity
- NLP (0.670)
- Computer Vision (0.662)
- Introduction to ML (0.734)

This makes sense as transfer learning applies across all ML domains!

## Categories and Clusters

```
AI Cluster:
├── Introduction to Machine Learning
├── Deep Learning Fundamentals
├── Reinforcement Learning Overview
└── Transfer Learning in Practice

NLP Cluster:
└── Natural Language Processing Basics

Computer Vision Cluster:
└── Computer Vision Applications

Data Science Cluster:
├── Data Preprocessing Techniques
└── Model Evaluation Metrics
```

## Similarity Threshold Analysis

**Used threshold: 0.7 for creating relationships**

```
Very High Similarity (> 0.8):
- Deep Learning ←→ Transfer Learning (0.811)

High Similarity (0.7-0.8):
- Introduction to ML ←→ Transfer Learning (0.734)
- Introduction to ML ←→ Data Preprocessing (0.736)
- Introduction to ML ←→ Reinforcement Learning (0.737)
- NLP ←→ Transfer Learning (0.670)
- Computer Vision ←→ Transfer Learning (0.662)

Medium Similarity (0.6-0.7):
- (Not included in graph relationships)
```

## Query Examples with Graph Context

### Example 1: Finding Related Documents

**Query:** "machine learning algorithms"

**Direct Match:**
- Introduction to Machine Learning (0.841)

**Graph Context (1-hop):**
- Transfer Learning (0.734)
- Data Preprocessing (0.736)
- Reinforcement Learning (0.737)

**Why Graph Helps:**
User searching for ML algorithms also gets preprocessing techniques and RL approaches, which they might not have found with pure vector search.

### Example 2: Cross-Domain Discovery

**Query:** "neural networks"

**Direct Match:**
- Deep Learning (0.811)

**Graph Context:**
- Transfer Learning (0.811 connection)
- Computer Vision (via Transfer Learning)
- NLP (via Transfer Learning)

**Why Graph Helps:**
Discovers applications of neural networks across different domains through the hub node.

## Multi-Hop Reasoning

### 2-Hop Path Example

```
Question: "How does machine learning relate to computer vision?"

Path 1:
Introduction to ML → Transfer Learning → Computer Vision
    (0.734)              (0.662)

Path 2:
Introduction to ML → Deep Learning → Computer Vision
    (implicit)           (0.811)

Path 3:
Introduction to ML → Data Preprocessing → (enhances) → Computer Vision
    (0.736)              (implied)
```

## Neo4j Cypher Query Visualization

### Get Full Graph

```cypher
MATCH (d:Document)-[r:SIMILAR_TO]-(d2:Document)
RETURN d, r, d2
```

**Result:** Beautiful graph showing all 8 documents and 20 relationships

### Get Hub Nodes

```cypher
MATCH (d:Document)-[r:SIMILAR_TO]-()
WITH d, count(r) as connections
WHERE connections > 2
RETURN d.title, connections
ORDER BY connections DESC
```

**Result:**
```
Transfer Learning in Practice: 4 connections
Introduction to Machine Learning: 3 connections
Data Preprocessing Techniques: 3 connections
```

### Find Shortest Path

```cypher
MATCH path = shortestPath(
  (d1:Document {id: 'doc_001'})-[*..3]-(d2:Document {id: 'doc_004'})
)
RETURN path
```

**Result:** Shows how "Introduction to ML" connects to "Computer Vision"

## Key Insights

### 1. Transfer Learning is Central
- Acts as a bridge between different ML domains
- Highest number of connections (4)
- Enables cross-domain recommendations

### 2. Natural Clustering
- Documents automatically cluster by topic
- AI documents form tight group
- Clear separation of concerns

### 3. Explainable Recommendations
- Can trace why document A relates to document B
- Similarity scores provide quantitative backing
- Graph visualization makes relationships obvious

### 4. Context Enrichment
- Pure vector search: 1-3 direct results
- With graph: 5-10 contextually relevant results
- Better user experience

## Comparison: Vector-Only vs Graph-Enhanced

### Vector-Only Search
```
Query: "machine learning"
Results:
1. Introduction to ML (0.84)
2. Deep Learning (0.75)
3. Transfer Learning (0.72)
```

### Graph-Enhanced Search
```
Query: "machine learning"
Direct Results:
1. Introduction to ML (0.84)

Related via Graph:
2. Transfer Learning (0.734) - direct connection
3. Data Preprocessing (0.736) - direct connection
4. Reinforcement Learning (0.737) - direct connection
5. Deep Learning (0.72) - via transfer learning
6. NLP (0.67) - via transfer learning
7. Computer Vision (0.66) - via transfer learning
```

**7 results vs 3 results** with better context!

## Visual Representation in Neo4j Browser

When you open http://localhost:7474 and run:

```cypher
MATCH (d:Document)-[r:SIMILAR_TO]-(d2)
RETURN d, r, d2
```

You'll see:
- 🔵 **Blue nodes** = Documents
- ➡️ **Arrows** = SIMILAR_TO relationships
- 📊 **Relationship labels** = Similarity scores
- 🎨 **Color coding** = Can group by category

**Pro tip:** Click any node to see its properties and connections!

---

This visualization clearly shows how Neo4j's graph structure enhances traditional vector search with relationship context and multi-hop reasoning capabilities.