from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
    # For now, just echo it back
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "analysis": f"Got repo URL: {repo_url}"}
    )
