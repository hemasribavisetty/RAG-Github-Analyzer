import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.errors import BadRequestError, HfHubHTTPError

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    raise RuntimeError("HF_API_KEY not set in environment or .env")

# 🔹 Chat model – use the one you already tested and know works
CHAT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"  # this is from your working script

# 🔹 Embedding model – standard sentence-transformers model
EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Chat client (OpenAI-style)
chat_client = InferenceClient(api_key=HF_API_KEY)

# Embedding client (normal HF inference)
embed_client = InferenceClient(model=EMBED_MODEL, token=HF_API_KEY)


def embed_texts(texts):
    """
    Takes a list of strings and returns a list of embedding vectors.
    Uses HF feature_extraction on the embeddings model.
    """
    embeddings = []
    for t in texts:
        emb = embed_client.feature_extraction(t)
        # emb can be [dim] or [[dim]]
        if isinstance(emb[0], list):
            embeddings.append(emb[0])
        else:
            embeddings.append(emb)
    return embeddings


def generate_text(prompt: str, max_new_tokens: int = 600) -> str:
    """
    Uses the OpenAI-style chat.completions.create interface via huggingface_hub.
    This matches exactly how you tested your key and model.
    """
    messages = [
        {"role": "system", "content": "You are a helpful codebase explanation assistant."},
        {"role": "user", "content": prompt},
    ]

    try:
        response = chat_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=max_new_tokens,
        )

        if not response.choices:
            return "[LLM error: no choices returned]"

        # Same pattern you used in your test script
        return response.choices[0].message["content"]

    except (BadRequestError, HfHubHTTPError) as e:
        # Show a readable error in the UI instead of crashing
        return f"[LLM error: {e}]"
    except Exception as e:
        return f"[Unexpected LLM error: {e}]"
