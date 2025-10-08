# EV Operations RAG Chatbot

 This is a minimal Retrieval-Augmented Generation (RAG) chatbot for an electric vehicle monitoring dashboard. It combines a small in-memory knowledge base with Groq LLMs to answer operator questions about fleet health, charging, and efficiency.

## Features

- Flask-powered chat UI tuned for EV operations teams.
- Retrieval over both built-in playbook snippets and any `.txt`, `.md`, or `.json` files you drop into `uploads/`.
- Groq LLM integration with automatic model fallback (`openai/gpt-oss-120b` by default).
- Source tracing in the response payload so you can see which documents informed each answer.

## Prerequisites

- Python 3.9 or newer
- Groq API key with access to Groq text models (e.g., `openai/gpt-oss-120b`, `openai/gpt-oss-20b`)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
# Edit `.env` and set:
#   GROQ_API_KEY=your_secret_value
#   GROQ_MODEL=openai/gpt-oss-120b        # primary text model
#   GROQ_MODEL_FALLBACKS=openai/gpt-oss-20b,openai/qwen-3-32b  # optional comma-separated list
```

### Environment variables

| Variable | Description |
| --- | --- |
| `GROQ_API_KEY` | Required Groq API key with access to the selected models. |
| `GROQ_MODEL` | Preferred Groq model slug (default `openai/gpt-oss-120b`). |
| `GROQ_MODEL_FALLBACKS` | Optional comma-separated list of backup models tried if the primary fails. |

### Add your fleet documents

Drop `.txt`, `.md`, or `.json` files into the `uploads/` directory. The app watches this folder and will automatically index new files the next time you ask a question. If the folder is empty, the built-in EV knowledge base is used as a fallback.

## Run the app

```bash
flask --app app run --debug
```

Open <http://127.0.0.1:5000> in your browser to chat with the assistant. The UI displays the model's answer and the knowledge base entries that were retrieved for context.

## How it works

1. `knowledge_base.py` stores a handful of EV fleet operations insights.
2. `retrieval.py` builds a TF-IDF index and returns the most relevant snippets for each query.
3. `app.py` wraps everything in Flask, builds a prompt that includes the retrieved context, and forwards it to Groq's hosted LLMs (`openai/gpt-oss-120b` by default, with configurable fallbacks).

You can replace the built-in documents with your own EV telemetry summaries or connect the retriever to a database to tailor responses to your fleet.
