"""
AI assistant for RPHMS, powered by Groq (fast open-model inference).

Lets a healthcare provider ask natural-language questions about the
current monitoring state ("which patients are critical right now?",
"what does a warning SpO2 status mean?") from a chat widget on the
dashboard.

SETUP:
1. Get a free API key from https://console.groq.com/keys
2. Put it in backend/.env as GROQ_API_KEY=gsk_...
3. (Optional) Set GROQ_MODEL if you want a different model - defaults
   to "llama-3.3-70b-versatile". See https://console.groq.com/docs/models
   for the current list of available models.

If GROQ_API_KEY is not set, the assistant responds with a friendly
message explaining it's not configured yet - the rest of the system
works completely normally either way, same pattern as the Telegram
alerts (telegram_alert.py).

IMPORTANT: this assistant answers general questions and explains what's
on the dashboard. It does NOT diagnose patients or replace clinical
judgment - the system prompt below enforces that boundary, and you
should mention this design choice in your project defense.
"""

import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are the RPHMS Assistant, embedded in a hospital
remote patient monitoring dashboard. You help healthcare staff understand
what's on their screen - vitals, statuses, alerts, and how the system
works.

Rules you must always follow:
- You are NOT a diagnostic tool and must never diagnose a condition,
  suggest treatment, or tell a user a patient is medically safe or
  unsafe. If asked for medical judgment, direct them to consult a
  qualified healthcare professional.
- Keep answers concise and practical - this is used in a live clinical
  workflow, not a chat for long essays.
- You are given a live snapshot of the dashboard's current data below.
  Use it to answer questions about specific patients or counts
  accurately. If the answer isn't in the snapshot, say you don't have
  that information rather than guessing.
"""


def call_groq(user_message: str, dashboard_context: str, history: list[dict] | None = None) -> str:
    """
    Sends a message to Groq along with the current dashboard snapshot as
    context. Returns the assistant's reply as plain text.

    Fails gracefully: if the API key isn't set or the request fails, a
    clear, non-crashing message is returned instead of raising - the
    chat widget will just display that message.
    """
    if not GROQ_API_KEY:
        return (
            "The AI assistant isn't configured yet. Add GROQ_API_KEY to "
            "backend/.env (see .env.example) to enable it. Get a free key "
            "at https://console.groq.com/keys"
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nCurrent dashboard snapshot:\n" + dashboard_context}]

    if history:
        for turn in history[-6:]:  # keep only recent turns to stay within context limits
            messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 400,
            },
            timeout=20,
        )

        if response.status_code == 401:
            return "Groq rejected the API key (401). Check GROQ_API_KEY in backend/.env."
        if response.status_code == 404:
            return (f"Groq doesn't recognise the model '{GROQ_MODEL}' (404). "
                    "Check https://console.groq.com/docs/models for valid model names "
                    "and set GROQ_MODEL in backend/.env.")
        if response.status_code == 429:
            return "Groq is rate-limiting requests right now. Wait a moment and try again."
        if response.status_code != 200:
            print(f"[groq] API error {response.status_code}: {response.text}")
            return "Sorry, the AI assistant couldn't process that request right now. Please try again shortly."

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except requests.RequestException as e:
        print(f"[groq] Request failed: {e}")
        return "Sorry, I couldn't reach the AI assistant service. Check your internet connection and try again."
    except (KeyError, IndexError) as e:
        print(f"[groq] Unexpected response shape: {e}")
        return "Sorry, I received an unexpected response from the AI service."
