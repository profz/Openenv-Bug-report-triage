from env.models import Action, Reward

SEVERITY = ["low", "medium", "high", "critical"]

def score_action(action: Action, ground_truth: dict) -> Reward:
    score = 0.0
    breakdown = {}

    # verdict: 0.6 weight — most important signal
    breakdown["verdict"] = 0.6 if action.verdict == ground_truth["verdict"] else 0.0
    score += breakdown["verdict"]

    # penalty: marking critical bug as wontfix is the worst possible mistake
    if ground_truth["severity"] == "critical" and action.verdict == "wontfix":
        score -= 0.2
        breakdown["critical_wontfix_penalty"] = -0.2

    # severity: 0.25 weight, partial credit within 1 level
    pi, ti = SEVERITY.index(action.severity), SEVERITY.index(ground_truth["severity"])
    if pi == ti:
        breakdown["severity"] = 0.25
    elif abs(pi - ti) == 1:
        breakdown["severity"] = 0.1
    else:
        breakdown["severity"] = 0.0
    score += breakdown["severity"]

    # team: 0.15 weight
    breakdown["team"] = 0.15 if action.team == ground_truth["team"] else 0.0
    score += breakdown["team"]

    v = "✓" if breakdown["verdict"] else "✗"
    s = "✓" if breakdown["severity"] == 0.25 else ("~" if breakdown["severity"] else "✗")
    t = "✓" if breakdown["team"] else "✗"

    return Reward(
        score=score,
        breakdown=breakdown,
        explanation=f"verdict={v} severity={s} team={t}",
    )

grade = score_action
