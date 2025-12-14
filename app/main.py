from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .code_utils import clone_repo, list_code_files

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "analysis": None}
    )

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_repo(request: Request, repo_url: str = Form(...)):
    repo_path = clone_repo(repo_url)
    files = list_code_files(repo_path)

    # Simple text summary for now
    tree_lines = [f["relative_path"] for f in files]
    tree_text = "\n".join(tree_lines)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "analysis": f"Cloned repo to: {repo_path}\n\nCode files:\n{tree_text}"
        }
    )
