from pydantic import BaseModel, field_validator
from typing import Optional, Literal, List

class BugObservation(BaseModel):
    id: str = ""
    title: str = ""
    body: str = ""
    author: str = ""
    labels: List[str] = []
    repo: str = ""
    comment_count: int = 0
    code_snippet: Optional[str] = None

class BugAction(BaseModel):
    verdict: Literal["valid", "duplicate", "needs-info", "wontfix"] = "needs-info"
    severity: Literal["critical", "high", "medium", "low"] = "low"
    team: Literal["frontend", "backend", "infra", "docs", "security"] = "backend"
    needs_repro: bool = False

class BugReward(BaseModel):
    score: float
    breakdown: dict
    explanation: str

    @field_validator("score")
    @classmethod
    def clamp(cls, v):
        return round(max(0.0, min(1.0, v)), 3)
