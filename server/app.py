import uvicorn
from openenv.core import create_app
from server.environment import BugTriageEnvironment, BugAction, BugObservation

app = create_app(
    env=BugTriageEnvironment,
    action_cls=BugAction,
    observation_cls=BugObservation,
    env_name="openenv-bug-triage",
)

# expose tasks so validator can discover graders
@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {"id": "validity-check-v1",   "difficulty": "easy",   "grader": "tasks/validity_check/grader.py"},
            {"id": "severity-routing-v1", "difficulty": "medium", "grader": "tasks/severity_routing/grader.py"},
            {"id": "full-triage-v1",      "difficulty": "hard",   "grader": "tasks/full_triage/grader.py"},
        ]
    }

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
