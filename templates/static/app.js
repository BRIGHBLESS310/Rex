// ==========================================
// REX AI - MAIN JAVASCRIPT
// ==========================================

let currentMode = "chat";

// ------------------------------------------
// ELEMENTS
// ------------------------------------------

const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

// ------------------------------------------
// CHANGE MODE
// ------------------------------------------

function setMode(mode) {
    currentMode = mode;

    // Remove active state
    document.querySelectorAll(".mode-button").forEach(button => {
        button.classList.remove("active");
    });

    // Add active state
    const selected = document.querySelector(
        `[data-mode="${mode}"]`
    );

    if (selected) {
        selected.classList.add("active");
    }

    // Update placeholder
    const placeholders = {
        chat: "Ask REX anything...",
        search: "What should REX search for?",
        image: "Describe the image you want...",
        video: "Describe the video you want...",
        research: "What should REX research?"
    };

    if (messageInput) {
        messageInput.placeholder =
            placeholders[mode] || placeholders.chat;
    }
}

// ------------------------------------------
// ADD MESSAGE
// ------------------------------------------

function addMessage(sender, content) {
    if (!chatBox) return;

    const message = document.createElement("div");

    message.className =
        sender === "user"
            ? "message user-message"
            : "message rex-message";

    message.innerHTML = content;

    chatBox.appendChild(message);

    chatBox.scrollTop = chatBox.scrollHeight;
}

// ------------------------------------------
// TYPING INDICATOR
// ------------------------------------------

function showTyping() {
    if (!chatBox) return;

    const typing = document.createElement("div");

    typing.id = "rexTyping";
    typing.className = "message rex-message";

    typing.innerHTML = `
        <div class="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatBox.appendChild(typing);

    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
    const typing = document.getElementById("rexTyping");

    if (typing) {
        typing.remove();
    }
}

// ------------------------------------------
// SEND CHAT
// ------------------------------------------

async function send() {
    if (!messageInput) return;

    const prompt = messageInput.value.trim();

    if (!prompt) return;

    messageInput.value = "";

    // Show user's message
    addMessage("user", escapeHTML(prompt));

    // IMAGE
    if (currentMode === "image") {
        await generateImage(prompt);
        return;
    }

    // VIDEO
    if (currentMode === "video") {
        await generateVideo(prompt);
        return;
    }

    // Other modes
    await sendToAPI(currentMode, prompt);
}

// ------------------------------------------
// SEND TO BACKEND
// ------------------------------------------

async function sendToAPI(mode, prompt) {
    showTyping();

    try {
        const response = await fetch(`/api/${mode}`, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                prompt: prompt
            })
        });

        const data = await response.json();

        removeTyping();

        if (!response.ok) {
            addMessage(
                "rex",
                `❌ ${escapeHTML(
                    data.error || "Something went wrong."
                )}`
            );

            return;
        }

        // Try common response fields
        const answer =
            data.answer ||
            data.response ||
            data.message ||
            data.result ||
            "REX didn't return a response.";

        addMessage(
            "rex",
            formatResponse(answer)
        );

    } catch (error) {
        removeTyping();

        addMessage(
            "rex",
            "❌ Could not connect to REX's server."
        );

        console.error(error);
    }
}

// ------------------------------------------
// REAL IMAGE GENERATION
// ------------------------------------------

async function generateImage(prompt) {
    showTyping();

    try {
        const response = await fetch("/api/image", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                prompt: prompt
            })
        });

        const data = await response.json();

        removeTyping();

        if (!response.ok) {
            addMessage(
                "rex",
                `❌ ${escapeHTML(
                    data.error || "Image generation failed."
                )}`
            );

            return;
        }

        const image = data.image;

        if (!image) {
            addMessage(
                "rex",
                "❌ REX did not receive an image."
            );

            return;
        }

        // Base64 image
        if (image.b64_json) {
            const imageHTML = `
                <div class="generated-image">
                    <img
                        src="data:image/png;base64,${image.b64_json}"
                        alt="REX generated image"
                    >
                </div>
            `;

            addMessage("rex", imageHTML);

            return;
        }

        // URL image
        if (image.url) {
            const imageHTML = `
                <div class="generated-image">
                    <img
                        src="${escapeAttribute(image.url)}"
                        alt="REX generated image"
                    >
                </div>
            `;

            addMessage("rex", imageHTML);

            return;
        }

        addMessage(
            "rex",
            "❌ REX received an unknown image format."
        );

    } catch (error) {
        removeTyping();

        addMessage(
            "rex",
            "❌ Image generation could not connect to the server."
        );

        console.error("IMAGE ERROR:", error);
    }
}

// ------------------------------------------
// VIDEO GENERATION
// ------------------------------------------

async function generateVideo(prompt) {
    showTyping();

    try {
        const response = await fetch("/api/video", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                prompt: prompt
            })
        });

        const data = await response.json();

        removeTyping();

        if (!response.ok) {
            addMessage(
                "rex",
                `❌ ${escapeHTML(
                    data.error || "Video generation failed."
                )}`
            );

            return;
        }

        const result =
            data.video ||
            data.answer ||
            data.response ||
            data.message ||
            data.result;

        if (!result) {
            addMessage(
                "rex",
                "🎬 Video request completed, but no video was returned yet."
            );

            return;
        }

        // If backend returns a video URL
        if (
            typeof result === "string" &&
            (
                result.startsWith("http://") ||
                result.startsWith("https://")
            )
        ) {
            addMessage(
                "rex",
                `
                <div class="generated-video">
                    <video controls>
                        <source src="${escapeAttribute(result)}">
                        Your browser does not support video.
                    </video>
                </div>
                `
            );

            return;
        }

        addMessage(
            "rex",
            formatResponse(result)
        );

    } catch (error) {
        removeTyping();

        addMessage(
            "rex",
            "❌ Video generation could not connect to the server."
        );

        console.error("VIDEO ERROR:", error);
    }
}

// ------------------------------------------
// CLEAR CHAT
// ------------------------------------------

function clearChat() {
    if (!chatBox) return;

    chatBox.innerHTML = "";

    localStorage.removeItem("rexChatHistory");

    showWelcomeMessage();
}

// ------------------------------------------
// WELCOME MESSAGE
// ------------------------------------------

function showWelcomeMessage() {
    if (!chatBox) return;

    addMessage(
        "rex",
        `
        <h2>👋 Hey! I'm REX.</h2>

        <p>
            I'm ready to help you.
        </p>

        <p>
            Try Chat, Search, Image, Video, or Research.
        </p>
        `
    );
}

// ------------------------------------------
// SAVE CHAT
// ------------------------------------------

function saveChat() {
    if (!chatBox) return;

    localStorage.setItem(
        "rexChatHistory",
        chatBox.innerHTML
    );
}

// ------------------------------------------
// LOAD CHAT
// ------------------------------------------

function loadChat() {
    if (!chatBox) return;

    const saved =
        localStorage.getItem("rexChatHistory");

    if (saved) {
        chatBox.innerHTML = saved;
    } else {
        showWelcomeMessage();
    }
}

// ------------------------------------------
// ESCAPE HTML
// ------------------------------------------

function escapeHTML(text) {
    const div = document.createElement("div");

    div.textContent = String(text);

    return div.innerHTML;
}

// ------------------------------------------
// ESCAPE ATTRIBUTE
// ------------------------------------------

function escapeAttribute(text) {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

// ------------------------------------------
// FORMAT RESPONSE
// ------------------------------------------

function formatResponse(text) {
    if (text === null || text === undefined) {
        return "";
    }

    return escapeHTML(String(text))
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n/g, "<br>");
}

// ------------------------------------------
// ENTER KEY
// ------------------------------------------

if (messageInput) {
    messageInput.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();
                send();
            }

        }
    );
}

// ------------------------------------------
// SEND BUTTON
// ------------------------------------------

if (sendButton) {
    sendButton.addEventListener(
        "click",
        send
    );
}

// ------------------------------------------
// MODE BUTTONS
// ------------------------------------------

document
    .querySelectorAll(".mode-button")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const mode =
                    button.dataset.mode;

                if (mode) {
                    setMode(mode);
                }

            }
        );

    });

// ------------------------------------------
// QUICK ACTION BUTTONS
// ------------------------------------------

document
    .querySelectorAll("[data-action]")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const action =
                    button.dataset.action;

                if (action) {
                    setMode(action);

                    if (messageInput) {
                        messageInput.focus();
                    }
                }

            }
        );

    });

// ------------------------------------------
// START REX
// ------------------------------------------

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setMode("chat");

        loadChat();

    }
);