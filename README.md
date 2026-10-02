# SolutionAI_Autogen

A multi-agent incident-analysis assistant built on [AutoGen](https://github.com/ag2ai/ag2) with a [Gradio](https://www.gradio.app/) chat UI.

You describe an operational or production problem in plain language. Six specialist agents — each with a different role in the incident-response lifecycle — process the problem, and the UI shows both the final answer and the full per-agent execution trace. Every run is appended to `conversation.txt` as an audit log.

---

## The agent team

Defined in [agents.py](agents.py), each as an AutoGen `AssistantAgent` with a single-purpose system message:

| Agent | Role |
|---|---|
| `Scenario_explainer` | Explains the current scenario in the process |
| `incident_responder` | Articulates the incident that occurred |
| `rca_finder` | Performs root cause analysis and reports the root cause |
| `immediate_fixer` | Proposes the immediate fix to address the client |
| `mitigation_expert` | Produces mitigation steps to resolve the problem |
| `summarizer` | Summarizes everything and closes out with the stakeholder |

The agents are assembled into an AutoGen `GroupChat` (`max_round=2`) in [groupchat.py](groupchat.py), and a `GroupChatManager` wraps a group chat in [groupchat_manager.py](groupchat_manager.py).

---

## Architecture

```
main.py              Gradio UI + orchestration driver
  │
  ├── groupchat.py            → GroupChat(agents=[...6 agents...], max_round=2)
  │     └── agents.py         → six AssistantAgent factory functions
  │           └── llm.py      → llm_config (model + API key from .env)
  │
  └── groupchat_manager.py    → GroupChatManager(groupchat, llm_config)
```

Request flow in [main.py](main.py):

1. `chat()` receives the user's message from the Gradio textbox and calls `run_autogen()`.
2. `run_autogen()` builds a fresh `GroupChat` and `GroupChatManager` per request ([main.py:17-18](main.py#L17-L18)).
3. It iterates over `groupchat.agents` and has each agent `initiate_chat()` with the manager ([main.py:32-46](main.py#L32-L46)).
4. Each agent's result is collected into a `conversation` list and appended to `conversation.txt`.
5. The last agent's response becomes the final chat answer; the full list is rendered as the **Agent Execution Trace** panel.

### Model configuration

[llm.py](llm.py) returns an AutoGen `llm_config` dict:

```python
{"config_list": [{"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")}]}
```

To change the model, edit the `model` value in [llm.py:13](llm.py#L13).

---

## Setup

**Requirements:** Python 3.13 (the checked-in virtual environment was created with 3.13.7) and an OpenAI API key.

### 1. Create and activate a virtual environment

```powershell
python -m venv .solutionaiautogen
.\.solutionaiautogen\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

`requirements.txt` is a full `pip freeze` of the working environment (80 pinned packages). The ones that matter directly:

- `autogen==0.14.1` — multi-agent framework
- `gradio==6.29.0` — web UI
- `openai==3.22.1` — model client
- `langchain-openai==1.6.7` — imported in `llm.py`
- `python-dotenv==1.2.3` — `.env` loading

If you prefer a minimal install instead of the frozen set:

```powershell
pip install autogen gradio openai langchain-openai python-dotenv
```

### 3. Configure your API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
```

### 4. Run

```powershell
python main.py
```

Gradio prints a local URL (default `http://127.0.0.1:7860`). Open it, type a problem into **Your Request**, and press **Send** or Enter.

---

## Using it

The UI ([main.py:164-291](main.py#L164-L291)) has four parts:

- **Conversation** — the chat history (user message → final agent answer)
- **Agent Execution Trace** — every agent's output, numbered and separated, so you can see each role's contribution
- **Your Request** — a 3-line textbox; Enter submits
- **Clear Conversation** — resets the chat and the trace

Example prompt:

> An employee using the company's AI-powered Knowledge Assistant requested project-specific information, but the AI mistakenly returned confidential architecture and security details from another client's project. Analyze the incident, identify the likely root cause, assess the business and security impact, recommend immediate containment actions, and propose long-term preventive measures.

Errors are caught in `chat()` and surfaced in the trace panel rather than crashing the app; empty submissions are rejected before any model call.

---

## Files

| File | Purpose |
|---|---|
| [main.py](main.py) | Gradio UI, orchestration driver, conversation logging |
| [agents.py](agents.py) | Six `AssistantAgent` factory functions |
| [groupchat.py](groupchat.py) | Assembles the agents into a `GroupChat` |
| [groupchat_manager.py](groupchat_manager.py) | Builds the `GroupChatManager` |
| [llm.py](llm.py) | Loads `.env` and returns the AutoGen `llm_config` |
| [requirements.txt](requirements.txt) | Pinned dependencies (`pip freeze`) |
| `conversation.txt` | Append-only log of every run (generated) |
| `.env` | API key (not committed) |

---

## Known limitations

These are real behaviours of the current code, worth knowing before you build on it:

1. **The agents don't actually collaborate.** `run_autogen()` loops over the agents and calls `initiate_chat()` on each one independently ([main.py:32-39](main.py#L32-L39)). Each agent starts a separate conversation with the manager from the same original user message, so no agent sees any other agent's output. The intended AutoGen pattern is a single `initiate_chat()` against the `GroupChatManager`, letting the manager route turns between agents.

2. **The manager is wired to a different group chat than the one being iterated.** `create_groupchat_manager()` calls `create_groupchat()` itself ([groupchat_manager.py:8](groupchat_manager.py#L8)), producing a second `GroupChat` with six brand-new agent instances. The agents `main.py` loops over are not the agents the manager manages. Pass the existing `groupchat` into the manager instead.

3. **`max_round=2`** ([groupchat.py:16](groupchat.py#L16)) is lower than the six agents in the chat, so a correctly wired group chat would terminate before every agent had spoken.

4. **Raw `ChatResult` objects are logged and displayed.** `str(response)` on an AutoGen `ChatResult` yields the full repr (chat_id, chat_history, cost, …) rather than the message text. Use `response.summary` or `response.chat_history[-1]["content"]` for readable output.

5. **`conversation.txt` grows unbounded** — it is opened in append mode with no rotation or size cap.

6. **No `.gitignore` at the project root.** The project is not currently a git repository; if you initialize one, exclude `.env`, `.solutionaiautogen/`, `__pycache__/`, and `conversation.txt` before the first commit so the API key is never committed.

7. **`langchain_openai` is imported but unused.** [llm.py:2](llm.py#L2) imports `ChatOpenAI`; the function returns a plain AutoGen config dict. The import (and the dependency) can be dropped.

---

## Roadmap

- Rewire orchestration to a single `GroupChatManager`-driven conversation so agents build on each other's findings
- Raise `max_round` to match the agent count and add a termination condition on the summarizer
- Extract readable text from `ChatResult` before logging and rendering
- Stream agent outputs to the UI instead of blocking until all agents finish
- Make the model, temperature, and round count configurable from `.env`
