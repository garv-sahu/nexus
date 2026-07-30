"""
NEXUS — Web Agent : Flask backend template
--------------------------------------------------
Serves the single-page UI (templates/index.html) and exposes three
endpoints for the frontend to call. Wire the marked sections up to
your existing agent (Ollama + Playwright/CDP browser control).

Run:
    pip install flask
    python app.py
"""

from flask import Flask, render_template, request, jsonify, Response
import json
from agent.chat import Nexus

app = Flask(__name__)

agent = Nexus()

# ------------------------------------------------------------------
# CONFIG — adjust to match your setup
# ------------------------------------------------------------------

OLLAMA_HOST = "http://localhost:11434"

# ------------------------------------------------------------------
# PAGE
# ------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------------------------------------------
# GET /api/models — list models available in Ollama
# ------------------------------------------------------------------
@app.route("/api/models")
def get_models():
    try:
        import requests
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        r.raise_for_status()
        tags = r.json().get("models", [])
        models = [{"name": m["name"], "tag": _size_label(m)} for m in tags]
    except Exception:
        # Fallback if Ollama isn't reachable — keeps the UI usable
        models = [
            {"name": "gemma4:8b", "tag": "local"},
            {"name": "qwen3:8b", "tag": "local"},
            {"name": "llama3.1:8b", "tag": "local"},
        ]

    return jsonify({
        "models": models,
        "active": agent.get_model()
    })


def _size_label(model_obj):
    size_bytes = model_obj.get("size", 0)
    if not size_bytes:
        return "local"
    gb = size_bytes / (1024 ** 3)
    return f"{gb:.1f}GB"


# ------------------------------------------------------------------
# POST /api/switch-model — set the active model for future turns
# ------------------------------------------------------------------
@app.route("/api/switch-model", methods=["POST"])
def switch_model():
    data = request.get_json(force=True) or {}
    model = data.get("model")
    if not model:
        return jsonify({"error": "model is required"}), 400

    agent.set_model(model)
    # TODO: if your agent keeps its own LLM handle (e.g. a LangGraph
    # node bound to a specific model), update it here too.

    return jsonify({
        "ok": True,
        "active": agent.get_model()
    })


# ------------------------------------------------------------------
# POST /api/chat — main entry point the console UI calls
#
# The frontend expects a streamed, plain-text chunked response body
# (it reads res.body via a ReadableStream). Replace the generator
# below with calls into your existing agent:
#   1. Parse the user's command / intent
#   2. Drive the browser via Playwright connected over CDP
#   3. Stream back partial results / the model's reasoning
# ------------------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    message = data.get("message", "")
    # model = data.get("model", STATE["active_model"])

    try:
        response = agent.chat(message)

        return Response(
            response,
            mimetype="text/plain"
        )
    except Exception as e:
        return Response(
            f"Error: {str(e)}",
            status=500,
            mimetype="text/plain"
        )


if __name__ == "__main__":
    app.run(debug=True, port=5000)