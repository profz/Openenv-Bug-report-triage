from __future__ import annotations
from typing import List
from graders import grade_episode, GradeResult

TASKS = [
    {
        "id": "validity-check-v1",
        "difficulty": "easy",
        "description": "Classify bug reports as valid/duplicate/needs-info/wontfix with severity and team",
        "dataset": "tasks/validity_check/reports.json",
    },
    {
        "id": "severity-routing-v1",
        "difficulty": "medium",
        "description": "Route bug reports to correct team with emphasis on severity classification",
        "dataset": "tasks/severity_routing/reports.json",
    },
    {
        "id": "full-triage-v1",
        "difficulty": "hard",
        "description": "Full triage including verdict, severity, team, and reproduction requirements",
        "dataset": "tasks/full_triage/reports.json",
    },
]

def get_task(task_id: str) -> dict:
    for t in TASKS:
        if t["id"] == task_id:
            return t
    raise ValueError(f"Unknown task: {task_id}")

def list_tasks() -> List[dict]:
    return TASKS
