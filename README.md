---
title: Openenv Bug Triage
emoji: 🐛
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
tags:
  - openenv
  - bug-triage
  - rl-environment
---

# OpenEnv — Bug Report Triage

An AI agent environment simulating real-world GitHub bug report triage.
Implements the full OpenEnv spec with typed models, `step()` / `reset()` / `state()` API.

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/reset` | Start new episode, returns initial observation |
| POST | `/step` | Submit action, returns observation + reward + done |
| GET | `/state` | Current episode snapshot |
| GET | `/health` | Health check |

## Observation Space

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique report ID |
| `title` | `str` | Issue title |
| `body` | `str` | Issue body |
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

## Tasks

| ID | Difficulty | Reports | Random Agent |
|---|---|---|---|
| `validity-check-v1` | Easy | 25 | 0.268 |

## Setup

```bash
pip install -r requirements.txt
PYTHONPATH=. uvicorn app:app --reload
```

## Docker

```bash
docker build -t openenv-bug-triage .
docker run -p 7860:7860 openenv-bug-triage
```
