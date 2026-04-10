from pydantic import BaseModel

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

def score_action(action, ground_truth: dict) -> dict:
    s = 0.0
    bd = {}
    bd["verdict"] = 0.6 if action.verdict == ground_truth["verdict"] else 0.0
    s += bd["verdict"]
    if ground_truth["severity"] == "critical" and action.verdict == "wontfix":
        bd["penalty"] = -0.2
        s -= 0.2
    pi = SEVERITY.index(action.severity)
    ti = SEVERITY.index(ground_truth["severity"])
    bd["severity"] = 0.25 if pi == ti else (0.1 if abs(pi-ti)==1 else 0.0)
    s += bd["severity"]
    bd["team"] = 0.15 if action.team == ground_truth["team"] else 0.0
    s += bd["team"]
    score = round(max(0.0, min(1.0, s)), 3)
    return {"score": score, "breakdown": bd, "explanation": f"v={'✓' if bd['verdict'] else '✗'} s={'✓' if bd['severity']==0.25 else '✗'} t={'✓' if bd['team'] else '✗'}"}

grade = score_action
