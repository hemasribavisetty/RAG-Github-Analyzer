import requests
from redis import Redis
from rq import Queue
from .rag_index import build_repo_index
from .code_utils import clone_repo, list_repo_files

# Initialize Redis connection
redis_conn = Redis(host='localhost', port=6379)
task_queue = Queue('repo_analysis', connection=redis_conn)

def notify_progress(rid: str, message: str):
    """
    Helper to send progress updates back to the FastAPI websocket manager via HTTP.
    In a real AWS deployment, you might use a shared Redis Pub/Sub instead.
    """
    try:
        # Assuming local execution; workers call the internal progress endpoint
        requests.post(f"http://localhost:8000/analyze-progress/{rid}", json={"message": message})
    except:
        pass

def enqueue_repo_analysis(repo_url: str, rid: str):
    job = task_queue.enqueue(perform_analysis, repo_url, rid)
    return job.id

def perform_analysis(repo_url: str, rid: str):
    notify_progress(rid, "🚀 Worker started: Initializing environment...")
    
    notify_progress(rid, "📂 Cloning repository from GitHub...")
    repo_path = clone_repo(repo_url)
    
    notify_progress(rid, "🔍 Parsing file structure and preparing chunks...")
    files = list_repo_files(repo_path)
    
    notify_progress(rid, "🧠 Building semantic index (Vector Embeddings)... This may take a moment.")
    build_repo_index(rid, files)
    
    notify_progress(rid, "✅ Analysis complete! Ready for your questions.")
    return {"status": "complete", "repo_id": rid}
