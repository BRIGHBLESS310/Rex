from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

# ========= PUT YOUR NEW KEYS HERE =========
OPENAI_KEY = os.environ.get("OPENAI_KEY", "PUT_NEW_OPENAI_KEY_HERE")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "PUT_NEW_CLAUDE_KEY_HERE")
THIRD_KEY = os.environ.get("THIRD_KEY", "")
# ==========================================

def try_openai(msg):
    if not OPENAI_KEY or "PUT_" in OPENAI_KEY:
        return None, "No OpenAI key set"
    try:
        headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": "You are Rex, built by Ovenseri Blessed from Edo State Nigeria. Answer like ChatGPT, helpful, friendly, you sabi Pidgin."}, {"role": "user", "content": msg}],
            "max_tokens": 900,
            "temperature": 0.7
        }
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'], "OpenAI ✅"
        else:
            return None, f"OpenAI fail {r.status_code}"
    except Exception as e:
        return None, f"OpenAI error: {e}"

def try_anthropic(msg):
    if not ANTHROPIC_KEY or "PUT_" in ANTHROPIC_KEY:
        return None, "No Claude key set"
    try:
        headers = {"x-api-key": ANTHROPIC_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 900,
            "messages": [{"role": "user", "content": msg}]
        }
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()['content'][0]['text'], "Claude ✅"
        else:
            return None, f"Claude fail {r.status_code}"
    except Exception as e:
        return None, f"Claude error: {e}"

def try_third(msg):
    try:
        low = msg.lower()
        if "how are you" in low:
            return "I dey kampe Blessed! 💪 I dey perfect! My 3 keys dey ready - if one nor work, another go work! hahah 😂 How you dey? Wetin you wan build today? 🚀", "Local Brain ✅"
        if "name" in low or "who are you" in low:
            return "Na me be Rex! 🤖 3-KEYS VERSION! Built by Ovenseri Blessed (BRIGHTBLESS/Shadow-lambo) from Edo State Naija! I get 3 brains: OpenAI, Claude, and Local - if one nor work, another go work! hahah", "Local Brain ✅"
        if "python" in low or "code" in low or "website" in low:
            return f"Oya for '{msg}':\n\n```python\nprint('Wetin dey sup Blessed!')\n\ndef greet(name):\n return f'Omo {{name}}, 3 keys ready! If one nor work, another go work! hahah'\n\nprint(greet('Blessed'))\n```\n", "Local Brain ✅"
    except:
        pass
    return f"Oya Blessed! You talk '{msg}' - All 3 keys no work! But I still dey here offline! Tell me wetin you wan code!", "Local Fallback ✅"

def smart_chat(msg):
    print(f"Trying for: {msg[:40]}")
    ans, log = try_openai(msg)
    logs = [f"Key1 OpenAI: {log}"]
    print(log)
    if ans:
        return ans, logs
    ans, log = try_anthropic(msg)
    logs.append(f"Key2 Claude: {log}")
    print(log)
    if ans:
        return ans, logs
    ans, log = try_third(msg)
    logs.append(f"Key3 Third: {log}")
    print(log)
    return ans, logs

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rex 3-Keys - By Blessed</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',sans-serif;background:#0a0a0f;color:#fff;height:100vh;display:flex}.sidebar{width:260px;background:#11111a;border-right:1px solid #222;display:flex;flex-direction:column;padding:15px;gap:10px;overflow-y:auto}.sidebar h2{color:#00ff88}.side-btn{padding:12px;background:rgba(255,255,255,.06);border:1px solid #222;border-radius:10px;color:#fff;cursor:pointer;text-align:left}.side-btn.active{background:linear-gradient(135deg,#00ff88,#00ccff);color:#000;font-weight:700}.key-box{background:#0f0f1a;border:1px solid #222;border-radius:10px;padding:10px;font-size:11px}.main{flex:1;display:flex;flex-direction:column}.header{padding:12px 20px;background:rgba(0,0,0,.3);border-bottom:1px solid #222;display:flex;justify-content:space-between}.video-area{display:flex;justify-content:center;padding:10px}.avatar{width:100px;height:100px;border-radius:50%;border:3px solid #00ff88;overflow:hidden}.avatar img{width:100%;height:100%;object-fit:cover}.avatar.speaking{animation:pulse.6s infinite}@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.05)}100%{transform:scale(1)}}.chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}.msg{max-width:80%;padding:12px 15px;border-radius:16px;white-space:pre-wrap;font-size:14px}.user{align-self:flex-end;background:linear-gradient(135deg,#00ff88,#00ccff);color:#000;font-weight:600}.bot{align-self:flex-start;background:#1e1e2f;border:1px solid #2a2a40}.logs{font-size:10px;opacity:.6;background:#000;border:1px solid #222;border-radius:8px;padding:8px;margin-top:6px;font-family:monospace;color:#00ff88;white-space:pre-wrap}.input-area{padding:15px;background:#11111a;border-top:1px solid #222;display:flex;gap:10px}.input-area input{flex:1;padding:13px 18px;border-radius:25px;border:1px solid #333;background:#1a1a26;color:#fff;outline:none}.input-area button{width:50px;height:50px;border-radius:50%;border:none;background:linear-gradient(135deg,#00ff88,#00ccff);cursor:pointer}.typing{display:none;font-size:12px;opacity:.6;padding:0 20px 5px}</style></head><body>
<div class="sidebar"><h2>🤖 REX 3-KEYS</h2><div style="font-size:10px;opacity:.5">If one nor work, another go work! hahah</div>
<button class="side-btn active" id="btn-chat" onclick="setMode('chat')">💬 New Chat</button>
<button class="side-btn" id="btn-search" onclick="setMode('search')">🔍 Search</button>
<button class="side-btn" id="btn-image" onclick="setMode('image')">🎨 Image</button>
<button class="side-btn" id="btn-video" onclick="setMode('video')">🎬 Video</button>
<button class="side-btn" id="btn-research" onclick="setMode('research')">🧠 Research</button>
<div class="key-box"><div style="font-weight:700;margin-bottom:4px">🔑 LIVE LOGS</div><div id="liveLogs" style="font-size:9px;opacity:.7">Ready - 3 keys loaded...</div></div>
<button class="side-btn" onclick="clearChat()" style="margin-top:auto;background:#2a1a1a">🗑️ Clear</button>
</div>
<div class="main"><div class="header"><h1 id="title">💬 Rex - 3 Keys Fallback</h1><span style="font-size:10px;background:#00ff88;color:#000;padding:4px 10px;border-radius:20px;font-weight:700">3 APIs ✅</span></div>
<div class="video-area"><div class="avatar" id="avatar"><img id="avImg" src="https://i.pravatar.cc/300?img=68"></div></div>
<div class="chat" id="chat"><div class="msg bot">Wetin dey sup Blessed? Na Rex 3-KEYS LIVE for Render! 😂

1️⃣ Try OpenAI
2️⃣ If fail → Try Claude
3️⃣ If fail → Try Local

If one nor work, another go work! hahah! Type "how are you" now! 🚀</div></div>
<div class="typing" id="typing">Rex dey try 3 keys... ⏳</div>
<div class="input-area"><input id="text" placeholder="Ask anything - 3 keys go try!" onkeypress="if(event.key==='Enter')send()"><button onclick="send()">🚀</button></div>
</div>
<script>
let mode='chat';const chat=document.getElementById('chat'),text=document.getElementById('text'),typing=document.getElementById('typing'),avatar=document.getElementById('avatar'),avImg=document.getElementById('avImg'),liveLogs=document.getElementById('liveLogs');const faces=["https://i.pravatar.cc/300?img=68","https://i.pravatar.cc/300?img=69","https://i.pravatar.cc/300?img=65"];let iv;
function setMode(m){mode=m;document.querySelectorAll('.side-btn').forEach(b=>b.classList.remove('active'));document.getElementById('btn-'+m)?.classList.add('active');document.getElementById('title').textContent=m.toUpperCase()+' - Rex 3 KEYS';}
function start(){avatar.classList.add('speaking');let i=0;iv=setInterval(()=>{avImg.src=faces[i%faces.length];i++},180)}
function stop(){avatar.classList.remove('speaking');clearInterval(iv);avImg.src=faces[0]}
function add(t,w,logs){const d=document.createElement('div');d.className='msg '+w;d.textContent=t;chat.appendChild(d);if(logs&&w==='bot'){const l=document.createElement('div');l.className='logs';l.textContent=logs.join('\\n');chat.appendChild(l);liveLogs.innerHTML=logs.join('<br>');}chat.scrollTop=chat.scrollHeight;if(w==='bot'){start();const u=new SpeechSynthesisUtterance(t.slice(0,380));u.rate=.95;u.onend=stop;speechSynthesis.speak(u);setTimeout(stop,Math.min(t.length*45,7000))}}
function clearChat(){chat.innerHTML='<div class="msg bot">Chat clear! 3 keys ready!</div>';liveLogs.innerHTML='Ready...';}
async function send(){const v=text.value.trim();if(!v)return;add(v,'user');text.value='';typing.style.display='block';liveLogs.innerHTML='Trying 3 keys...<br>Key1: OpenAI...';try{let url='/chat';if(mode!=='chat')url='/'+mode;const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:v})});const j=await r.json();typing.style.display='none';add(j.reply,'bot',j.logs);}catch(e){typing.style.display='none';add('Error! Check Render dey run!','bot');stop()}}
</script></body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat_route():
    m = request.json.get("message","")
    ans, logs = smart_chat(m)
    return jsonify({"reply": ans, "logs": logs})

@app.route("/search", methods=["POST"])
def search_route():
    q = request.json.get("message","")
    ans, logs = smart_chat(f"Search: {q}")
    return jsonify({"reply": f"🔍 {ans}", "logs": logs})

@app.route("/research", methods=["POST"])
def research_route():
    q = request.json.get("message","")
    ans, logs = smart_chat(f"Deep research: {q}")
    return jsonify({"reply": f"🧠 {ans}", "logs": logs})

@app.route("/image", methods=["POST"])
def image_route():
    return jsonify({"reply": "🎨 Image prompt ready! Add image API key for real images!", "logs": ["Image mode"]})

@app.route("/video", methods=["POST"])
def video_route():
    p = request.json.get("message","")
    ans, logs = smart_chat(f"Video storyboard: {p}")
    return jsonify({"reply": f"🎬 {ans}", "logs": logs})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("="*70)
    print("REX 3-KEYS - If one nor work, another go work! hahah")
    print(f"Running on port {port}")
    print("="*70)
    app.run(host="0.0.0.0", port=port, debug=False)