#!/usr/bin/env python3
"""
Baseline inference script.
Usage:
  OPENAI_API_KEY=sk-... python scripts/baseline.py
  OPENAI_API_KEY=sk-... python scripts/baseline.py --agent random
"""
import os
import json
import argparse
from pathlib import Path

def run(agent_type: str = "llm"):
    from env.bugreport_env import BugReportEnv
    from tasks.validity_check.grader import score_action

    tasks = [
        {
            "id": "validity-check-v1",
            "path": "tasks/validity_check/reports.json",
            "grader": score_action,
        }
    ]

    if agent_type == "llm":
        if not os.environ.get("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY not set")
        from agents.llm_agent import act
    else:
        from agents.random_agent import act

    all_results = {}

    for task in tasks:
        print(f"\n{'─'*50}")
        print(f"Task: {task['id']}  agent: {agent_type}")
        print(f"{'─'*50}")

        env = BugReportEnv(task["path"], grader_fn=task["grader"])
        obs = env.reset(seed=42)
        done = False

        while not done:
            action = act(obs)
            obs, reward, done, _ = env.step(action)
            s = env.state()
            print(f"  [{s['index']:02d}/{s['total']}] {reward.explanation}  score={reward.score:.3f}")

        final = env.state()["mean_reward"]
        print(f"\n  ✓ {task['id']}: {final:.3f}")
        all_results[task["id"]] = final

    Path("results").mkdir(exist_ok=True)
    out = Path("results/baseline_scores.json")
    out.write_text(json.dumps({"agent": agent_type, "scores": all_results}, indent=2))
    print(f"\nSaved → {out}")
    return all_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=["llm", "random"], default="llm")
    args = parser.parse_args()
    run(args.agent)
