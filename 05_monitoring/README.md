# LLM Monitoring & Observability

## Overview

In this module, I built an end-to-end monitoring pipeline for a Retrieval-Augmented Generation (RAG) application. Instead of treating each LLM request as a black box, I captured execution metrics, stored them in PostgreSQL, collected human and LLM feedback, and visualized system performance using Streamlit and Grafana.

The project demonstrates how to monitor production LLM applications by tracking latency, token usage, cost, answer quality, and user feedback over time.

---

# Architecture

```
                 User Question
                       │
                       ▼
                Streamlit Chat UI
                       │
                       ▼
               RAG Pipeline (OpenAI)
                       │
      ┌────────────────┼────────────────┐
      │                │                │
      ▼                ▼                ▼
 Capture Metrics   Judge Evaluation  User Feedback
      │                │                │
      └────────────────┼────────────────┘
                       ▼
                 PostgreSQL Database
                       │
          ┌────────────┴─────────────┐
          ▼                          ▼
   Streamlit Dashboard          Grafana Dashboard
```

---

# Technologies

- Python
- OpenAI API
- Streamlit
- PostgreSQL
- Docker & Docker Compose
- Grafana
- psycopg
- Dataclasses
- SQL

---

# What I Learned

## 1. Instrumenting LLM Calls

Instead of only returning the model response, I instrumented every LLM request by recording:

- Response time
- Prompt tokens
- Completion tokens
- Total tokens
- Model name
- Prompt
- Instructions
- Generated answer
- API cost
- Timestamp

A custom `LLMCallRecord` dataclass keeps all metrics together and makes them easy to store and analyze.

---

## 2. Cost Tracking

I implemented token-based cost calculation using the OpenAI pricing model.

For every request, I calculate:

- Prompt token cost
- Completion token cost
- Total request cost

This allows monitoring overall LLM spending over time.

---

## 3. Extending the RAG Pipeline

Rather than modifying the original RAG implementation, I created a subclass (`RAGWithMetrics`) that automatically captures metrics whenever an LLM call is made.

This keeps the original code unchanged while adding monitoring through object-oriented design.

---

## 4. Persisting Metrics in PostgreSQL

Instead of keeping metrics only in memory, every conversation is stored in PostgreSQL.

The database records:

- Question
- Answer
- Prompt
- Model
- Token usage
- Response time
- Cost
- Timestamp

Using PostgreSQL enables historical analysis and integrates naturally with Grafana.

---

## 5. Building a Streamlit Dashboard

I created a lightweight monitoring dashboard that displays:

- Total conversations
- Average response time
- Total LLM cost
- Average token usage
- Cost trend
- Latency trend
- Recent conversations

This provides immediate visibility into application performance without external monitoring tools.

---

## 6. Collecting User Feedback

I added thumbs-up and thumbs-down buttons to the chat application.

Each rating is stored in a dedicated feedback table linked to its conversation, allowing human feedback to be analyzed alongside execution metrics.

---

## 7. LLM-as-a-Judge

I implemented an automated evaluation pipeline using another LLM to judge response quality.

For every answer, the judge classifies it as:

- RELEVANT
- PARTLY_RELEVANT
- NON_RELEVANT

and provides an explanation.

These evaluations are stored in PostgreSQL together with user feedback for future analysis.

---

## 8. Monitoring with Grafana

I connected Grafana directly to PostgreSQL and built dashboards that visualize:

- Response latency
- Token usage
- LLM cost
- Model usage
- Relevance distribution
- User feedback
- Recent conversations

Grafana enables real-time operational monitoring and supports alerting for production deployments.

---

## 9. Containerizing the System

To simplify deployment, I containerized the entire monitoring stack using Docker Compose.

The environment includes:

- PostgreSQL
- Grafana
- Streamlit application

Running a single command launches the complete monitoring platform.

---

# Database Schema

## conversations

Stores execution metrics for every LLM request.

Main fields include:

- question
- answer
- model
- prompt
- token usage
- response time
- cost
- timestamp

---

## feedback

Stores both human and LLM-generated feedback.

Includes:

- conversation_id
- source (user / judge)
- relevance
- explanation
- score
- timestamp

---

# Key Monitoring Metrics

The system continuously captures:

- Response latency
- Prompt tokens
- Completion tokens
- Total tokens
- Cost per request
- Total cost
- User ratings
- Judge relevance
- Conversation history

---

# Key Takeaways

Through this project I learned how to:

- Instrument LLM applications for production monitoring
- Capture token usage, latency, and cost automatically
- Persist monitoring data using PostgreSQL
- Build operational dashboards with Streamlit
- Collect both human and AI-generated feedback
- Evaluate RAG quality using an LLM judge
- Visualize production metrics using Grafana
- Deploy the complete monitoring stack with Docker Compose

---

# Future Improvements

- Asynchronous judge evaluation
- Judge cost tracking
- Automated alerting in Grafana
- Judge sampling to reduce inference cost
- Monitoring multiple LLM models simultaneously
- Integration with Prometheus/OpenTelemetry

# Module 5 Homework: OpenTelemetry Monitoring

## Overview

In this homework, I explored **OpenTelemetry (OTel)** as a standardized observability framework for monitoring a Retrieval-Augmented Generation (RAG) application. Instead of building custom monitoring with dataclasses and PostgreSQL, I instrumented the RAG pipeline using distributed tracing, captured LLM metrics as span attributes, persisted traces to SQLite, and analyzed performance bottlenecks using SQL.

---

# Architecture

```text
                 User Query
                      │
                      ▼
              Traced RAG Pipeline
                      │
      ┌───────────────┼────────────────┐
      │               │                │
      ▼               ▼                ▼
   rag span      search span      llm span
                                      │
                     ┌────────────────┼────────────────┐
                     │                │                │
                     ▼                ▼                ▼
               Input Tokens    Output Tokens       Cost
                      │
                      ▼
             OpenTelemetry SDK
                      │
                      ▼
              Span Processor
                      │
                      ▼
            SQLite Span Exporter
                      │
                      ▼
                 traces.db
```

---

# Technologies

- OpenTelemetry (OTel)
- Python
- SQLite
- OpenAI API
- SQL

---

# What I Learned

## 1. OpenTelemetry Fundamentals

Learned the core OpenTelemetry concepts, including **traces**, **spans**, **span attributes**, and **exporters**. A trace represents an end-to-end user request, while spans capture individual operations such as document retrieval and LLM inference.

---

## 2. Instrumenting the RAG Pipeline

Extended the existing RAG implementation by creating a `RAGTraced` subclass that automatically wraps major operations (`rag`, `search`, and `llm`) inside OpenTelemetry spans. This enabled end-to-end request tracing without modifying the original business logic.

---

## 3. Capturing LLM Metrics

Recorded key LLM execution metrics as span attributes, including:

- Input tokens
- Output tokens
- API cost
- User query

These attributes provide detailed visibility into model usage and operational costs.

---

## 4. Building a Custom SQLite Exporter

Implemented a custom OpenTelemetry exporter that writes span information directly into a SQLite database. This demonstrates how OpenTelemetry traces can be persisted to any storage backend for later analysis.

---

## 5. Performance Analysis

Queried the collected traces using SQL to identify system bottlenecks. Analysis showed that document retrieval consistently completed in **under 100 ms**, while LLM inference required approximately **2–3 seconds**, making it the dominant contributor to overall response latency.

---

# Key Takeaways

- OpenTelemetry provides a standardized approach to application observability without requiring custom monitoring frameworks.
- Distributed tracing makes it easy to identify performance bottlenecks across different stages of the RAG pipeline.
- Span attributes can capture valuable operational metrics such as token usage, latency, cost, and request metadata.
- Custom exporters allow traces to be stored in databases like SQLite or forwarded to enterprise monitoring platforms.
- SQL can be used to analyze trace data and uncover latency trends, token usage patterns, and cost insights.
- LLM inference remains the largest performance bottleneck, while retrieval operations contribute minimal latency.
