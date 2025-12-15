import os
from typing import List, Dict

import chromadb

from chromadb.config import Settings

from .config import embed_texts, generate_text

# Chroma client, persisted to ./chroma_db
chroma_client = chromadb.PersistentClient(path="./chroma_db")


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def chunk_text(text: str, max_lines: int = 120) -> List[str]:
    """
    Simple line-based chunking. You can improve this later to be token-based.
    """
    lines = text.splitlines()
    chunks = []
    current = []

    for line in lines:
        current.append(line)
        if len(current) >= max_lines:
            chunks.append("\n".join(current))
            current = []

    if current:
        chunks.append("\n".join(current))

    return chunks


def build_repo_index(repo_id: str, files: List[Dict]) -> str:
    """
    Build or rebuild a Chroma collection for a repo.
    repo_id: unique id string for the repo
    files: list of file metadata from list_code_files
    """
    collection_name = f"repo_{repo_id}"

    # Remove existing collection if any
    try:
        chroma_client.delete_collection(name=collection_name)
    except Exception:
        pass

    collection = chroma_client.create_collection(name=collection_name)

    doc_ids = []
    documents = []
    metadatas = []

    for file_info in files:
        content = read_file(file_info["full_path"])
        chunks = chunk_text(content, max_lines=120)
        rel_path = file_info["relative_path"]

        for i, chunk in enumerate(chunks):
            doc_ids.append(f"{rel_path}::{i}")
            documents.append(chunk)
            metadatas.append(
                {
                    "file_path": rel_path,
                    "chunk_index": i,
                }
            )

    if not documents:
        return collection_name

    # Get embeddings using Hugging Face
    embeddings = embed_texts(documents)

    collection.add(
        ids=doc_ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    # No need to call persist() with PersistentClient
    return collection_name


def answer_question(repo_id: str, question: str) -> str:
    """
    Use RAG: embed the question, retrieve relevant chunks from Chroma,
    and feed them to the LLM.
    """
    collection_name = f"repo_{repo_id}"
    collection = chroma_client.get_collection(name=collection_name)

    # Embed the question
    q_embedding = embed_texts([question])[0]

    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=6,
    )

    if not results["documents"]:
        return "I could not find any context for this repository."

    context_snippets = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context_snippets.append(
            f"File: {meta['file_path']} (chunk {meta['chunk_index']})\n{doc}\n"
        )

    context = "\n\n".join(context_snippets)

    prompt = f"""
You are a codebase assistant for students.
Use only the context from the repository below to answer the question.
If the answer is not in the context, say you do not know.

Context:
{context}

Question:
{question}

Answer clearly and mention file paths when helpful.
"""

    answer = generate_text(prompt)
    return answer

def summarize_repo_structure(files: List[Dict]) -> str:
    """
    Take the list of code files and ask the LLM to infer the architecture.
    We limit to the first N files to keep the prompt small.
    """
    if not files:
        return "No code files found in this repository."

    # Limit to first 40 files to avoid giant prompts
    MAX_FILES = 40
    limited_files = files[:MAX_FILES]

    file_list_text = "\n".join(f["relative_path"] for f in limited_files)

    prompt = f"""
You are analyzing a project's code structure for a student.

Here is a (possibly partial) list of code files in the project (up to {MAX_FILES} files):

{file_list_text}

Tasks:
1. Group files into logical areas like API, models, UI, utils, configuration, etc.
2. Explain what each group probably does in simple language.
3. Point out likely entry points such as main.py, app.py, index.js, server.js, etc.
4. Tell a new contributor where they should start reading the code to understand:
   - how the app starts
   - where the core logic lives
   - where configuration lives
5. Always reference file paths explicitly when you mention them.

If you feel some parts are missing because not all files are shown, state that clearly.
"""

    print(">>> Calling HF generate_text for summarize_repo_structure", flush=True)
    summary = generate_text(prompt, max_new_tokens=500)
    print(">>> HF generate_text returned for summarize_repo_structure", flush=True)
    return summary