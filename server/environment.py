import json
import random
from pathlib import Path
from openenv.core import Environment, Action, Observation, State

class BugAction(Action):
    verdict: str = "needs-info"
    severity: str = "low"
    team: str = "backend"
    needs_repro: bool = False

class BugObservation(Observation):
    id: str = ""
    title: str = ""
    body: str = ""
    author: str = ""
    labels: list = []
    repo: str = ""
    comment_count: int = 0

SEVERITY = ["low", "medium", "high", "critical"]

def score(action: BugAction, gt: dict) -> float:
    s = 0.0
    s += 0.6 if action.verdict == gt["verdict"] else 0.0
    if gt["severity"] == "critical" and action.verdict == "wontfix":
        s -= 0.2
    pi, ti = SEVERITY.index(action.severity), SEVERITY.index(gt["severity"])
    s += 0.25 if pi == ti else (0.1 if abs(pi - ti) == 1 else 0.0)
    s += 0.15 if action.team == gt["team"] else 0.0
    return round(max(0.0, min(1.0, s)), 3)

class BugTriageEnvironment(Environment):
    def __init__(self, task_path: str = "tasks/validity_check/reports.json"):
        self.task_path = Path(task_path)
        self.reports = []
        self.index = 0
        self.history = []
        self.cumulative = 0.0

    def reset(self) -> BugObservation:
        self.reports = json.loads(self.task_path.read_text())
        random.seed(42)
        random.shuffle(self.reports)
        self.index = 0
        self.history = []
        self.cumulative = 0.0
        return self._obs(self.reports[0])

    def step(self, action: BugAction):
        report = self.reports[self.index]
        reward = score(action, report["ground_truth"])
        self.cumulative += reward
        self.history.append((report["id"], reward))
        self.index += 1
        done = self.index >= len(self.reports)
        obs = self._obs(self.reports[self.index] if not done else report)
        return obs, reward, done

    def state(self) -> State:
        return State(
            step=self.index,
            done=self.index >= len(self.reports),
            metadata={
                "cumulative": self.cumulative,
                "mean": round(self.cumulative / max(self.index, 1), 3),
            }
        )

    def _obs(self, r: dict) -> BugObservation:
        return BugObservation(
            id=r["id"], title=r["title"], body=r["body"],
            author=r["author"], labels=r.get("labels", []),
            repo=r["repo"], comment_count=r.get("comment_count", 0),
        )
