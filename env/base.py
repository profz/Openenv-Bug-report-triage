from abc import ABC, abstractmethod
from .models import Observation, Action, Reward

class BaseEnv(ABC):
    @abstractmethod
    def reset(self, seed: int = 42) -> Observation: ...

    @abstractmethod
    def step(self, action: Action) -> tuple[Observation, Reward, bool, dict]: ...

    @abstractmethod
    def state(self) -> dict: ...
