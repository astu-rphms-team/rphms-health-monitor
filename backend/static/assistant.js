/* ============================================================
   RPHMS AI Assistant widget (Grok-powered)

   Injects a floating chat button + panel into whatever page loads
   this file. It calls our own backend at POST /api/ai/chat, which
   forwards the request to Grok server-side - the API key never
   touches the browser.
   ============================================================ */

const AI_SUGGESTIONS = [
  "Which patients need attention right now?",
  "Summarise the current ward status",
  "Any devices offline?",
  "What do the status thresholds mean?",
];

let aiHistory = [];
let aiBusy = false;

function buildAssistantWidget() {
  if (document.getElementById("aiLauncher")) return; // already mounted

  const launcher = document.createElement("button");
  launcher.id = "aiLauncher";
  launcher.title = "Ask the RPHMS assistant";
  launcher.innerHTML = "✦";

  const panel = document.createElement("div");
  panel.id = "aiPanel";
  panel.innerHTML = `
    <div class="ai-header">
      <div>
        <div class="ai-title"><span class="spark">✦</span> RPHMS Assistant</div>
        <div class="ai-sub">Powered by Grok · sees your live dashboard</div>
      </div>
      <button id="aiClose" title="Close">×</button>
    </div>
    <div class="ai-messages" id="aiMessages"></div>
    <div class="ai-suggestions" id="aiSuggestions"></div>
    <div class="ai-input-row">
      <input type="text" id="aiInput" placeholder="Ask about your patients..." autocomplete="off">
      <button id="aiSend">Send</button>
    </div>
    <div class="ai-disclaimer">
      Monitoring support only — not medical advice or diagnosis.
    </div>
  `;

  document.body.appendChild(launcher);
  document.body.appendChild(panel);

  const messages = panel.querySelector("#aiMessages");
  const input = panel.querySelector("#aiInput");
  const sendBtn = panel.querySelector("#aiSend");
  const suggestionHost = panel.querySelector("#aiSuggestions");

  function addMessage(text, who) {
    const el = document.createElement("div");
    el.className = "ai-msg " + who;
    el.textContent = text;
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
    return el;
  }

  function renderSuggestions() {
    suggestionHost.innerHTML = "";
    AI_SUGGESTIONS.forEach((text) => {
      const b = document.createElement("button");
      b.textContent = text;
      b.addEventListener("click", () => {
        input.value = text;
        send();
      });
      suggestionHost.appendChild(b);
    });
  }

  async function send() {
    const message = input.value.trim();
    if (!message || aiBusy) return;

    aiBusy = true;
    sendBtn.disabled = true;
    input.value = "";
    suggestionHost.innerHTML = "";

    addMessage(message, "user");
    const thinking = addMessage("Thinking...", "bot thinking");

    try {
      const data = await apiRequest("/api/ai/chat", {
        method: "POST",
        body: JSON.stringify({ message, history: aiHistory }),
      });

      thinking.remove();
      addMessage(data.reply, "bot");

      aiHistory.push({ role: "user", content: message });
      aiHistory.push({ role: "assistant", content: data.reply });
      aiHistory = aiHistory.slice(-8); // keep the request small
    } catch (err) {
      thinking.remove();
      addMessage("Couldn't reach the assistant: " + err.message, "bot");
    } finally {
      aiBusy = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  function openPanel() {
    panel.classList.add("open");
    launcher.classList.add("hidden");
    if (!messages.children.length) {
      addMessage(
        "Hi! I can see your live dashboard. Ask me about patient status, " +
        "trends, offline devices, or how the system works.",
        "bot"
      );
      renderSuggestions();
    }
    input.focus();
  }

  function closePanel() {
    panel.classList.remove("open");
    launcher.classList.remove("hidden");
  }

  launcher.addEventListener("click", openPanel);
  panel.querySelector("#aiClose").addEventListener("click", closePanel);
  sendBtn.addEventListener("click", send);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") send();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && panel.classList.contains("open")) closePanel();
  });
}

// Mount once the page is ready.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", buildAssistantWidget);
} else {
  buildAssistantWidget();
}
