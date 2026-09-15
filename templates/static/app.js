let currentMode = "chat";
let chatHistory = [];

const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


function addMessage(role, text) {
    const message = document.createElement("div");

    message.className =
        role === "user"
            ? "message user-message"
            : "message rex-message";

    message.innerHTML = `
        <div class="message-avatar">
            ${role === "user" ? "👤" : "R"}
        </div>

        <div class="message-content">
            ${escapeHTML(text).replace(/\n/g, "<br>")}
        </div>
    `;

    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
}


function showTyping() {
    const typing = document.createElement("div");

    typing.id = "typingIndicator";
    typing.className = "message rex-message";

    typing.innerHTML = `
        <div class="message-avatar">R</div>

        <div class="message-content typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;
}


function removeTyping() {
    const typing = document.getElementById("typingIndicator");

    if (typing) {
        typing.remove();
    }
}


async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) return;

    addMessage("user", message);

    chatHistory.push({
        role: "user",
        content: message
    });

    messageInput.value = "";

    sendButton.disabled = true;
    messageInput.disabled = true;

    showTyping();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message,
                history: chatHistory
            })
        });

        const data = await response.json();

        removeTyping();

        if (!response.ok) {
            throw new Error(data.error || "REX could not respond.");
        }

        const reply = data.reply || "REX received your message.";

        addMessage("assistant", reply);

        chatHistory.push({
            role: "assistant",
            content: reply
        });

    } catch (error) {
        removeTyping();

        addMessage(
            "assistant",
            "⚠️ REX had a problem: " + error.message
        );

    } finally {
        sendButton.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}


function setMode(mode) {
    currentMode = mode;

    document
        .querySelectorAll(".mode-button")
        .forEach(button => {
            button.classList.toggle(
                "active",
                button.dataset.mode === mode
            );
        });

    if (mode === "chat") {
        messageInput.placeholder = "Ask REX anything...";
    }

    if (mode === "search") {
        messageInput.placeholder = "What do you want REX to search for?";
    }

    if (mode === "image") {
        messageInput.placeholder = "Describe the image you want...";
    }

    if (mode === "video") {
        messageInput.placeholder = "Describe the video you want...";
    }

    if (mode === "research") {
        messageInput.placeholder = "What should REX research?";
    }
}


function clearChat() {
    chatHistory = [];

    chatBox.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">R</div>
            <h2>Welcome to REX AI</h2>
            <p>Ask me anything and let's build something amazing.</p>
        </div>
    `;
}


sendButton.addEventListener("click", sendMessage);


messageInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});


document.querySelectorAll(".mode-button").forEach(button => {
    button.addEventListener("click", () => {
        setMode(button.dataset.mode);
    });
});


setMode("chat");