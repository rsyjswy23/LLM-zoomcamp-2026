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

