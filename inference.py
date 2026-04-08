import os
import json
from openai import OpenAI
from env.bugreport_env import BugReportEnv
from env.models import Action
from tasks.validity_check.grader import score_action

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
        return Action(**json.loads(resp.choices[0].message.content))
    except Exception as e:
        print(f"[error] {e}")
        return Action(verdict="needs-info", severity="low", team="backend", needs_repro=True)

if __name__ == "__main__":
    env = BugReportEnv("tasks/validity_check/reports.json", grader_fn=score_action)
    obs = env.reset(seed=42)
    done = False
    step = 0

    print("START")

    while not done:
        action = act(obs)
        obs, reward, done, _ = env.step(action)
        step += 1
        print(f"STEP {step} score={reward.score:.3f} {reward.explanation}")

    final = env.state()["mean_reward"]
    print(f"END score={final:.3f}")
