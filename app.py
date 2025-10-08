import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from groq import Groq

from document_loader import load_documents
from knowledge_base import DOCUMENTS
from retrieval import RetrievedDocument, SimpleRetriever

load_dotenv()
app = Flask(__name__)

UPLOAD_DIR = Path(os.getenv("UPLOADS_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "openai/gpt-oss-120b"
GROQ_MODEL = os.getenv("GROQ_MODEL", DEFAULT_MODEL)

_retriever_cache: Optional[SimpleRetriever] = None
_cache_state: Tuple[Tuple[str, int, int], ...] = ()


def _scan_upload_state() -> Tuple[Tuple[str, int, int], ...]:
    entries: List[Tuple[str, int, int]] = []
    if not UPLOAD_DIR.exists():
        return tuple(entries)

    for path in UPLOAD_DIR.rglob("*"):
        if not path.is_file():
            continue
        stat = path.stat()
        entries.append((str(path), int(stat.st_mtime_ns), stat.st_size))

    return tuple(sorted(entries))


def _build_retriever() -> SimpleRetriever:
    uploads = load_documents(UPLOAD_DIR)
    documents = DOCUMENTS + uploads if uploads else DOCUMENTS
    return SimpleRetriever(documents)


def get_retriever() -> SimpleRetriever:
    global _retriever_cache, _cache_state
    current_state = _scan_upload_state()
    if _retriever_cache is None or current_state != _cache_state:
        _retriever_cache = _build_retriever()
        _cache_state = current_state
    return _retriever_cache


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("The GROQ_API_KEY environment variable is not set.")
    return Groq(api_key=api_key)


def _normalize_model_slug(text: str) -> str:
    return (
        text.strip()
        .lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .replace("/", "")
    )


def _model_display_name(slug: str) -> str:
    aliases: Dict[str, str] = {
        "openai/gpt-oss-120b": "GPT OSS 120B",
        "openai/gpt-oss-20b": "GPT OSS 20B",
        "openai/qwen-3-32b": "Qwen 3 32B",
        "gpt-oss-120b": "GPT OSS 120B",
        "gpt-oss-20b": "GPT OSS 20B",
        "kimi-k2": "Kimi K2",
        "llama-4-scout": "Llama 4 Scout",
        "llama-3.3-70b": "Llama 3.3 70B",
    }
    normalized = _normalize_model_slug(slug)
    # Normalize alias keys to match normalized slug.
    for key, value in aliases.items():
        if normalized == _normalize_model_slug(key):
            return value
    cleaned = slug.replace("-", " ").replace("_", " ").strip()
    return cleaned.title() if cleaned else slug


def build_prompt(question: str, docs: List[RetrievedDocument]) -> str:
    if docs:
        context_blocks = [
            f"Source {idx + 1} ({doc.doc_id}):\n{doc.text}"
            for idx, doc in enumerate(docs)
        ]
        context = "\n\n".join(context_blocks)
    else:
        context = "No relevant context was retrieved."

    return (
        "You are an assistant for an EV fleet monitoring dashboard. "
        "Use the provided context when possible. "
        "If the answer is not in the context, say you do not have that information.\n\n"
        f"Context:\n{context}\n\n"
        f"User question:\n{question}\n\n"
        "Answer:"
    )


def _get_fallback_models() -> List[str]:
    env_value = os.getenv("GROQ_MODEL_FALLBACKS")
    if env_value:
        return [item.strip() for item in env_value.split(",") if item.strip()]
    return [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "openai/qwen-3-32b",
    ]


def call_llm(prompt: str) -> str:
    client = get_groq_client()
    requested = os.getenv("GROQ_MODEL", GROQ_MODEL)

    tried: set[str] = set()
    last_error: Optional[Exception] = None

    candidate_models = [requested, *_get_fallback_models()]
    for candidate in candidate_models:
        if candidate in tried or not candidate:
            continue
        tried.add(candidate)
        try:
            response = client.chat.completions.create(
                model=candidate,
                messages=[
                    {"role": "system", "content": "You are a concise assistant for EV operations."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=512,
            )
            logging.info("Groq call succeeded with model %s", candidate)
            return response.choices[0].message.content.strip()
        except Exception as exc:  # pragma: no cover - external service failures
            logging.warning("Groq model %s failed: %s", candidate, exc)
            last_error = exc

    raise RuntimeError("Unable to obtain response from Groq models.") from last_error


@app.route("/", methods=["GET"])
def index() -> str:
    model_slug = os.getenv("GROQ_MODEL", GROQ_MODEL)
    return render_template(
        "index.html",
        model_display=_model_display_name(model_slug),
    )


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    try:
        retrieved_docs = get_retriever().fetch_top_k(question, k=3)
    except Exception as exc:  # pragma: no cover - initialization failures
        logging.exception("retrieval failure")
        return jsonify({"error": "retrieval error", "details": str(exc)}), 500

    prompt = build_prompt(question, retrieved_docs)

    try:
        answer = call_llm(prompt)
    except Exception as exc:  # pragma: no cover - external service failure
        logging.exception("groq call failed")
        return jsonify({"error": "llm_error", "details": str(exc)}), 502

    sources = [
        {"id": doc.doc_id, "score": doc.score, "tags": list(doc.tags)}
        for doc in retrieved_docs
    ]

    return jsonify({"answer": answer, "sources": sources})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
