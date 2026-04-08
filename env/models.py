from pydantic import BaseModel, field_validator
from typing import Optional, Literal

class Observation(BaseModel):
    id: str
    title: str
    body: str
    author: str
    labels: list[str]
    repo: str
    comment_count: int = 0
    code_snippet: Optional[str] = None

class Action(BaseModel):
    verdict: Literal["valid", "duplicate", "needs-info", "wontfix"]
    severity: Literal["critical", "high", "medium", "low"]
    team: Literal["frontend", "backend", "infra", "docs", "security"]
    needs_repro: bool = False

class Reward(BaseModel):
    score: float
    breakdown: dict
    explanation: str

    @field_validator("score")
    @classmethod
    def clamp(cls, v):
        return round(max(0.0, min(1.0, v)), 3)
