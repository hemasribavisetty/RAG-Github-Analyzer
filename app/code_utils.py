import os
import tempfile
from typing import List, Dict
from git import Repo

CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb"}

def clone_repo(repo_url: str) -> str:
    tmp_dir = tempfile.mkdtemp(prefix="repo_")
    Repo.clone_from(repo_url, tmp_dir)
    return tmp_dir

def list_code_files(root_dir: str) -> List[Dict]:
    files_info = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            ext = os.path.splitext(fname)[1]
            if ext.lower() in CODE_EXTENSIONS:
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, root_dir)
                files_info.append({
                    "relative_path": rel_path,
                    "full_path": full_path,
                    "extension": ext.lower(),
                })
    return files_info
