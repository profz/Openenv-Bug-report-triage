import gradio as gr
import json
from pathlib import Path
from env.bugreport_env import BugReportEnv
from tasks.validity_check.grader import score_action
from agents.random_agent import act as random_act

def run_demo(agent_choice: str):
    env = BugReportEnv("tasks/validity_check/reports.json", grader_fn=score_action)
    obs = env.reset(seed=42)
    done = False
    log = []

    while not done:
        action = random_act(obs)   # always random in demo — no API key needed
        obs, reward, done, _ = env.step(action)
        s = env.state()
        log.append(
            f"[{s['index']:02d}/{s['total']}] "
            f"verdict={action.verdict} severity={action.severity} "
            f"team={action.team} | {reward.explanation} | score={reward.score:.3f}"
        )

    final = env.state()["mean_reward"]
    log.append(f"\nFinal mean score: {final:.3f}")
    return "\n".join(log)

def show_scores():
    p = Path("results/baseline_scores.json")
    if p.exists():
        data = json.loads(p.read_text())
        rows = [[k, f"{v:.3f}"] for k, v in data["scores"].items()]
        return rows
    return [["validity-check-v1", "run baseline.py first"]]

def show_yaml():
    return Path("openenv.yaml").read_text()

with gr.Blocks(title="OpenEnv Bug Triage") as demo:
    gr.Markdown("# OpenEnv — Bug Report Triage Environment")
    gr.Markdown("Real-world AI agent environment: triage GitHub bug reports with scores 0.0–1.0")

    with gr.Tab("Live Demo (Random Agent)"):
        btn = gr.Button("Run Episode", variant="primary")
        out = gr.Textbox(label="Episode Log", lines=30, interactive=False)
        btn.click(fn=run_demo, inputs=gr.Textbox(visible=False, value="random"), outputs=out)

    with gr.Tab("Baseline Scores"):
        gr.Dataframe(
            value=show_scores,
            headers=["Task", "Score"],
            label="Baseline Results",
        )

    with gr.Tab("openenv.yaml"):
        gr.Code(value=show_yaml, language="yaml")

if __name__ == "__main__":
    demo.launch()
