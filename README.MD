# Production-Ready RAG Engineering Platform

A production-oriented LLM-powered Q&A chatbot that answers student questions using a knowledge base while demonstrating end-to-end Retrieval-Augmented Generation (RAG), hybrid retrieval, query rewriting, reranking, AI agent workflows, LLM-as-a-Judge, offline and online evaluation, user feedback collection (👍/👎), OpenTelemetry observability, and real-time monitoring with Streamlit and Grafana to continuously improve retrieval quality, answer accuracy, and system reliability.

---

# Architecture

```text
                                    ┌─────────────────────────────┐
                                    │        User Question        │
                                    └──────────────┬──────────────┘
                                                   │
                                                   ▼
                                    ┌─────────────────────────────┐
                                    │      Query Processing       │
                                    │ • Query Rewriting           │
                                    │ • Prompt Construction       │
                                    └──────────────┬──────────────┘
                                                   │
                                                   ▼
        ┌──────────────────────────────────────────────────────────────┐
        │                     Retrieval Layer                          │
        │                                                              │
        │ SQLite / PostgreSQL (pgvector)                               │
        │ ┌────────────────────┐    ┌──────────────────────────────┐   │
        │ │ Keyword Search     │    │ Semantic Vector Search       │   │
        │ └─────────┬──────────┘    └──────────────┬───────────────┘   │
        └───────────┼──────────────────────────────┼───────────────────┘
                    │                              │
                    └─────────────┬────────────────┘
                                  ▼
                 ┌───────────────────────────────────────┐
                 │ Retrieval Optimization                │
                 │ • Hybrid Search                       │
                 │ • Metadata Filtering & Boosting       │
                 │ • Document Reranking                  │
                 └───────────────────┬───────────────────┘
                                     │
                                     ▼
                 ┌───────────────────────────────────────┐
                 │ Context Assembly & Prompt Builder     │
                 └───────────────────┬───────────────────┘
                                     │
                                     ▼
                 ┌───────────────────────────────────────┐
                 │ OpenAI Responses API                  │
                 │ Structured Outputs / Function Calling │
                 └───────────────────┬───────────────────┘
                                     │
                                     ▼
                 ┌───────────────────────────────────────┐
                 │         Final RAG Response            │
                 └───────────────┬───────────────────────┘
                                 │
              ┌──────────────────┴───────────────────┐
              ▼                                      ▼
┌────────────────────────────────┐      ┌──────────────────────────────────────┐
│ Offline Evaluation             │      │ Online Monitoring & Evaluation       │
│ • Ground Truth Dataset         │      │ • OpenTelemetry Traces              │
│ • Hit Rate                     │      │ • Response Latency                  │
│ • Mean Reciprocal Rank (MRR)   │      │ • Token Usage & Cost                │
│ • LLM-as-a-Judge               │      │ • PostgreSQL Telemetry              │
│ • Retrieval Experiments        │      │ • Streamlit & Grafana Dashboards    │
└────────────────────────────────┘      │ • 👍 / 👎 User Feedback              │
                                        │ • Judge Feedback                     │
                                        └──────────────┬───────────────────────┘
                                                       │
                                                       ▼
                                   ┌──────────────────────────────────┐
                                   │ Continuous Improvement Loop      │
                                   │ • Prompt Refinement              │
                                   │ • Query Rewriting                │
                                   │ • Retrieval Tuning               │
                                   │ • Reranking Optimization         │
                                   │ • Evaluation Dataset Expansion   │
                                   └──────────────────────────────────┘
```

---

# Technology Stack

| Area | Technologies |
|------|--------------|
| **LLM** | OpenAI Responses API |
| **Retrieval** | SQLiteSearch, PostgreSQL (pgvector) |
| **Vector Database** | PostgreSQL + pgvector |
| **Embeddings** | ONNX Runtime |
| **Data Processing** | NumPy, Pandas |
| **RAG Pipeline** | Custom Retrieval-Augmented Generation framework |
| **Workflow Orchestration** | Kestra |
| **Retrieval Optimization** | Hybrid Search, Reciprocal Rank Fusion (RRF), Metadata Boosting, Query Rewriting, Document Reranking |
| **Evaluation** | Hit Rate, Mean Reciprocal Rank (MRR), LLM-as-a-Judge |
| **Monitoring** | OpenTelemetry, Streamlit, Grafana |
| **Storage** | PostgreSQL, SQLite |
| **Deployment** | Docker Compose |

---

# Demo Video
![](./2dashboard.mov)

# Features

## Retrieval

- Keyword Search
- Semantic Vector Search
- Hybrid Retrieval
- Reciprocal Rank Fusion (RRF)
- Metadata Filtering & Boosting
- Query Rewriting
- Document Reranking
- Optimized Chunking Strategy

## RAG Pipeline

- Modular Retrieval Pipeline
- Context Engineering
- Prompt Construction
- Structured LLM Outputs
- Function Calling
- Multi-Agent Workflows

---

# Retrieval Optimization

The retrieval layer is treated as an optimization problem rather than a fixed search component.

Implemented techniques include:

- Hybrid lexical + semantic retrieval
- Reciprocal Rank Fusion (RRF)
- Metadata score boosting
- Query rewriting
- Context engineering
- Optimized chunk sizing
- Candidate reranking

These techniques improve retrieval recall, increase answer grounding, and reduce hallucinations.

---

# Evaluation

## Offline Evaluation

The project includes a complete offline evaluation framework for benchmarking retrieval quality before deployment.

### Implemented Metrics

- Ground truth generation
- Hit Rate
- Mean Reciprocal Rank (MRR)
- Top-K Retrieval Evaluation
- Hybrid Search Experiments
- LLM-as-a-Judge Evaluation
- Token Usage & Cost Analysis

---

## Online Evaluation

Production-style evaluation captures real user interactions and operational metrics.

### Collected Signals

- Conversation Logging
- Response Latency
- Token Usage
- LLM Inference Cost
- 👍 / 👎 User Feedback
- LLM Judge Feedback
- OpenTelemetry Traces

User feedback and automated judge evaluations form a continuous feedback loop that helps improve retrieval quality, prompts, reranking strategies, and future evaluation datasets.

---

# Monitoring & Observability

The project demonstrates two complementary monitoring implementations.

## Custom Monitoring

A lightweight monitoring solution built with PostgreSQL and Streamlit.

### Capabilities

- Conversation Logging
- Response Latency
- Token Usage
- Cost Tracking
- User Feedback
- LLM Judge Evaluation

---

## OpenTelemetry Monitoring

A second implementation instruments the RAG pipeline using distributed tracing.

```text
User Query
      │
      ▼
RAG Pipeline
      │
 ├── search span
 ├── llm span
 │      ├── input_tokens
 │      ├── output_tokens
 │      ├── cost
 │      └── latency
      │
      ▼
SQLite Exporter
      │
      ▼
Trace Database
```

### Captured Span Attributes

- Input Tokens
- Output Tokens
- Response Latency
- API Cost
- User Query
- Model Metadata

---

# Dashboards

The monitoring dashboards provide operational visibility into:

- Response Latency
- Token Consumption
- API Cost
- Model Usage
- Retrieval Quality
- Judge Relevance
- User Feedback
- Recent Conversations

### Built Using

- Streamlit
- PostgreSQL
- Grafana
- OpenTelemetry

---

# Key Engineering Concepts

This repository demonstrates production-grade engineering patterns commonly used in enterprise LLM applications.

- Retrieval-Augmented Generation (RAG)
- Hybrid Search
- Semantic Vector Search
- Reciprocal Rank Fusion (RRF)
- Context Engineering
- Function Calling
- Multi-Agent Workflows
- LLM Evaluation
- OpenTelemetry
- Distributed Tracing
- Production Monitoring
- Cost Optimization
- Continuous Improvement Feedback Loop

