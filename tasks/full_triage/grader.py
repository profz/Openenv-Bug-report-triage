from pydantic import BaseModel
from typing import Any

class Action(BaseModel):
    verdict: str = "needs-info"
    severity: str = "low"
    team: str = "backend"
    needs_repro: bool = False

class Reward(BaseModel):
    score: float
    breakdown: dict
    explanation: str

SEVERITY = ["low", "medium", "high", "critical"]

def score_action(action: Any, ground_truth: dict) -> Reward:
    score = 0.0
    breakdown = {}
    breakdown["verdict"] = 0.6 if action.verdict == ground_truth["verdict"] else 0.0
    score += breakdown["verdict"]
    if ground_truth.get("severity") == "critical" and action.verdict == "wontfix":
        score -= 0.2
        breakdown["critical_wontfix_penalty"] = -0.2
    pi = SEVERITY.index(action.severity) if action.severity in SEVERITY else 0
    ti = SEVERITY.index(ground_truth["severity"]) if ground_truth.get("severity") in SEVERITY else 0
    if pi == ti:
        breakdown["severity"] = 0.25
    elif abs(pi - ti) == 1:
        breakdown["severity"] = 0.1
    else:
        breakdown["severity"] = 0.0
    score += breakdown["severity"]
    breakdown["team"] = 0.15 if action.team == ground_truth.get("team") else 0.0
    score += breakdown["team"]
    return Reward(score=round(max(0.0, min(1.0, score)), 3), breakdown=breakdown,
                  explanation=f"verdict={'✓' if breakdown['verdict'] else '✗'} severity={'✓' if breakdown.get('severity')==0.25 else '✗'} team={'✓' if breakdown['team'] else '✗'}")

grade = score_action
