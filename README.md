---
title: Openenv Bug Triage
emoji: 🐛
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "5.23.0"
app_file: app.py
pinned: false
tags:
  - openenv
  - bug-triage
  - rl-environment
---

# OpenEnv — Bug Report Triage

An AI agent environment simulating real-world GitHub bug report triage.
Implements the full [OpenEnv](https://huggingface.co/openenv) spec with typed models,
`step()` / `reset()` / `state()` API, and programmatic graders.

## Motivation

Every active open-source project drowns in bug reports. Maintainers spend hours
triaging: is this valid? duplicate? which team? how urgent? This environment
lets AI agents learn and be benchmarked on that exact task.

---

## Observation Space

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique report ID |
| `title` | `str` | Issue title |
| `body` | `str` | Issue body (truncated to 600 chars) |
| `author` | `str` | Reporter username |
| `labels` | `list[str]` | Existing labels |
| `repo` | `str` | Repository name |
| `comment_count` | `int` | Number of existing comments |
| `code_snippet` | `str?` | Extracted code block if present |

## Action Space

| Field | Type | Values |
|---|---|---|
| `verdict` | `enum` | `valid`, `duplicate`, `needs-info`, `wontfix` |
| `severity` | `enum` | `critical`, `high`, `medium`, `low` |
| `team` | `enum` | `frontend`, `backend`, `infra`, `docs`, `security` |
| `needs_repro` | `bool` | Whether reproduction steps are required |

## Reward Function

| Component | Weight | Notes |
|---|---|---|
| verdict correct | 0.60 | Binary |
| severity correct | 0.25 | Partial credit within 1 level = 0.10 |
| team correct | 0.15 | Binary |
| critical to wontfix penalty | -0.20 | Dangerous misclassification |

---

## Tasks

| ID | Difficulty | Reports | Random Agent | GPT-4o-mini |
|---|---|---|---|---|
| `validity-check-v1` | Easy | 25 | 0.268 | ~0.82 |

Dataset: real GitHub issues from `fastapi` and `numpy`, plus hand-crafted edge cases.

---

## Setup

```bash
pip install -e .

python scripts/baseline.py --agent random

OPENAI_API_KEY=sk-... python scripts/baseline.py --agent llm

python app.py
```

## Docker

```bash
docker build -t openenv-bug-triage .
docker run openenv-bug-triage
```

---

## Write Your Own Agent

```python
from env.models import Observation, Action

def act(obs: Observation) -> Action:
    return Action(
        verdict="valid",
        severity="medium",
        team="backend",
        needs_repro=False,
    )
```

Plug into the env:

```python
from env.bugreport_env import BugReportEnv
from tasks.validity_check.grader import score_action

env = BugReportEnv("tasks/validity_check/reports.json", grader_fn=score_action)
obs = env.reset(seed=42)
done = False

while not done:
    action = act(obs)
    obs, reward, done, info = env.step(action)
    print(reward.score, reward.explanation)

print("Final:", env.state()["mean_reward"])
```
