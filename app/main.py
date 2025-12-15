import hashlib
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .code_utils import clone_repo, list_code_files
from .rag_index import build_repo_index, answer_question, summarize_repo_structure

app = FastAPI()
@app.get("/ping")
async def ping():
    return {"status": "ok"}

templates = Jinja2Templates(directory="app/templates")

# Simple in memory store
REPO_STATE = {}


def repo_id_from_url(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "analysis": None,
            "repo_id": None,
            "repo_url": None,
        },
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze_repo(request: Request, repo_url: str = Form(...)):
    rid = repo_id_from_url(repo_url)

    repo_path = clone_repo(repo_url)
    files = list_code_files(repo_path)

    build_repo_index(rid, files)
    structure_summary = summarize_repo_structure(files)

    REPO_STATE[rid] = {
        "repo_url": repo_url,
        "files": files,
        "structure_summary": structure_summary,
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "analysis": structure_summary,
            "repo_id": rid,
            "repo_url": repo_url,
        },
    )


@app.post("/ask", response_class=HTMLResponse)
async def ask_about_repo(
    request: Request,
    repo_id: str = Form(...),
    question: str = Form(...),
):
    answer = answer_question(repo_id, question)
    repo_data = REPO_STATE.get(repo_id)
    repo_url = repo_data["repo_url"] if repo_data else "Unknown"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "analysis": answer,
            "repo_id": repo_id,
            "repo_url": repo_url,
        },
    )
