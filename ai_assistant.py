"""
ai_assistant.py — IoT Shield AI Enhancement Layer.
Supports Groq, Gemini, OpenAI, and local Ollama.
API keys come from Streamlit Secrets or environment variables.
"""

import os

import requests


def _get_secret(key):
    """Retrieve a setting from Streamlit Secrets or the environment."""
    try:
        import streamlit as st

        if key in st.secrets:
            value = str(st.secrets[key]).strip()
            if value:
                return value
    except Exception:
        pass

    return os.environ.get(key, "").strip() or None


def get_available_provider():
    """Detect a configured provider; this does not verify API access."""
    if _get_secret("GROQ_API_KEY"):
        return "groq"

    if _get_secret("GEMINI_API_KEY") or _get_secret("GOOGLE_API_KEY"):
        return "gemini"

    if _get_secret("OPENAI_API_KEY"):
        return "openai"

    ollama_url = _get_secret("OLLAMA_URL")
    ollama_url = ollama_url or "http://localhost:11434/api/generate"

    try:
        base_url = ollama_url.removesuffix("/api/generate")
        response = requests.get(base_url, timeout=1)
        if response.status_code == 200:
            return "ollama"
    except requests.RequestException:
        pass

    return None


def ask_ai(
    prompt,
    system_instruction="You are an expert IoT network security analyst.",
):
    """Return (response_text, provider_label) for the dashboard."""

    # 1. Groq
    groq_key = _get_secret("GROQ_API_KEY")

    if groq_key:
        provider = "Groq (GPT-OSS 120B)"
        model = _get_secret("GROQ_MODEL") or "openai/gpt-oss-120b"

        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.2,
            "max_completion_tokens": 2048,
            "reasoning_effort": "low",
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )

            if response.status_code != 200:
                return (
                    f"Groq API error: HTTP {response.status_code}. "
                    "Check your API key, model access, and usage limits.",
                    provider,
                )

            data = response.json()
            answer = data["choices"][0]["message"].get("content")

            if not answer or not answer.strip():
                return "Groq returned an empty answer. Please try again.", provider

            return answer.strip(), provider

        except requests.Timeout:
            return "Groq timed out. Please try again.", provider
        except requests.RequestException:
            return "Unable to connect to Groq. Please try again.", provider
        except (ValueError, KeyError, IndexError, TypeError, AttributeError):
            return "Unexpected response received from Groq.", provider

    # 2. Gemini
    # These retain the model names from your original implementation.
    # Set GEMINI_MODEL in Secrets to use another model available to you.
    gemini_key = _get_secret("GEMINI_API_KEY") or _get_secret("GOOGLE_API_KEY")

    if gemini_key:
        configured_model = _get_secret("GEMINI_MODEL")
        models = (
            [configured_model]
            if configured_model
            else ["gemini-1.5-flash", "gemini-2.0-flash"]
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_instruction}\n\n{prompt}",
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 300,
            },
        }

        last_error = "No Gemini response received."

        for model in models:
            try:
                response = requests.post(
                    "https://generativelanguage.googleapis.com/"
                    f"v1beta/models/{model}:generateContent",
                    headers={"x-goog-api-key": gemini_key},
                    json=payload,
                    timeout=30,
                )

                if response.status_code == 200:
                    data = response.json()
                    parts = data["candidates"][0]["content"]["parts"]
                    answer = "".join(
                        part.get("text", "")
                        for part in parts
                        if not part.get("thought")
                    ).strip()

                    if answer:
                        return answer, f"Gemini ({model})"

                    last_error = "Gemini returned an empty answer."
                else:
                    last_error = (
                        f"Gemini API error: HTTP {response.status_code}. "
                        "Check your key, model access, and usage limits."
                    )

            except requests.Timeout:
                last_error = "Gemini timed out."
            except requests.RequestException:
                last_error = "Unable to connect to Gemini."
            except (ValueError, KeyError, IndexError, TypeError, AttributeError):
                last_error = "Unexpected response received from Gemini."

        return last_error, "Gemini"

    # 3. OpenAI
    openai_key = _get_secret("OPENAI_API_KEY")

    if openai_key:
        provider = "OpenAI (GPT-4o Mini)"

        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.2,
            "max_tokens": 300,
        }

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code != 200:
                return (
                    f"OpenAI API error: HTTP {response.status_code}. "
                    "Check your API key, model access, and usage limits.",
                    provider,
                )

            data = response.json()
            answer = data["choices"][0]["message"].get("content")

            if not answer or not answer.strip():
                return "OpenAI returned an empty answer.", provider

            return answer.strip(), provider

        except requests.Timeout:
            return "OpenAI timed out. Please try again.", provider
        except requests.RequestException:
            return "Unable to connect to OpenAI.", provider
        except (ValueError, KeyError, IndexError, TypeError, AttributeError):
            return "Unexpected response received from OpenAI.", provider

    # 4. Local Ollama
    ollama_url = _get_secret("OLLAMA_URL")
    ollama_url = ollama_url or "http://localhost:11434/api/generate"
    ollama_model = _get_secret("OLLAMA_MODEL") or "tinyllama"

    try:
        response = requests.post(
            ollama_url,
            json={
                "model": ollama_model,
                "prompt": f"{system_instruction}\n\n{prompt}",
                "stream": False,
            },
            timeout=30,
        )

        if response.status_code == 200:
            answer = response.json().get("response", "").strip()
            if answer:
                return answer, f"Ollama ({ollama_model})"

    except (requests.RequestException, ValueError, TypeError, AttributeError):
        pass

    return None, "No usable AI provider is configured."
