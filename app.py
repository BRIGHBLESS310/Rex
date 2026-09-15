import os
import requests

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv


# =========================================================
# REX AI
# Created by Blessed Ovenseri
# =========================================================

load_dotenv()

app = Flask(__name__)


# =========================================================
# API KEYS
# =========================================================

OPENAI_KEY = os.environ.get("OPENAI_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")
THIRD_KEY = os.environ.get("THIRD_KEY", "")

IMAGE_API_KEY = os.environ.get("IMAGE_API_KEY", "")
VIDEO_API_KEY = os.environ.get("VIDEO_API_KEY", "")


# =========================================================
# REX IDENTITY
# =========================================================

SYSTEM_PROMPT = """
You are REX AI.

You were created by Blessed Ovenseri.

IMPORTANT IDENTITY RULE:
If a user asks:
- Who created you?
- Who made you?
- Who built you?
- Who is your creator?
- Who developed you?
- Who owns REX?
- Who made REX?

Answer clearly:

"I was created by Blessed Ovenseri."

Do not claim that you created yourself.

You are a helpful AI assistant.
Be friendly, useful, and concise.
You can understand Nigerian English and Nigerian Pidgin.
"""


# =========================================================
# OPENAI CHAT
# =========================================================

def try_openai(prompt):

    if not OPENAI_KEY:
        return None

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
                        "content": SYSTEM_PROMPT
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                "temperature": 0.7
            },

            timeout=60
        )

        if not response.ok:
            print("OpenAI error:", response.text)
            return None

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:

        print("OpenAI exception:", e)

        return None


# =========================================================
# ANTHROPIC CHAT
# =========================================================

def try_anthropic(prompt):

    if not ANTHROPIC_KEY:
        return None

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

                "max_tokens": 1000,

                "system": SYSTEM_PROMPT,

                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },

            timeout=60
        )

        if not response.ok:
            print("Anthropic error:", response.text)
            return None

        data = response.json()

        return data["content"][0]["text"]

    except Exception as e:

        print("Anthropic exception:", e)

        return None


# =========================================================
# LOCAL FALLBACK
# =========================================================

def local_fallback(prompt):

    p = prompt.lower().strip()

    # Creator questions
    creator_questions = [
        "who created you",
        "who made you",
        "who built you",
        "who is your creator",
        "who developed you",
        "who made rex",
        "who built rex",
        "who created rex",
        "who owns rex"
    ]

    if any(question in p for question in creator_questions):

        return "I was created by Blessed Ovenseri."


    # Greetings
    if (
        p.startswith("hello")
        or p.startswith("hi")
        or p.startswith("hey")
    ):

        return (
            "Hello! 👋 I'm REX AI, created by Blessed Ovenseri. "
            "How can I help you?"
        )


    # Default
    return (
        "I'm REX AI. I couldn't reach my AI providers right now, "
        "but I'm still here to help."
    )


# =========================================================
# SMART CHAT
# =========================================================

def smart_chat(prompt):

    # Always handle creator identity locally first
    # so REX gives the correct answer even if an API fails.

    p = prompt.lower()

    creator_questions = [
        "who created you",
        "who made you",
        "who built you",
        "who is your creator",
        "who developed you",
        "who made rex",
        "who built rex",
        "who created rex"
    ]

    if any(question in p for question in creator_questions):

        return "I was created by Blessed Ovenseri."


    # Try OpenAI first
    answer = try_openai(prompt)

    if answer:
        return answer


    # Try Anthropic second
    answer = try_anthropic(prompt)

    if answer:
        return answer


    # Local fallback
    return local_fallback(prompt)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# CHAT API
# =========================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json() or {}

    prompt = (data.get("prompt") or "").strip()

    if not prompt:

        return jsonify({
            "error": "Please enter a message."
        }), 400


    answer = smart_chat(prompt)

    return jsonify({
        "success": True,
        "answer": answer
    })


# =========================================================
# IMAGE GENERATION
# =========================================================

@app.route("/api/image", methods=["POST"])
def generate_image():

    data = request.get_json() or {}

    prompt = (data.get("prompt") or "").strip()


    if not prompt:

        return jsonify({
            "error": "Please describe the image you want."
        }), 400


    if not OPENAI_KEY:

        return jsonify({
            "error": "OPENAI_KEY is missing."
        }), 500


    try:

        response = requests.post(

            "https://api.openai.com/v1/images/generations",

            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": "gpt-image-2.5-flare",
                "prompt": prompt,
                "size": "1024x1024",
                "quality": "medium"
            },

            timeout=180
        )


        result = response.json()


        if not response.ok:

            message = (
                result
                .get("error", {})
                .get("message", "Image generation failed.")
            )

            return jsonify({
                "error": message
            }), response.status_code


        if not result.get("data"):

            return jsonify({
                "error": "No image was returned."
            }), 500


        image = result["data"][0]


        return jsonify({
            "success": True,
            "image": image
        })


    except requests.Timeout:

        return jsonify({
            "error": "Image generation timed out. Please try again."
        }), 504


    except Exception as e:

        print("Image error:", e)

        return jsonify({
            "error": "Image generation failed."
        }), 500


# =========================================================
# VIDEO GENERATION
# =========================================================

@app.route("/api/video", methods=["POST"])
def generate_video():

    data = request.get_json() or {}

    prompt = (data.get("prompt") or "").strip()


    if not prompt:

        return jsonify({
            "error": "Please describe the video you want."
        }), 400


    # We are keeping this route ready for the
    # real video-generation provider.
    #
    # DO NOT pretend that this generates a video yet.

    return jsonify({

        "success": False,

        "message": (
            "REX video generation is not connected yet. "
            "The video API route is ready for the next upgrade."
        )

    }), 501


# =========================================================
# SEARCH
# =========================================================

@app.route("/api/search", methods=["POST"])
def search():

    data = request.get_json() or {}

    prompt = (data.get("prompt") or "").strip()


    if not prompt:

        return jsonify({
            "error": "Please enter something to search for."
        }), 400


    # Temporary search mode.
    # We will replace this with a real web-search API next.

    answer = smart_chat(
        f"""
The user wants information about this search:

{prompt}

Explain that this is currently REX's AI-assisted search mode.
Do not pretend that you performed a live web search.
Give the best answer you can from your available knowledge.
"""
    )


    return jsonify({
        "success": True,
        "answer": answer
    })


# =========================================================
# RESEARCH
# =========================================================

@app.route("/api/research", methods=["POST"])
def research():

    data = request.get_json() or {}

    prompt = (data.get("prompt") or "").strip()


    if not prompt:

        return jsonify({
            "error": "Please enter a research topic."
        }), 400


    answer = smart_chat(
        f"""
Research topic:

{prompt}

Give a structured research-style answer.
Use headings and bullet points where useful.
Do not claim that you searched the live internet.
"""
    )


    return jsonify({
        "success": True,
        "answer": answer
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "online",
        "assistant": "REX AI",
        "creator": "Blessed Ovenseri"
    })


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )