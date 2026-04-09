from env.models import Action, Reward

SEVERITY = ["low", "medium", "high", "critical"]

def score_action(action: Action, ground_truth: dict) -> Reward:
    score = 0.0
    breakdown = {}

    breakdown["verdict"] = 0.5 if action.verdict == ground_truth["verdict"] else 0.0
    score += breakdown["verdict"]

    if ground_truth["severity"] == "critical" and action.verdict == "wontfix":
        score -= 0.2
        breakdown["critical_wontfix_penalty"] = -0.2

    pi, ti = SEVERITY.index(action.severity), SEVERITY.index(ground_truth["severity"])
    if pi == ti:
        breakdown["severity"] = 0.35
    elif abs(pi - ti) == 1:
        breakdown["severity"] = 0.15
    else:
        breakdown["severity"] = 0.0
    score += breakdown["severity"]

    breakdown["team"] = 0.15 if action.team == ground_truth["team"] else 0.0
    score += breakdown["team"]

    v = "✓" if breakdown["verdict"] else "✗"
    s = "✓" if breakdown["severity"] == 0.35 else ("~" if breakdown["severity"] else "✗")
    t = "✓" if breakdown["team"] else "✗"

    return Reward(
        score=score,
        breakdown=breakdown,
        explanation=f"verdict={v} severity={s} team={t}",
    )

grade = score_action
