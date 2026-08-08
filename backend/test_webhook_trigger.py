import hmac, hashlib, json, os, sys
import httpx
from dotenv import load_dotenv
load_dotenv()

SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

def send_fake_event(repo: str, run_id: int, run_url: str, workflow_name: str = "CI"):
    payload = {
        "action": "completed",
        "workflow_run": {"id": run_id, "html_url": run_url, "name": workflow_name, "conclusion": "failure"},
        "repository": {"full_name": repo}
    }
    body = json.dumps(payload).encode()
    sig = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    resp = httpx.post(
        "http://localhost:8000/webhook/github",
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig}
    )
    print(resp.status_code, resp.text)

if __name__ == "__main__":
    repo = sys.argv[1]
    run_id = int(sys.argv[2])
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
    send_fake_event(repo, run_id, run_url)
