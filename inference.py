import os
import json
from openai import OpenAI
from env.bugreport_env import BugReportEnv
from models import BugAction
from graders import score_action

API_BASE_URL = os.getenv("API_BASE_URL", "<your-api-base-url>")
MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "placeholder")

PROMPT = """Triage this bug report. Respond ONLY with JSON.

Title: {title}
Repo: {repo}
Body: {body}

{{"verdict": "valid"|"duplicate"|"needs-info"|"wontfix", "severity": "critical"|"high"|"medium"|"low", "team": "frontend"|"backend"|"infra"|"docs"|"security", "needs_repro": true|false}}"""

NULL_ACTION = {"verdict": "needs-info", "severity": "low", "team": "backend", "needs_repro": True}

def act(obs):
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": PROMPT.format(
                title=obs.title, repo=obs.repo, body=obs.body[:600]
            )}],
            response_format={"type": "json_object"},
            max_tokens=120,
            temperature=0.0,
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"[error] {e}", flush=True)
        return NULL_ACTION

def run_task(task_id, task_path):
    def grader_fn(action, gt):
        return score_action(action, gt, task_id)

    env = BugReportEnv(task_path, grader_fn=grader_fn)
    obs = env.reset(seed=42)
    done = False
    step = 0

    print(f"[START] task={task_id}", flush=True)

    while not done:
        action_dict = act(obs)
        action = BugAction(**action_dict)
        obs, reward, done, _ = env.step(action)
        step += 1
        print(f"[STEP] step={step} reward={reward.score:.3f}", flush=True)

    final = env.state()["mean_reward"]
    print(f"[END] task={task_id} score={final:.3f} steps={step}", flush=True)
    return final

if __name__ == "__main__":
    from tasks import TASKS
    results = {}
    for task in TASKS:
        results[task["id"]] = run_task(task["id"], task["dataset"])

    os.makedirs("results", exist_ok=True)
    with open("results/baseline_scores.json", "w") as f:
        json.dump({"agent": "llm", "scores": results}, f, indent=2)
