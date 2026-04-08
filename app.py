import os
from fastapi import FastAPI
from env.bugreport_env import BugReportEnv
from env.models import Action
from tasks.validity_check.grader import score_action

app = FastAPI(title="OpenEnv Bug Triage")
env = BugReportEnv("tasks/validity_check/reports.json", grader_fn=score_action)

@app.post("/reset")
def reset():
    obs = env.reset(seed=42)
    return obs.model_dump()

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    }

@app.get("/state")
def state():
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok"}
