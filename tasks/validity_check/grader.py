from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

@dataclass
class GradeResult:
    score: float
    label: str
    details: str = ""

def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))

def grade_verdict(action_dict: dict, ground_truth: dict) -> GradeResult:
    correct = action_dict.get("verdict") == ground_truth.get("verdict")
    score = 0.6 if correct else 0.0
    if ground_truth.get("severity") == "critical" and action_dict.get("verdict") == "wontfix":
        score -= 0.2
    return GradeResult(score=clamp(score), label="Verdict", details=f"verdict={'correct' if correct else 'wrong'}")

def grade_severity(action_dict: dict, ground_truth: dict) -> GradeResult:
    SEVERITY = ["low", "medium", "high", "critical"]
    try:
        pi = SEVERITY.index(action_dict.get("severity", "low"))
        ti = SEVERITY.index(ground_truth.get("severity", "low"))
        if pi == ti:
            score = 0.25
        elif abs(pi - ti) == 1:
            score = 0.1
        else:
            score = 0.0
    except ValueError:
        score = 0.0
    return GradeResult(score=clamp(score), label="Severity", details=f"diff={abs(pi-ti)}")

def grade_team(action_dict: dict, ground_truth: dict) -> GradeResult:
    correct = action_dict.get("team") == ground_truth.get("team")
    return GradeResult(score=0.15 if correct else 0.0, label="Team", details=f"team={'correct' if correct else 'wrong'}")

def grade_episode(
    action_dict: dict,
    ground_truth: dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[GradeResult]]:
    grades = [
        grade_verdict(action_dict, ground_truth),
        grade_severity(action_dict, ground_truth),
        grade_team(action_dict, ground_truth),
    ]
    if weights is None:
        weights = {"Verdict": 0.6, "Severity": 0.25, "Team": 0.15}
    composite = sum(g.score * weights.get(g.label, 0.0) / max(weights.get(g.label, 1.0), 1e-9) * weights.get(g.label, 0.0) for g in grades)
    composite = sum(g.score for g in grades)
    return clamp(composite), grades

def score_action(action, ground_truth: dict) -> dict:
    if hasattr(action, 'model_dump'):
        action_dict = action.model_dump()
    elif isinstance(action, dict):
        action_dict = action
    else:
        action_dict = vars(action)
    composite, grades = grade_episode(action_dict, ground_truth)
    breakdown = {g.label: g.score for g in grades}
    explanation = " ".join(f"{g.label}={'✓' if g.score > 0 else '✗'}" for g in grades)
    return {"score": composite, "breakdown": breakdown, "explanation": explanation}

grade = score_action
