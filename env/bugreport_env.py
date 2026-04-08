import json
import random
from pathlib import Path
from .base import BaseEnv
from .models import Observation, Action, Reward

class BugReportEnv(BaseEnv):
    def __init__(self, task_path: str, grader_fn=None):
        self.task_path = Path(task_path)
        self.grader_fn = grader_fn
        self.reports: list[dict] = []
        self.index = 0
        self.history: list[tuple] = []
        self.cumulative_reward = 0.0

    def reset(self, seed: int = 42) -> Observation:
        self.reports = json.loads(self.task_path.read_text())
        random.seed(seed)
        random.shuffle(self.reports)
        self.index = 0
        self.history = []
        self.cumulative_reward = 0.0
        return self._obs(self.reports[0])

    def step(self, action: Action) -> tuple[Observation, Reward, bool, dict]:
        report = self.reports[self.index]
        reward = self.grader_fn(action, report["ground_truth"])
        self.cumulative_reward += reward.score
        self.history.append((report["id"], action.model_dump(), reward.score))
        self.index += 1
        done = self.index >= len(self.reports)
        next_obs = self._obs(self.reports[self.index] if not done else report)
        return next_obs, reward, done, {"step": self.index}

    def state(self) -> dict:
        return {
            "index": self.index,
            "total": len(self.reports),
            "cumulative_reward": round(self.cumulative_reward, 3),
            "mean_reward": round(self.cumulative_reward / max(self.index, 1), 3),
            "history": self.history,
        }

    def _obs(self, r: dict) -> Observation:
        return Observation(
            id=r["id"], title=r["title"], body=r["body"],
            author=r["author"], labels=r.get("labels", []),
            repo=r["repo"], comment_count=r.get("comment_count", 0),
            code_snippet=r.get("code_snippet"),
        )
