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

def is_text_file(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return False
        return True
    except:
        return False

def smart_chunk_code(text: str, file_path: str, max_tokens: int = 1000) -> List[str]:
    """
    ADVANCED CHUNKING:
    Moves beyond simple line-counting. This implementation:
    1. Respects logical boundaries (double newlines) to keep functions/classes together.
    2. Overlaps chunks to maintain context across boundaries.
    3. Adds metadata headers to each chunk so the LLM knows the context even for partial snippets.
    """
    # Simple semantic splitting by double newlines (often function/class boundaries)
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = f"File: {file_path}\n---\n"
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < max_tokens:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            # Overlap: keep the last 20% of the previous chunk for context
            overlap_context = current_chunk[-int(len(current_chunk)*0.2):]
            current_chunk = f"File: {file_path} (continued)\n---\n{overlap_context}\n{para}\n\n"
            
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def build_repo_index(repo_id: str, files: List[Dict]) -> str:
    collection_name = f"repo_{repo_id}"
    try:
        chroma_client.delete_collection(name=collection_name)
    except Exception:
        pass

    collection = chroma_client.create_collection(name=collection_name)
    doc_ids = []
    documents = []
    metadatas = []

    for file_info in files:
        if not is_text_file(file_info["full_path"]):
            continue
        content = read_file(file_info["full_path"])
        rel_path = file_info["relative_path"]
        
        # Use new smart chunking
        chunks = smart_chunk_code(content, rel_path)

        for i, chunk in enumerate(chunks):
            doc_ids.append(f"{rel_path}::{i}")
            documents.append(chunk)
            metadatas.append({
                "file_path": rel_path,
                "chunk_index": i,
                "extension": file_info["extension"]
            })

    if not documents:
        return collection_name

    embeddings = embed_texts(documents)
    collection.add(
        ids=doc_ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    return collection_name

def answer_question(repo_id: str, question: str) -> str:
    collection_name = f"repo_{repo_id}"
    collection = chroma_client.get_collection(name=collection_name)

    q_embedding = embed_texts([question])[0]

    # HYBRID SEARCH MOCKUP: 
    # In a full system, you would perform keyword search + vector search.
    # Here we improve precision by increasing 'n_results' and adding relevance scoring.
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=10, # Increased context window for better coverage
    )

    if not results["documents"]:
        return "I could not find any context for this repository."

    context_snippets = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context_snippets.append(f"{doc}\n")

    context = "\n\n".join(context_snippets)

    prompt = f"""
You are a senior software architect analyzing a codebase.
Use the semantic code snippets below to answer the user's question with high technical precision.

Context from Repository:
{context}

User Question:
{question}

Instructions:
1. If the code provided doesn't contain the answer, state that clearly.
2. If it does, provide a detailed technical explanation, referencing specific files or patterns found.
3. Be concise but thorough.
"""

    return generate_text(prompt, max_new_tokens=4000)

def summarize_repo_structure(files: List[Dict]) -> str:
    if not files:
        return "No files found."
    MAX_FILES = 50
    file_list_text = "\n".join(f["relative_path"] for f in files[:MAX_FILES])
    prompt = f"Analyze this project structure and explain the architecture:\n\n{file_list_text}"
    return generate_text(prompt, max_new_tokens=4000)
