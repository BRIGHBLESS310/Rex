import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENAI_KEY = os.environ.get("OPENAI_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")

SYSTEM_PROMPT = """
You are REX AI.

You were created by Blessed Ovenseri.

If someone asks who created, made, built, developed, or owns REX,
answer:

"I was created by Blessed Ovenseri."

You are a helpful AI assistant.
Be friendly, clear, and concise.
You understand normal English and Nigerian Pidgin.
"""


def openai_chat(message, history):
    if not OPENAI_KEY:
        return None

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Keep recent conversation context
    for item in history[-10:]:
        role = item.get("role")
        content = item.get("content")

        if role in ("user", "assistant") and content:
            messages.append({
                "role": role,
                "content": content
            })

    messages.append({
        "role": "user",
        "content": message
    })

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=60
        )

        if response.status_code != 200:
            print("OpenAI error:", response.text)
            return None

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("OpenAI exception:", e)
        return None


def anthropic_chat(message, history):
    if not ANTHROPIC_KEY:
        return None

    messages = []

    for item in history[-10:]:
        role = item.get("role")
        content = item.get("content")

        if role in ("user", "assistant") and content:
            messages.append({
                "role": role,
                "content": content
            })

    messages.append({
        "role": "user",
        "content": message
    })

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-3-haiku-20240307",
                "system": SYSTEM_PROMPT,
                "messages": messages,
                "max_tokens": 1000
            },
            timeout=60
        )

        if response.status_code != 200:
            print("Anthropic error:", response.text)
            return None

        data = response.json()

        return data["content"][0]["text"]

    except Exception as e:
        print("Anthropic exception:", e)
        return None


def local_fallback(message):
    text = message.lower().strip()

    creator_words = [
        "who created you",
        "who made you",
        "who built you",
        "who developed you",
        "who is your creator",
        "who owns rex"
    ]

    if any(word in text for word in creator_words):
        return "I was created by Blessed Ovenseri. 🚀"

    if "hello" in text or "hi" in text or "hey" in text:
        return "Hey! 👋 I'm REX AI. How can I help you?"

    if "how are you" in text:
        return "I'm doing great! 🤖 Ready to help."

    return (
        "I'm REX AI. 🤖 My main AI services aren't available right now, "
        "but I'm still online. Try again in a moment."
    )


def smart_chat(message, history):
    # Always guarantee the creator response.
    lower = message.lower()

    creator_words = [
        "who created you",
        "who made you",
        "who built you",
        "who developed you",
        "who is your creator",
        "who owns rex"
    ]

    if any(word in lower for word in creator_words):
        return "I was created by Blessed Ovenseri. 🚀"

    # Primary AI
    answer = openai_chat(message, history)

    if answer:
        return answer

    # Backup AI
    answer = anthropic_chat(message, history)

    if answer:
        return answer

    # Local fallback
    return local_fallback(message)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not message:
        return jsonify({
            "error": "Please type a message."
        }), 400

    answer = smart_chat(message, history)

    return jsonify({
        "reply": answer,
        "assistant": "REX AI"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "assistant": "REX AI",
        "creator": "Blessed Ovenseri"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )