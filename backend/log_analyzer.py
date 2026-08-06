from dotenv import load_dotenv
load_dotenv()

import os
import httpx
from groq import Groq

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
client = Groq()  # reads GROQ_API_KEY from env

async def fetch_run_log(repo: str, run_id: int) -> str:
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}

    async with httpx.AsyncClient() as http:
        resp = await http.get(url, headers=headers)
        resp.raise_for_status()
        jobs = resp.json()["jobs"]

    failed_steps = []
    for job in jobs:
        for step in job.get("steps", []):
            if step.get("conclusion") == "failure":
                failed_steps.append(f"Job: {job['name']} | Step: {step['name']}")

    return "\n".join(failed_steps) or "No step-level detail available."

async def analyze_failure(repo: str, run_id: int) -> str:
    log_snippet = await fetch_run_log(repo, run_id)

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                "You are a CI/CD assistant. Given this failed GitHub Actions run detail, "
                "summarize the likely root cause in 2-3 sentences, plain English, "
                "for a developer who wants a quick read before digging into full logs:\n\n"
                f"{log_snippet}"
            )
        }]
    )
    return completion.choices[0].message.content
