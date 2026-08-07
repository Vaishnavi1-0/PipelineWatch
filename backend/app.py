from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
import hmac, hashlib, os
from dotenv import load_dotenv
from log_analyzer import analyze_failure
from models import init_db, save_failure, get_failures

load_dotenv()

app = FastAPI(title="PipelineWatch")
templates = Jinja2Templates(directory="templates")

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

@app.on_event("startup")
def on_startup():
    init_db()

def verify_signature(payload_body: bytes, signature_header: str):
    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing signature")
    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail="Invalid signature")

@app.post("/webhook/github")
async def github_webhook(request: Request):
    body = await request.body()
    verify_signature(body, request.headers.get("X-Hub-Signature-256", ""))

    payload = await request.json()

    if payload.get("action") != "completed":
        return {"status": "ignored"}

    run = payload.get("workflow_run", {})
    if run.get("conclusion") != "failure":
        return {"status": "ignored, not a failure"}

    repo = payload["repository"]["full_name"]
    run_id = run["id"]
    run_url = run["html_url"]
    workflow_name = run["name"]

    summary = await analyze_failure(repo, run_id)

    save_failure(
        repo=repo,
        run_id=run_id,
        workflow_name=workflow_name,
        run_url=run_url,
        summary=summary,
    )

    return {"status": "analyzed", "summary": summary}

@app.get("/failures")
def list_failures():
    return get_failures()

@app.get("/dashboard")
def dashboard(request: Request):
    failures = get_failures()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "failures": failures}
    )
