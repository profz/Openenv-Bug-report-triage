import json
from openai import OpenAI
from env.models import Action, Observation

client = OpenAI()

SYSTEM = """You are a senior open-source maintainer triaging bug reports.
Respond ONLY with a JSON object — no explanation, no markdown."""

PROMPT = """Triage this bug report:

Title: {title}
Repo: {repo}
Author: {author}
Labels: {labels}
Body: {body}

Respond with exactly:
{{
  "verdict": "valid" | "duplicate" | "needs-info" | "wontfix",
  "severity": "critical" | "high" | "medium" | "low",
  "team": "frontend" | "backend" | "infra" | "docs" | "security",
  "needs_repro": true | false
}}"""

NULL_ACTION = Action(verdict="needs-info", severity="low", team="backend", needs_repro=True)

def act(obs: Observation, model: str = "gpt-4o-mini") -> Action:
    body = obs.body[:600] + "..." if len(obs.body) > 600 else obs.body
    prompt = PROMPT.format(
        title=obs.title, repo=obs.repo, author=obs.author,
        labels=", ".join(obs.labels) or "none", body=body,
    )
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=120,
            temperature=0.0,
        )
        return Action(**json.loads(resp.choices[0].message.content))
    except Exception as e:
        print(f"  [llm error] {e}")
        return NULL_ACTION
