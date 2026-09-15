from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests
import os
import time

load_dotenv()

app = Flask(__name__)

OPENAI_KEY = os.getenv("OPENAI_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY", "")
THIRD_KEY = os.getenv("THIRD_KEY", "")


def try_openai(message):
    if not OPENAI_KEY:
        return None, "OpenAI key not configured"

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are REX, a helpful AI assistant. "
                            "You can communicate clearly and naturally. "
                            "You may use Nigerian Pidgin when appropriate."
                        )
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "max_tokens": 1200,
                "temperature": 0.7
            },
            timeout=30
        )

        if response.ok:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            return answer, "OpenAI ✅"

        return None, f"OpenAI HTTP {response.status_code}"

    except requests.RequestException as error:
        return None, f"OpenAI error: {error}"


def try_anthropic(message):
    if not ANTHROPIC_KEY:
        return None, "Claude key not configured"

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1200,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            },
            timeout=30
        )

        if response.ok:
            data = response.json()
            answer = data["content"][0]["text"]
            return answer, "Claude ✅"

        return None, f"Claude HTTP {response.status_code}"

    except requests.RequestException as error:
        return None, f"Claude error: {error}"


def local_fallback(message):
    lower = message.lower()

    if "how are you" in lower:
        return (
            "I dey kampe! 🤖💚 REX is online and ready to help you.",
            "Local Brain ✅"
        )

    if "who are you" in lower or "your name" in lower:
        return (
            "Na me be REX 🤖 — your AI assistant. "
            "I can chat, generate images, generate videos, "
            "search, research and help you code.",
            "Local Brain ✅"
        )

    return (
        "REX's online AI providers are currently unavailable. "
        "But the local fallback is still running. 🔧",
        "Local Fallback ✅"
    )


def smart_chat(message):
    logs = []

    start = time.time()

    answer, status = try_openai(message)
    logs.append(f"Provider 1 — {status}")

    if answer:
        logs.append(f"Completed in {time.time() - start:.2f}s")
        return answer, logs

    answer, status = try_anthropic(message)
    logs.append(f"Provider 2 — {status}")

    if answer:
        logs.append(f"Completed in {time.time() - start:.2f}s")
        return answer, logs

    answer, status = local_fallback(message)
    logs.append(f"Provider 3 — {status}")
    logs.append(f"Completed in {time.time() - start:.2f}s")

    return answer, logs


@app.route("/")
def home():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    answer, logs = smart_chat(message)

    return jsonify({
        "reply": answer,
        "logs": logs
    })


@app.post("/api/image")
def generate_image():
    prompt = (request.get_json(silent=True) or {}).get("message", "").strip()

    if not prompt:
        return jsonify({"error": "Image prompt is required."}), 400

    # Real image-generation API will be connected here.
    return jsonify({
        "type": "image",
        "status": "ready",
        "prompt": prompt,
        "message": "Image generation endpoint is ready for the image provider."
    })


@app.post("/api/video")
def generate_video():
    prompt = (request.get_json(silent=True) or {}).get("message", "").strip()

    if not prompt:
        return jsonify({"error": "Video prompt is required."}), 400

    # Real video-generation API will be connected here.
    return jsonify({
        "type": "video",
        "status": "ready",
        "prompt": prompt,
        "message": "Video generation endpoint is ready for the video provider."
    })


@app.post("/api/search")
def search():
    query = (request.get_json(silent=True) or {}).get("message", "").strip()

    if not query:
        return jsonify({"error": "Search query is required."}), 400

    return jsonify({
        "type": "search",
        "message": "Search engine integration comes next.",
        "query": query
    })


@app.post("/api/research")
def research():
    query = (request.get_json(silent=True) or {}).get("message", "").strip()

    if not query:
        return jsonify({"error": "Research question is required."}), 400

    return jsonify({
        "type": "research",
        "message": "Research pipeline comes next.",
        "query": query
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)