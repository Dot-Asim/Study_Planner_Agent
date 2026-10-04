<div align="center">
  <h1>📚 Study-Plan Builder Agent</h1>
  <p><i>An autonomous, conflict-aware study session scheduler powered by Groq and LangChain.</i></p>
  
  [![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-00a393.svg)](https://fastapi.tiangolo.com/)
  [![LangChain](https://img.shields.io/badge/LangChain-Integration-orange.svg)](https://www.langchain.com/)
  [![Groq](https://img.shields.io/badge/Groq-Llama%203.1-black.svg)](https://groq.com/)
</div>

---

## 🌟 Overview
The **Study-Plan Builder** is an intelligent, bounded agent designed for the Agent Arena Reliability Challenge. It solves a common student problem: gracefully fitting assignments and study tasks into a busy, fixed weekly timetable without conflicts.

Built with an autonomous loop, the agent fetches your current class timetable, reviews pending assignments and their required hours, and autonomously schedules study blocks. It operates within a strict sandboxed `AgentState` and validates every decision against predefined rules to prevent hallucinated tasks or overlapping schedules.

---

## 🎯 Problem and Measurable Completion
- **The Challenge**: Students struggle to manually balance fixed class schedules with incoming assignment deadlines, often leading to poor time management and missed work.
- **The Goal**: Schedule study sessions for all pending tasks into available time blocks on or before their deadlines, without any overlaps.
- **Completion Condition**: The agent autonomously halts with a `completed` status once every task in the sandbox has been successfully scheduled.

---

## 🎨 Agent Design Canvas

| Element | Definition |
| :--- | :--- |
| **Operational Goal** | Schedule study sessions for pending tasks without conflicts. |
| **Completion Condition** | All pending tasks are scheduled successfully. |
| **System Boundary** | The agent operates strictly within the provided `AgentState` sandbox (timetable and pending tasks). |
| **Observations** | Agent observes tool outputs: timetable, pending tasks, and success/error messages from scheduling attempts. |
| **Actions / Tools** | `get_timetable`, `get_pending_tasks`, `schedule_session`, `get_scheduled_sessions`. |
| **State Tracking** | Tracked per-run in `AgentState`: `scheduled_sessions`, `timetable`, `pending_tasks`. |
| **Autonomy Boundary** | The agent can schedule freely within the sandbox. It **cannot** invent tasks or override external fixed timetables. |
| **Primary Risks** | Hallucinating tasks, scheduling overlapping sessions, missing deadlines, or getting stuck in infinite loops. |
| **Evaluation Criteria** | Correctness of the final schedule (no overlaps, correct duration), proper handling of injected faults (e.g., timeouts, malformed schema). |

---

## 🏗️ Architecture & File Map

The project is structured around a FastAPI backend that handles the Agent Arena contract and a LangChain-powered agent loop.

```text
Study_Planner_Agent/
├── app/
│   ├── main.py       # FastAPI application entry point
│   ├── api.py        # Core endpoints (/models, /arena/run, /chat)
│   ├── agent.py      # Bounded agent loop & fault injection logic
│   ├── prompts.py    # Strict system policy and constraints
│   ├── models.py     # Pydantic schemas (AgentDecision, AgentState)
│   ├── tools.py      # Sandboxed tool implementations
│   └── arena.py      # Timeout wrapper & safe event logging
├── data/
│   └── sample_data.json  # Initial sandbox state
├── requirements.txt
└── run.py            # Local development server script
```

---

## 🧠 Model Comparison

We evaluated multiple models to find the best balance of speed, cost, and strict schema adherence.

| Metric | 🦙 llama-3.1-70b-versatile | ⚡ llama-3.1-8b-instant |
|:---|:---:|:---:|
| **Task Success** | 10/10 | 9/10 |
| **Schema Validity** | 10/10 | 10/10 |
| **Action Selection** | 10/10 | 9/10 |
| **Latency** | ~1.5s | ~0.8s |
| **Token Usage** | ~300 in / 100 out | ~300 in / 100 out |
| **Approximate Cost** | Low | Very Low |

> **Selection Rationale**: Both models perform exceptionally well on structured output, but `llama-3.1-70b-versatile` provides flawless reasoning for scheduling logic with only a negligible impact on latency, making it our default model.

---

## 🛡️ Reliability & Constraints

### 1. Prompt & Context Design
- **System**: Enforces the agent's persona, strict tool definitions, and absolute requirement to output raw JSON.
- **History**: Bounded, multi-turn history passed to LangChain to maintain context across clarifications without overflowing the token budget.
- **Untrusted Context**: User inputs and external data are explicitly isolated to prevent prompt injection.

### 2. Typed Schema Validation
Every decision the model makes is strictly validated against a Pydantic `AgentDecision` schema. If the model attempts to output arbitrary text instead of JSON, the loop intercepts it and prompts a retry, protecting the system from malformed execution.

### 3. Fault Handling & Budgets
The agent is designed to survive the Reliability Arena stress tests:
- Automatically retries or downgrades upon simulated tool timeouts.
- Handles malformed tool outputs gracefully.
- Bounded strictly by `max_steps` to prevent infinite loops and runaway costs.

---

## 🚀 Setup & Deployment

### Local Development
1. Clone the repository and navigate to the project root.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows: .\.venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your Groq API key:
   - Rename `.env.example` to `.env`
   - Add your key: `GROQ_API_KEY=your_key_here`
5. Start the server:
   ```bash
   python run.py
   ```
6. Open `http://127.0.0.1:8000/` in your browser.

### Deployment Limitations
- **State Persistence**: The current implementation utilizes an in-memory state. Restarting the server resets all chat history and sandbox state. Ensure you use a single worker instance (`--workers 1`) during deployment.

---
<div align="center">
  <i>Developed for the Agentic AI - Reliability Challenge</i>
</div>
