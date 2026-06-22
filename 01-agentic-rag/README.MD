# Chapter 1 Reflection: Agentic RAG

## Overview

In Chapter 1, I learned how to build a complete Retrieval-Augmented Generation (RAG) system, from data ingestion and indexing to implementing Agentic RAG with tool calling capabilities. This chapter helped me understand not only the core architecture of RAG systems but also the importance of data schema design, modular code organization, and debugging real-world issues.

---

## What I Learned

### 1. Core RAG Architecture

Retrieval-Augmented Generation (RAG) combines information retrieval with Large Language Models (LLMs) to generate accurate and context-aware responses.

A typical RAG workflow consists of four steps:

```text
Search → Build Prompt → Call LLM → Return Answer
```

The main components include:

* **Search Index** – Retrieves relevant documents.
* **LLM Client** – Generates responses using retrieved context.
* **Orchestration Logic** – Coordinates retrieval and generation.

---

### 2. Building a Modular RAG System

I organized the application into two primary modules.

#### `ingest.py`

Responsible for loading data and building the search index.

Key functions:

* `load_faq_data()`
* `build_index()`

Responsibilities:

* Fetch FAQ data
* Process documents
* Build searchable indexes

#### `rag_helper.py`

Encapsulates the RAG pipeline within a reusable `RAGBase` class.

Core methods include:

* Document retrieval
* Context construction
* Prompt generation
* LLM interaction

This design follows several software engineering best practices:

* Dependency Injection
* Separation of Concerns
* Reusable and extensible components

This architecture allows different search engines and LLM providers to be swapped with minimal code changes.

---

### 3. Search Technologies

#### Minsearch

* Lightweight in-memory search engine
* Fast and simple to prototype
* Data is lost after restarting the application

#### SQLiteSearch

* Persistent search backend
* Stores indexes in SQLite
* Supports Full-Text Search (FTS5)
* Prevents duplicate records when re-running ingestion
* Enables data persistence across sessions

---

### 4. Agentic RAG

One of the most interesting concepts introduced in this chapter was **Agentic RAG**.

Instead of always retrieving documents before answering, the LLM is given access to tools and decides:

* When to search
* What information to retrieve
* Whether multiple searches are needed
* When sufficient context has been collected to answer the question

Agentic RAG provides:

* Improved accuracy
* Better handling of complex questions
* More flexible reasoning capabilities

Trade-offs include:

* Increased API usage
* Additional latency
* Higher token consumption

---

### 5. Libraries and Tools

Libraries explored in this chapter include:

#### ToyAIKit

A lightweight framework for building AI agents with tool-calling capabilities.

Features:

* Agent execution loop
* Tool registration
* Function calling support

#### Gitsource

Utility for downloading and processing files directly from GitHub repositories.

---

## Homework Reflections

Through this homework, I learned the complete RAG pipeline from data ingestion to agentic systems. The most valuable lesson was understanding the importance of data schema - I initially loaded FAQ data instead of lesson pages, which caused KeyError issues because the field names (section/question/answer) didn't match what my RAG helper expected (filename/content). I also discovered that chunking documents reduces token usage by approximately 3x, making the system more efficient while maintaining answer quality. The transition from plain RAG to agentic RAG showed me how giving the model search tools and letting it decide when to search creates more flexible and accurate responses, though at the cost of more API calls. Finally, I learned to properly count input tokens by modifying the RAG helper to return the full response object with usage information, and to count function calls by inspecting the agent's message history for function_call types.

Key Debugging Moments
Data Source Mismatch: Used GithubRepositoryDataReader instead of the FAQ API, and handled flexible field names with doc.get('filename') or doc.get('name') fallbacks

Token Counting: Modified llm() to return the full response object instead of just text, extracting usage from response.usage.input_tokens

Agent Function Call Counting: Counted search calls by iterating through result.all_messages and checking message.type == 'function_call'

Schema Adaptation: Created separate hw_rag_helper.py with content as the only text field instead of the FAQ's question/section/answer structure

Chunking Benefits: Realized that chunking with size=2000, step=1000 produces 295 chunks and reduces input tokens from 7,126 to 2,309 (3.1x reduction)

I also learned how to monitor LLM usage more effectively by:

* Returning the complete response object
* Extracting token usage information
* Tracking function calls within the agent loop

---

## Key Takeaways

* Understand the complete RAG architecture and workflow.
* Build modular and reusable RAG components.
* Compare in-memory and persistent search technologies.
* Implement Agentic RAG using tool/function calling.
* Appreciate the importance of schema consistency.
* Reduce token costs through document chunking.
* Measure token usage and agent behavior for evaluation and monitoring.

---

### Skills Gained

* Retrieval-Augmented Generation (RAG)
* Agentic RAG
* Tool/Function Calling
* SQLite FTS5
* Search Indexing
* Dependency Injection
* Prompt Engineering
* Document Chunking
* Token Monitoring
* Debugging Data Schema Issues
* Building Modular AI Applications
