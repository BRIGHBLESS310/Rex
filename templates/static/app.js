let mode = "chat";

const chat = document.getElementById("chat");
const message = document.getElementById("message");
const typing = document.getElementById("typing");
const sendButton = document.getElementById("sendButton");
const history = document.getElementById("history");

const modeInfo = {
    chat: {
        title: "REX Chat",
        description: "Your AI assistant",
        placeholder: "Ask REX anything..."
    },

    search: {
        title: "REX Search",
        description: "Search for information",
        placeholder: "What do you want to search for?"
    },

    image: {
        title: "Generate Image",
        description: "Turn your idea into an image",
        placeholder: "Describe the image you want..."
    },

    video: {
        title: "Generate Video",
        description: "Turn your idea into a video",
        placeholder: "Describe the video you want..."
    },

    research: {
        title: "REX Research",
        description: "Deep research and analysis",
        placeholder: "What should REX research?"
    }
};


function setMode(newMode) {

    mode = newMode;

    document.querySelectorAll(".mode").forEach(button => {
        button.classList.remove("active");
    });

    const active = document.querySelector(
        `.mode[data-mode="${newMode}"]`
    );

    if (active) {
        active.classList.add("active");
    }

    document.getElementById("modeTitle").textContent =
        modeInfo[newMode].title;

    document.getElementById("modeDescription").textContent =
        modeInfo[newMode].description;

    message.placeholder =
        modeInfo[newMode].placeholder;

    message.focus();
}


function quickPrompt(prompt) {
    message.value = prompt;
    message.focus();
}


function addMessage(text, sender, logs = []) {

    const wrapper = document.createElement("div");

    wrapper.className = `message ${sender}`;

    const content = document.createElement("div");

    content.className = "message-content";

    content.textContent = text;

    wrapper.appendChild(content);

    chat.appendChild(wrapper);


    if (logs.length && sender === "bot") {

        const logBox = document.createElement("div");

        logBox.className = "logs";

        logBox.textContent = logs.join("\n");

        chat.appendChild(logBox);
    }

    chat.scrollTop = chat.scrollHeight;
}


function showTyping() {
    typing.style.display = "block";
    sendButton.disabled = true;
}


function hideTyping() {
    typing.style.display = "none";
    sendButton.disabled = false;
}


async function sendMessage() {

    const value = message.value.trim();

    if (!value) return;

    addMessage(value, "user");

    message.value = "";

    showTyping();

    let endpoint = `/api/${mode}`;

    try {

        const response = await fetch(endpoint, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: value
            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.error || "REX request failed."
            );
        }


        if (data.reply) {

            addMessage(
                data.reply,
                "bot",
                data.logs || []
            );

        } else if (data.message) {

            addMessage(
                data.message,
                "bot",
                data.logs || []
            );

        }


        saveHistory(value);

    } catch (error) {

        addMessage(
            `REX error: ${error.message}`,
            "bot"
        );

    } finally {

        hideTyping();

    }
}


function newChat() {

    chat.innerHTML = `
        <div class="welcome">

            <div class="rex-icon">🤖</div>

            <h2>Wetin dey sup? 👋</h2>

            <p>
                I'm REX. What are we building today?
            </p>

        </div>
    `;

    message.value = "";

    setMode("chat");
}


function clearChat() {

    newChat();

    history.innerHTML = "";

    localStorage.removeItem("rexHistory");
}


function saveHistory(text) {

    let saved =
        JSON.parse(
            localStorage.getItem("rexHistory") || "[]"
        );

    saved.unshift(text);

    saved = saved.slice(0, 10);

    localStorage.setItem(
        "rexHistory",
        JSON.stringify(saved)
    );

    renderHistory();
}


function renderHistory() {

    const saved =
        JSON.parse(
            localStorage.getItem("rexHistory") || "[]"
        );

    history.innerHTML = "";

    saved.forEach(item => {

        const div =
            document.createElement("div");

        div.className = "history-item";

        div.textContent =
            item.length > 30
                ? item.substring(0, 30) + "..."
                : item;

        div.onclick = () => {
            message.value = item;
            message.focus();
        };

        history.appendChild(div);

    });
}


message.addEventListener("keydown", event => {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendMessage();
    }

});


message.addEventListener("input", () => {

    message.style.height = "auto";

    message.style.height =
        Math.min(message.scrollHeight, 150) + "px";

});


renderHistory();