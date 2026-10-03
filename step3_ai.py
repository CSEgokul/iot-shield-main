"""
step3_ai.py — IoT Shield AI Enhancement Layer
Tests LLM connection (Gemini / Groq / OpenAI cloud API or local Ollama)
and explains threats using the AI assistant.
Run: python step3_ai.py
"""

import os
import ai_assistant

def explain_threat(label, src_ip, dst_ip, confidence, proto):
    prompt = (
        f"You are a network security analyst. Explain this IoT network alert in 2-3 sentences:\n"
        f"- Threat type: {str(label).upper()}\n"
        f"- Source IP: {src_ip}\n"
        f"- Destination IP: {dst_ip}\n"
        f"- Protocol: {str(proto).upper()}\n"
        f"- Confidence: {confidence:.1f}%\n"
        f"What does this mean and what action should be taken?"
    )
    answer, provider = ai_assistant.ask_ai(prompt)
    if answer is None:
        return (
            "[AI Assistant Offline] No cloud API key configured (GEMINI_API_KEY or GROQ_API_KEY) "
            "and local Ollama is not running."
        )
    return f"[{provider}]\n{answer}"


if __name__ == "__main__":
    print("=" * 60)
    print("  IoT Shield — AI Layer Test")
    print("=" * 60)
    provider = ai_assistant.get_available_provider() or "None (standby)"
    print(f"\n[*] Active AI Provider: {provider}")

    result = explain_threat(
        label="ddos",
        src_ip="192.168.1.100",
        dst_ip="10.0.0.1",
        confidence=97.3,
        proto="udp"
    )
    print(f"\n[*] AI Response:\n{result}")
    print("\n[*] Run step4_dashboard.py next.")