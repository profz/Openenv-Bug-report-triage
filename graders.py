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

SEVERITY = ["low", "medium", "high", "critical"]

# ── Individual Graders ────────────────────────────────────────────────────────

def grade_verdict(action_dict: dict, ground_truth: dict) -> GradeResult:
    correct = action_dict.get("verdict") == ground_truth.get("verdict")
    score = 0.6 if correct else 0.0
    if ground_truth.get("severity") == "critical" and action_dict.get("verdict") == "wontfix":
        score -= 0.2
    return GradeResult(score=clamp(score), label="Verdict",
                       details=f"verdict={'correct' if correct else 'wrong'}")

def grade_severity(action_dict: dict, ground_truth: dict) -> GradeResult:
    try:
        pi = SEVERITY.index(action_dict.get("severity", "low"))
        ti = SEVERITY.index(ground_truth.get("severity", "low"))
        score = 0.25 if pi == ti else (0.1 if abs(pi - ti) == 1 else 0.0)
        diff = abs(pi - ti)
    except ValueError:
        score, diff = 0.0, 0
    return GradeResult(score=clamp(score), label="Severity", details=f"diff={diff}")

def grade_team(action_dict: dict, ground_truth: dict) -> GradeResult:
    correct = action_dict.get("team") == ground_truth.get("team")
    return GradeResult(score=0.15 if correct else 0.0, label="Team",
                       details=f"team={'correct' if correct else 'wrong'}")

def grade_needs_repro(action_dict: dict, ground_truth: dict) -> GradeResult:
    correct = action_dict.get("needs_repro") == ground_truth.get("needs_repro", False)
    return GradeResult(score=0.1 if correct else 0.0, label="NeedsRepro",
                       details=f"repro={'correct' if correct else 'wrong'}")

# ── Per-task composite graders ────────────────────────────────────────────────

def grade_validity_check(
    action_dict: dict,
    ground_truth: dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[GradeResult]]:
    """Easy: binary valid/invalid classification."""
    grades = [
        grade_verdict(action_dict, ground_truth),
        grade_severity(action_dict, ground_truth),
        grade_team(action_dict, ground_truth),
    ]
    return clamp(sum(g.score for g in grades)), grades

def grade_severity_routing(
    action_dict: dict,
    ground_truth: dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[GradeResult]]:
    """Medium: emphasis on correct severity routing."""
    verdict = grade_verdict(action_dict, ground_truth)
    verdict.score = clamp(verdict.score * 0.5 / 0.6)  # scale to 0.5 weight
    sev = grade_severity(action_dict, ground_truth)
    sev.score = clamp(sev.score * 0.35 / 0.25)        # scale to 0.35 weight
    team = grade_team(action_dict, ground_truth)
    grades = [verdict, sev, team]
    return clamp(sum(g.score for g in grades)), grades

def grade_full_triage(
    action_dict: dict,
    ground_truth: dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[GradeResult]]:
    """Hard: full action space including needs_repro."""
    grades = [
        grade_verdict(action_dict, ground_truth),
        grade_severity(action_dict, ground_truth),
        grade_team(action_dict, ground_truth),
        grade_needs_repro(action_dict, ground_truth),
    ]
    return clamp(sum(g.score for g in grades)), grades

# ── Main entry point ──────────────────────────────────────────────────────────

def grade_episode(
    action_dict: dict,
    ground_truth: dict,
    task_id: str = "validity-check-v1",
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[GradeResult]]:
    if task_id == "severity-routing-v1":
        return grade_severity_routing(action_dict, ground_truth, weights)
    elif task_id == "full-triage-v1":
        return grade_full_triage(action_dict, ground_truth, weights)
    else:
        return grade_validity_check(action_dict, ground_truth, weights)

def score_action(action, ground_truth: dict, task_id: str = "validity-check-v1") -> dict:
    if hasattr(action, "model_dump"):
        action_dict = action.model_dump()
    elif isinstance(action, dict):
        action_dict = action
    else:
        action_dict = vars(action)
    composite, grades = grade_episode(action_dict, ground_truth, task_id)
    return {
        "score": composite,
        "breakdown": {g.label: g.score for g in grades},
        "explanation": " ".join(f"{g.label}={'✓' if g.score > 0 else '✗'}" for g in grades),
    }

grade = score_action
