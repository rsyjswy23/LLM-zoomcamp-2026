# 🚀 Vector Search — Complete Learning Summary

## 📚 Module Overview

In this module, I learned the fundamentals of **Vector Search**, from the underlying concepts to production-ready implementations. The module covered how to generate embeddings, perform semantic search, compare multiple vector databases, and integrate vector search into a Retrieval-Augmented Generation (RAG) system.

---

# 📖 Table of Contents

* Introduction to Vector Search
* Understanding Embeddings
* Embedding the Dataset
* Building Vector Search from Scratch
* Vector Search with Minsearch
* RAG with Vector Search
* SQLiteSearch
* PGVector
* ONNX Runtime vs PyTorch
* Key Takeaways

---

# 1. Introduction to Vector Search

## What I Learned

* Difference between traditional keyword search and semantic vector search
* How vector search captures semantic meaning instead of exact keywords
* Common applications:

  * Retrieval-Augmented Generation (RAG)
  * Recommendation Systems
  * Semantic Search
  * Question Answering

---

# 2. Understanding Embeddings

## What I Learned

* How transformer models convert text into dense vector representations
* The **all-MiniLM-L6-v2** embedding model (384 dimensions)
* Difference between semantic similarity and lexical matching
* How embeddings preserve context and meaning

> **Key Concept**
>
> Embeddings convert text into dense numerical vectors where semantically similar documents are located close together in vector space.

---

# 3. Embedding the Dataset

## What I Learned

* Loading FAQ data from the ingestion pipeline
* Combining **question + answer** to create richer embeddings
* Batch processing for improved efficiency
* Using **tqdm** for progress tracking
* Converting embeddings into NumPy arrays

### Example

```python
texts = [
    doc["question"] + " " + doc["answer"]
    for doc in documents
]

for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    batch_vectors = model.encode(batch)
    vectors.extend(batch_vectors)
```

---

# 4. Building Vector Search from Scratch

## What I Learned

* Computing dot products manually
* Cosine similarity vs Euclidean distance
* Matrix multiplication with NumPy
* Ranking documents by similarity
* Retrieving Top-K documents using `argsort`

### Example

```python
scores = X.dot(v_query)

top5 = np.argsort(-scores)[:5]
```

---

# 5. Vector Search with Minsearch

## What I Learned

* Wrapping vector search inside a reusable library
* Filtering by metadata (course/category)
* Consistent API for text and vector search
* In-memory indexing for experimentation

### Example

```python
from minsearch import VectorSearch

vindex = VectorSearch(
    keyword_fields=["course"]
)

vindex.fit(X, documents)

results = vindex.search(
    query_vector,
    filter_dict={"course": "llm-zoomcamp"}
)
```

---

# 6. RAG with Vector Search

## What I Learned

* Modular RAG architecture
* Replacing only the search layer while keeping the rest unchanged
* Using subclassing to support different retrieval methods
* Dependency injection for flexible design

> **Key Insight**
>
> RAG is modular. The retrieval layer can be replaced without modifying prompt engineering or LLM generation.

---

# 7. SQLiteSearch

## What I Learned

* Persistent vector storage using SQLite
* Approximate Nearest Neighbor (ANN) search
* Three ANN algorithms:

  * LSH
  * IVF
  * HNSW
* Two-stage retrieval:

  1. Candidate retrieval
  2. Exact reranking
* Reopening indexes without regenerating embeddings

> **Key Insight**
>
> Exact Nearest Neighbor compares against every document, while ANN narrows the search space first for much faster retrieval.

---

# 8. PGVector

## What I Learned

* PostgreSQL with the **pgvector** extension
* Storing embeddings directly inside relational databases
* Using cosine distance (`<=>`)
* Creating HNSW indexes
* Transaction support and concurrent access
* Production-ready vector search

### Example

```sql
CREATE TABLE documents (
    embedding vector(384)
);

SELECT *
FROM documents
ORDER BY embedding <=> query_vector
LIMIT 5;
```

---

# 9. ONNX Runtime vs PyTorch

## What I Learned

* ONNX Runtime provides much lighter deployments
* Generates identical embeddings with significantly fewer dependencies
* Ideal for production inference

| Feature           | ONNX Runtime |                PyTorch |
| ----------------- | -----------: | ---------------------: |
| Package Size      |       147 MB |                 4.8 GB |
| Packages          |           27 |                     58 |
| Embedding Quality |         Same |                   Same |
| Best For          |   Production | Development & Training |

> **Key Insight**
>
> ONNX Runtime produces the same embeddings while being dramatically smaller and faster to deploy.

---

# 🔑 Key Takeaways

## Search Methods

| Method         | Strength               | Weakness            | Best Use Case             |
| -------------- | ---------------------- | ------------------- | ------------------------- |
| Keyword Search | Fast, exact matching   | Misses synonyms     | IDs, names, codes         |
| Vector Search  | Semantic understanding | Higher compute cost | Question answering        |
| Hybrid Search  | High accuracy          | More complex        | Production search systems |

---

## Vector Search Implementations

| Tool         | Persistence | Search Type | Best For               |
| ------------ | ----------- | ----------- | ---------------------- |
| Minsearch    | In Memory   | Exact NN    | Learning & experiments |
| SQLiteSearch | SQLite      | ANN         | Personal projects      |
| PGVector     | PostgreSQL  | ANN + Index | Production systems     |

---

## Reciprocal Rank Fusion (RRF)

RRF combines rankings from multiple retrieval methods without relying on raw similarity scores.

**Formula**

```text
RRF(d) = Σ 1 / (k + rank(d))
```

Where:

* `k = 60` (default constant)
* Rewards documents that rank highly across multiple search methods
* Combines rankings instead of similarity scores
* Commonly used for Hybrid Search (Keyword + Vector Search)
