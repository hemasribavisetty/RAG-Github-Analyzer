import os
import tempfile
from typing import List, Dict

from git import Repo


def clone_repo(repo_url: str) -> str:
    tmp_dir = tempfile.mkdtemp(prefix="repo_")
    Repo.clone_from(repo_url, tmp_dir)
    return tmp_dir


def list_repo_files(root_dir: str) -> List[Dict]:
    files_info = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip .git directory
        if '.git' in dirnames:
            dirnames.remove('.git')
        for fname in filenames:
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, root_dir)
            ext = os.path.splitext(fname)[1].lower()
            files_info.append(
                {
                    "relative_path": rel_path,
                    "full_path": full_path,
                    "extension": ext,
                }
            )
    return files_info


def get_repo_structure(root_dir: str) -> str:
    """Generate a string representation of the directory structure."""
    def build_tree(path, prefix=""):
        items = []
        try:
            entries = sorted(os.listdir(path))
            # Exclude .git directory
            entries = [e for e in entries if e != '.git']
        except PermissionError:
            return ""
        
        for i, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            items.append(f"{prefix}{connector}{entry}")
            
            if os.path.isdir(full_path):
                extension = "    " if is_last else "│   "
                items.append(build_tree(full_path, prefix + extension))
        
        return "\n".join(items)
    
    return build_tree(root_dir)
