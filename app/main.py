import hashlib
import json
import asyncio
import requests
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from rq.job import Job

from .code_utils import list_repo_files, get_repo_structure
from .rag_index import answer_question, summarize_repo_structure
from .worker_tasks import enqueue_repo_analysis, redis_conn

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

# Simple in memory store for session data
REPO_STATE = {}

# Manager to keep track of active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, repo_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[repo_id] = websocket

    def disconnect(self, repo_id: str):
        if repo_id in self.active_connections:
            del self.active_connections[repo_id]

    async def send_update(self, repo_id: str, message: str):
        if repo_id in self.active_connections:
            await self.active_connections[repo_id].send_text(json.dumps({"status": "update", "message": message}))

manager = ConnectionManager()

def repo_id_from_url(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "analysis": None,
            "repo_id": None,
            "repo_url": None,
            "chat_history": [],
            "job_id": None
        },
    )

@app.websocket("/ws/{repo_id}")
async def websocket_endpoint(websocket: WebSocket, repo_id: str):
    await manager.connect(repo_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(repo_id)

@app.post("/analyze-progress/{repo_id}")
async def report_progress(repo_id: str, data: dict):
    """Internal endpoint for workers to report progress to the UI via websocket."""
    await manager.send_update(repo_id, data.get("message", ""))
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_repo(request: Request, repo_url: str = Form(...)):
    rid = repo_id_from_url(repo_url)
    job_id = enqueue_repo_analysis(repo_url, rid)

    REPO_STATE[rid] = {
        "repo_url": repo_url,
        "chat_history": [],
        "job_id": job_id
    }

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "analysis": f"Analysis started. Connecting to live stream...",
            "repo_id": rid,
            "repo_url": repo_url,
            "job_id": job_id,
            "chat_history": [],
        },
    )

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return {
            "job_id": job_id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None
        }
    except Exception as e:
        return JSONResponse(status_code=404, content={"error": str(e)})

@app.post("/ask")
async def ask_about_repo(
    request: Request,
    repo_id: str = Form(...),
    question: str = Form(...),
):
    answer = answer_question(repo_id, question)
    repo_data = REPO_STATE.get(repo_id)
    if repo_data:
        repo_data["chat_history"].append({"question": question, "answer": answer})
    
    repo_url = repo_data["repo_url"] if repo_data else "Unknown"
    chat_history = repo_data.get("chat_history", []) if repo_data else []

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "analysis": answer,
            "repo_id": repo_id,
            "repo_url": repo_url,
            "chat_history": chat_history,
        },
    )
