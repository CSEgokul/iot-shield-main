"""
ai_assistant.py — IoT Shield AI Enhancement Layer
Supports hosted cloud LLMs (Gemini, Groq, OpenAI) and local Ollama fallback.
API keys are loaded safely from Streamlit Secrets or environment variables.
"""

import os
import requests

def _get_secret(key):
    """Retrieve key from Streamlit secrets or environment variables."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = str(st.secrets[key]).strip()
            if val:
                return val
    except Exception:
        pass
    return os.environ.get(key, "").strip() or None


def get_available_provider():
    """Detect available LLM provider based on configured secrets/env."""
    if _get_secret("GROQ_API_KEY"):
        return "groq"
    if _get_secret("GEMINI_API_KEY") or _get_secret("GOOGLE_API_KEY"):
        return "gemini"
    if _get_secret("OPENAI_API_KEY"):
        return "openai"
    # Check if local Ollama is reachable
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
    try:
        base_ping = ollama_url.replace("/api/generate", "")
        r = requests.get(base_ping, timeout=1.0)
        if r.status_code == 200:
            return "ollama"
    except Exception:
        pass
    return None


def ask_ai(prompt, system_instruction="You are an expert IoT network security analyst."):
    """Send prompt to the best available LLM provider.
    Returns (response_text, provider_label).
    If no provider is configured or reachable, returns (None, explanation_message)."""
    provider = get_available_provider()

    # 1. Groq (Primary — user's deployed key)
    groq_key = _get_secret("GROQ_API_KEY")
    if groq_key:
        groq_models = [
            ("llama-3.3-70b-versatile", "Groq (Llama 3.3 70B)"),
            ("meta-llama/llama-4-scout-17b-16e-instruct", "Groq (Llama 4 Scout)"),
        ]
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        last_error = None
        for model_id, model_label in groq_models:
            try:
                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 300
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    return text.strip(), model_label
                last_error = f"[Groq API HTTP {resp.status_code}] {resp.text[:200]}"
            except Exception as e:
                last_error = f"[Groq connection error: {e}]"
        return last_error, "Groq"

    # 2. Gemini (fallback)
    gemini_key = _get_secret("GEMINI_API_KEY") or _get_secret("GOOGLE_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": f"{system_instruction}\n\n{prompt}"}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 300}
            }
            resp = requests.post(url, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip(), "Gemini 1.5 Flash"
            else:
                url2 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
                resp2 = requests.post(url2, json=payload, timeout=20)
                if resp2.status_code == 200:
                    data = resp2.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return text.strip(), "Gemini 2.0 Flash"
                return f"[Gemini API HTTP {resp.status_code}] {resp.text[:200]}", "Gemini"
        except Exception as e:
            return f"[Gemini connection error: {e}]", "Gemini"

    # 3. OpenAI
    openai_key = _get_secret("OPENAI_API_KEY")
    if openai_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 300
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return text.strip(), "OpenAI (GPT-4o Mini)"
            return f"[OpenAI API HTTP {resp.status_code}] {resp.text[:200]}", "OpenAI"
        except Exception as e:
            return f"[OpenAI connection error: {e}]", "OpenAI"

    # 4. Local Ollama fallback
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
    ollama_model = os.environ.get("OLLAMA_MODEL", "tinyllama")
    try:
        resp = requests.post(ollama_url, json={
            "model": ollama_model,
            "prompt": f"{system_instruction}\n\n{prompt}",
            "stream": False
        }, timeout=25)
        if resp.status_code == 200:
            text = resp.json().get("response", "No response from local model.")
            return text.strip(), f"Ollama ({ollama_model})"
    except Exception:
        pass

    return None, None
