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

@app.get("/graders")
def list_graders():
    from tasks.validity_check.grader import grade as g1
    from tasks.severity_routing.grader import grade as g2
    from tasks.full_triage.grader import grade as g3
    return {
        "graders": [
            {"task_id": "validity-check-v1",   "callable": "tasks.validity_check.grader.grade",   "ready": callable(g1)},
            {"task_id": "severity-routing-v1", "callable": "tasks.severity_routing.grader.grade", "ready": callable(g2)},
            {"task_id": "full-triage-v1",      "callable": "tasks.full_triage.grader.grade",      "ready": callable(g3)},
        ]
    }
