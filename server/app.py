import uvicorn
from openenv.core import create_app
from server.environment import BugTriageEnvironment, BugAction, BugObservation

app = create_app(
    env=BugTriageEnvironment,
    action_cls=BugAction,
    observation_cls=BugObservation,
    env_name="openenv-bug-triage",
)

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
