import random
from env.models import Action, Observation

VERDICTS = ["valid", "duplicate", "needs-info", "wontfix"]
SEVERITIES = ["critical", "high", "medium", "low"]
TEAMS = ["frontend", "backend", "infra", "docs", "security"]

def act(obs: Observation) -> Action:
    return Action(
        verdict=random.choice(VERDICTS),
        severity=random.choice(SEVERITIES),
        team=random.choice(TEAMS),
        needs_repro=random.choice([True, False]),
    )
