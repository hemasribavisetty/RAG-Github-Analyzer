# RAG GitHub Repository Analyzer  

## LIVE: https://rag-github-analyzer.onrender.com/

## Overview
The RAG GitHub Analyzer is an advanced, interactive, and asynchronous tool designed to help users better understand GitHub repositories by leveraging **Retrieval-Augmented Generation (RAG)** techniques. It is built to analyze repositories, understand their structure, and answer user questions in real-time. By combining powerful backend code with a fast and intuitive interface, the tool allows users to explore and comprehend the contents of any GitHub repository efficiently.

## Core Architecture
The system is built as a distributed application to handle time-intensive tasks like cloning, parsing, and indexing without blocking the main web interface.

*   **FastAPI Backend**: Serves as the web interface and provides the REST and WebSocket API.
*   **Asynchronous Processing**: Uses **Redis** as a message broker and **RQ (Redis Queue)** to manage background worker processes for repository analysis.
*   **Real-time Communication**: Employs **WebSockets** to provide live, step-by-step progress updates to the user as the repository is processed.
*   **ChromaDB**: Utilizes this vector database for storing and efficiently querying semantic embeddings of repository code and documentation.

## Key Features

1.  **Asynchronous Repository Analysis**:
    - Users provide a GitHub URL, and the system offloads the analysis to background workers, keeping the UI responsive.
    - Status updates are streamed directly to the user via WebSockets.
2.  **Interactive Chatbot**:
    - Users can ask specific questions about the codebase. The system retrieves relevant code snippets using semantic search (RAG) and generates context-aware answers.
3.  **Repository Indexing & Search**:
    - Uses **Chroma** to index repository content, allowing for fast, semantic-based retrieval of information.
    - Automatically identifies important files and project structure.
4.  **Backend Efficiency**:
    - Built with **FastAPI** for high performance.
    - Uses **GitPython** for repository management and **Hugging Face** models for generating vector embeddings.

## Technical Stack

- **Backend**: Python, FastAPI
- **Task Queue**: Redis, RQ (Redis Queue)
- **Vector Database**: ChromaDB
- **Frontend**: HTML, Jinja2, CSS, JavaScript (WebSockets)
- **Code Analysis**: GitPython
- **Deployment**: Optimized for cloud platforms (e.g., Render)

## How It Works

1.  **Enqueueing**: When a repository URL is submitted, FastAPI creates a background job and starts a WebSocket stream.
2.  **Background Processing**:
    - **Cloning**: The worker clones the repository using `GitPython`.
    - **Parsing**: The worker analyzes the file structure.
    - **Indexing**: Content is chunked and embedded using Hugging Face models, then stored in **Chroma**.
3.  **Live Interaction**: Users can then ask questions, which are answered by retrieving context from the Chroma index and passing it to a language model for generation.
