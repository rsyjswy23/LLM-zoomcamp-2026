# Module 04: Evaluation of Search, RAG, and Agents

This module covers offline evaluation for three components of an LLM pipeline: **search retrieval**, **RAG answer quality**, and **agent behavior**. Each evaluation builds on the previous one, moving from retrieval to generation to autonomous tool use.

---

## Overview

```
Ground Truth Generation
        │
        ▼
1. Search Evaluation   ──► Hit Rate + MRR
        │
        ▼
2. RAG Evaluation      ──► LLM-as-a-Judge (A→Q→A')
        │
        ▼
3. Agent Evaluation    ──► Answer Score + Trajectory Score
```

---

## Setup

```bash
uv add tqdm pandas
```

Set your OpenAI API key in a `.env` file:

```
OPENAI_API_KEY=your-key-here
```

---

## Step 1: Generate Ground Truth

Before evaluating anything, we need a ground truth dataset — questions with known correct documents.

For each FAQ document, we use an LLM to generate synthetic questions, then record which document each question came from.

```python
import json
from tqdm.auto import tqdm
from concurrent.futures import ThreadPoolExecutor
from evaluation_utils import llm_structured_retry, map_progress, calc_total_price

def generate_ground_truth(doc):
    user_prompt = json.dumps(doc)
    out, usage = llm_structured_retry(
        openai_client,
        data_gen_instructions,
        user_prompt,
        Questions
    )
    results = []
    for q in out.questions:
        results.append({
            "question": q,
            "document": doc["id"]
        })
    return results, usage

# Run in parallel (6 workers avoids rate limits)
with ThreadPoolExecutor(max_workers=6) as pool:
    results = map_progress(pool, documents, generate_ground_truth)

ground_truth = []
usages = []
for records, usage in results:
    ground_truth.extend(records)
    usages.append(usage)

# Save
import pandas as pd
df_ground_truth = pd.DataFrame(ground_truth)
df_ground_truth.to_csv("data/ground_truth-new.csv", index=False)
```

> **Cost reference:** 79 documents → 395 questions → ~$0.057

Or download the pre-generated file:
```bash
PREFIX=https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main
wget -O data/ground_truth-new.csv ${PREFIX}/04-evaluation/data/ground_truth-new.csv
```

---

## Evaluation 1: Search

### Goal
Check whether the correct document appears in the top-k search results for each ground truth question.

### Metrics

**Hit Rate (Recall@k)** — fraction of queries where the correct document appears anywhere in results:

```python
def hit_rate(relevance):
    cnt = 0
    for line in relevance:
        if 1 in line:
            cnt += 1
    return cnt / len(relevance)
```

**Mean Reciprocal Rank (MRR)** — rewards systems that rank the correct document higher. Position 1 scores 1.0, position 2 scores 0.5, position 3 scores 0.333:

```python
def mrr(relevance):
    total_score = 0.0
    for line in relevance:
        for rank in range(len(line)):
            if line[rank] == 1:
                total_score += 1 / (rank + 1)
                break
    return total_score / len(relevance)
```

### Running Search Evaluation

```python
def text_search(query):
    boost_dict = {"question": 1.0, "answer": 2.0, "section": 0.1}
    return index.search(query, num_results=5, boost_dict=boost_dict)

def compute_relevance(q, search_function):
    doc_id = q["document"]
    results = search_function(query=q["question"])
    return [int(d["id"] == doc_id) for d in results]

def compute_relevance_total(ground_truth, search_function):
    relevance_total = []
    for q in tqdm(ground_truth):
        relevance_total.append(compute_relevance(q, search_function))
    return relevance_total

def evaluate(ground_truth, search_function):
    relevance_total = compute_relevance_total(ground_truth, search_function)
    return {
        "hit_rate": hit_rate(relevance_total),
        "mrr": mrr(relevance_total),
    }

evaluate(ground_truth, text_search)
# {"hit_rate": 0.899, "mrr": 0.769}
```

### Parameter Tuning

Use grid search to find the best field boost combination instead of guessing:

```python
results = []
for question_boost in [1.0, 2.0, 5.0]:
    for answer_boost in [1.0, 2.0, 4.0, 10.0]:
        for section_boost in [0.1, 0.2, 0.5]:
            result = evaluate(
                ground_truth,
                lambda query, qb=question_boost, ab=answer_boost, sb=section_boost:
                    index.search(query, num_results=5,
                                 boost_dict={"question": qb, "answer": ab, "section": sb})
            )
            results.append({"question": question_boost, "answer": answer_boost,
                            "section": section_boost, **result})

df_results = pd.DataFrame(results)
df_results.sort_values("mrr", ascending=False).head(5)
```

**Key finding:** The data showed `answer` should be weighted **twice as heavily as question**, with almost no weight on section — the opposite of intuition. This is exactly why we measure instead of guess.

| question | answer | section | hit_rate | mrr   |
|----------|--------|---------|----------|-------|
| 1.0      | 2.0    | 0.1     | 0.975    | 0.885 |
| 2.0      | 4.0    | 0.2     | 0.975    | 0.885 |

### Interpreting Metrics
- **Hit Rate** = did the correct document appear at all in top-k?
- **MRR** = how high was the correct document ranked?
- High Hit Rate + Low MRR → correct doc is found but buried under noise
- Synthetic questions can inflate metrics; treat numbers above 95% with caution

---

## Evaluation 2: RAG (LLM-as-a-Judge)

### Goal
Evaluate whether the full RAG pipeline produces answers that match the original FAQ answers. This uses the **A→Q→A' setup**:

```
A  = original FAQ answer
Q  = question generated from A  (ground truth)
A' = answer produced by RAG system

If A' ≈ A, the RAG pipeline is working correctly
```

### Generate RAG Answers

```python
from evaluation_utils import RAGWithUsage

assistant = RAGWithUsage(index=index, llm_client=openai_client)

def generate_rag_answer(rec):
    question = rec["question"]
    doc_id = rec["document"]
    answer_llm = assistant.rag(question)
    answer_orig = doc_idx[doc_id]["answer"]
    return {
        "question": question,
        "answer_llm": answer_llm,
        "answer_orig": answer_orig,
        "document": doc_id,
    }

with ThreadPoolExecutor(max_workers=6) as pool:
    results = map_progress(pool, ground_truth, generate_rag_answer)

df_answers = pd.DataFrame(results)
df_answers.to_csv("data/rag-answers-new.csv", index=False)
```

> **Cost reference:** 395 questions → ~$0.34

### Judge RAG Answers

An LLM judge compares the RAG answer to the original FAQ answer and scores it `good` or `bad`:

```python
from pydantic import BaseModel, Field
from typing import Literal

class AnswerEvaluation(BaseModel):
    reasoning: str = Field(description="Reasoning about the quality of the answer.")
    score: Literal["good", "bad"] = Field(
        description="'good' if the answer is correct and complete, 'bad' otherwise."
    )

aqa_judge_instructions = """
You are an expert evaluator. You will be given:
1. A question from a student
2. The original answer from the FAQ (ground truth)
3. An answer generated by an AI assistant

Your task is to decide if the AI answer is semantically equivalent to the original answer.

Rules:
- The AI answer does NOT need to be word-for-word identical
- It should convey the same key information
- Extra detail is fine as long as the core answer is correct
- Mark 'bad' only if the AI answer is wrong or misses the key point
""".strip()

aqa_judge_prompt = """
Question: {question}
Original Answer (ground truth): {answer_orig}
AI Answer: {answer_llm}
""".strip()

def evaluate_aqa(question, answer_orig, answer_llm):
    prompt = aqa_judge_prompt.format(
        question=question, answer_orig=answer_orig, answer_llm=answer_llm
    )
    result, usage = llm_structured_retry(
        openai_client, aqa_judge_instructions, prompt, AnswerEvaluation
    )
    return result, usage

def judge_record(rec):
    eval_result, usage = evaluate_aqa(
        question=rec["question"],
        answer_orig=rec["answer_orig"],
        answer_llm=rec["answer_llm"]
    )
    return {
        "question": rec["question"],
        "document": rec["document"],
        "score": eval_result.score,
        "reasoning": eval_result.reasoning,
    }, usage

with ThreadPoolExecutor(max_workers=6) as pool:
    results = map_progress(pool, answers, judge_record)

evaluations, usages = zip(*results)
df_eval = pd.DataFrame(evaluations)

# Results summary
good = (df_eval["score"] == "good").sum()
total = len(df_eval)
print(f"Good: {good}/{total} = {good/total:.2%}")
# Good: 379/395 = 95.95%

# Investigate bad cases
df_eval[df_eval["score"] == "bad"].head()
```

> **Cost reference:** 395 answers judged → ~$0.25

**What bad cases reveal:**
- Search retrieved the wrong document
- Answer is too generic or misses the key point
- RAG pipeline said "I don't know" even though the FAQ had the answer

> **Important:** Always sample and manually review judge verdicts. The judge can be wrong. If it's too lenient, tighten the instructions.

---

## Evaluation 3: Agent (Answer + Trajectory)

### Goal
Evaluate both the **final answer** and the **tool call behavior** (trajectory) of an agent. The same A→Q→A' setup applies, but A' comes from an agent instead of a fixed RAG pipeline.

### Run the Agent

```python
from toyaikit.tools import Tools
from toyaikit.chat.runners import OpenAIResponsesRunner
from toyaikit.llm import OpenAIClient

def search(query: str) -> list[dict]:
    """Search the FAQ database for entries matching the given query."""
    return index.search(
        query,
        num_results=5,
        boost_dict={"question": 1.0, "answer": 2.0, "section": 0.1},
        filter_dict={"course": "llm-zoomcamp"}
    )

agent_tools = Tools()
agent_tools.add_tool(search)

runner = OpenAIResponsesRunner(
    tools=agent_tools,
    developer_prompt="You're a course teaching assistant. Use the search tool before answering.",
    llm_client=OpenAIClient(model="gpt-5.4-mini")
)

def extract_tool_calls(messages):
    tool_calls = []
    for message in messages:
        if isinstance(message, dict):
            continue
        if message.type == "function_call":
            tool_calls.append({"name": message.name, "arguments": message.arguments})
    return tool_calls

def generate_agent_answer(rec):
    doc_id = rec["document"]
    result = runner.loop(prompt=rec["question"])
    tool_calls = extract_tool_calls(result.all_messages)
    return {
        "question": rec["question"],
        "answer_agent": result.last_message,
        "answer_orig": doc_idx[doc_id]["answer"],
        "tool_calls": tool_calls,
        "cost": result.cost.total_cost,
        "document": doc_id,
    }

with ThreadPoolExecutor(max_workers=6) as pool:
    agent_answers = map_progress(pool, ground_truth[:50], generate_agent_answer)

df_agent = pd.DataFrame(agent_answers)
df_agent.to_csv("data/agent-answers.csv", index=False)
```

> **Cost reference:** 50 questions → ~$0.07

### Judge Agent Answers AND Trajectories

The agent judge scores two things independently:

```python
class AgentEvaluation(BaseModel):
    answer_reasoning: str = Field(description="Reasoning about whether the final answer is correct.")
    answer_score: Literal["good", "bad"] = Field(
        description="'good' if the final answer matches the original answer."
    )
    trajectory_reasoning: str = Field(description="Reasoning about whether the tool calls were useful.")
    trajectory_score: Literal["good", "bad"] = Field(
        description="'good' if the tool calls were reasonable for the question."
    )

agent_judge_instructions = """
You are an expert evaluator. Evaluate two things:

Answer quality:
- Does the agent answer match the original answer?
- It does not need to be word-for-word identical.

Trajectory quality:
- Were the search queries relevant to the question?
- Did the agent avoid duplicate or unnecessary tool calls?
- Was the number of calls reasonable? Usually 1 is enough, 2-3 can be okay.
- Did the tool calls support the final answer?
""".strip()

agent_judge_prompt = """
Question: {question}
Original Answer (ground truth): {answer_orig}
Agent Answer: {answer_agent}
Tool Calls: {tool_calls}
""".strip()

def evaluate_agent_answer(rec):
    tool_calls = rec["tool_calls"]
    if isinstance(tool_calls, str):
        tool_calls = json.loads(tool_calls)
    prompt = agent_judge_prompt.format(
        question=rec["question"],
        answer_orig=rec["answer_orig"],
        answer_agent=rec["answer_agent"],
        tool_calls=json.dumps(tool_calls, indent=2),
    )
    result, usage = llm_structured_retry(
        openai_client, agent_judge_instructions, prompt, AgentEvaluation
    )
    return result, usage

def judge_agent_record(rec):
    agent_eval, usage = evaluate_agent_answer(rec)
    return {
        "question": rec["question"],
        "document": rec["document"],
        "answer_score": agent_eval.answer_score,
        "answer_reasoning": agent_eval.answer_reasoning,
        "trajectory_score": agent_eval.trajectory_score,
        "trajectory_reasoning": agent_eval.trajectory_reasoning,
    }, usage

with ThreadPoolExecutor(max_workers=6) as pool:
    results = map_progress(pool, agent_answers, judge_agent_record)

agent_evaluations, usages = zip(*results)
df_agent_eval = pd.DataFrame(agent_evaluations)

print(df_agent_eval["answer_score"].value_counts())
# good    45
# bad      5

print(df_agent_eval["trajectory_score"].value_counts())
# good    49
# bad      1

df_agent_eval.to_csv("data/agent-evaluations.csv", index=False)
```

> **Cost reference:** 50 answers judged → ~$0.05

**Diagnosing failures with two scores:**

| answer_score | trajectory_score | Likely cause |
|---|---|---|
| bad | bad | Agent searched for the wrong thing or stopped too early |
| bad | good | Model retrieved correctly but answered poorly |
| good | bad | Got lucky despite poor tool use — worth fixing |
| good | good | Pipeline working as expected |

---

## File Structure

```
04-evaluation/
├── data/
│   ├── ground_truth-new.csv      # questions + correct document IDs
│   ├── rag-answers-new.csv       # RAG answers alongside original answers
│   ├── rag-evaluations-new.csv   # judge scores for RAG answers
│   ├── agent-answers.csv         # agent answers + tool call trajectories
│   └── agent-evaluations.csv     # judge scores for agent answers + trajectories
├── notebooks/
│   ├── 01_ground_truth.ipynb
│   ├── 02_search_evaluation.ipynb
│   ├── 03_rag_evaluation.ipynb
│   └── 04_agent_evaluation.ipynb
├── evaluation_utils.py            # shared helpers: retry, cost calc, parallel map
└── ingest.py                      # FAQ loader and search index builder
```

---

## Cost Summary

| Step | Records | Cost |
|---|---|---|
| Ground truth generation | 79 docs → 395 questions | ~$0.06 |
| RAG answer generation | 395 questions | ~$0.34 |
| RAG judge | 395 answers | ~$0.25 |
| Agent answer generation | 50 questions | ~$0.07 |
| Agent judge | 50 answers | ~$0.05 |
| **Total** | | **~$0.77** |

---

## Key Takeaways

**1. Measure instead of guess.**
Intuition said boosting the `question` field would help retrieval. The data showed `answer` mattered more. Without offline evaluation, you would never know.

**2. Separate retrieval quality from answer quality.**
A low RAG score could mean bad search OR bad generation. Evaluating them independently tells you exactly where to fix things.

**3. Trajectory evaluation catches silent agent failures.**
An agent can produce a correct answer through bad behavior (lucky guess, redundant searches). Scoring tool calls separately reveals this.

**4. The judge needs to be evaluated too.**
Sample bad cases manually and check whether you agree with the judge's verdict. If the judge is too lenient, tighten the instructions. You cannot use another LLM to evaluate the judge — this step requires human review.

**5. Synthetic ground truth inflates metrics.**
Generated questions are close to the source text, which makes retrieval look better than it is. Treat numbers above 95% with caution and validate with real user questions when possible.