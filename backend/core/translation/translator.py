import os
from langdetect import detect
from dotenv import load_dotenv

load_dotenv()

SUPPORTED_LANGUAGES = {
    "Hindi": "hi", "Marathi": "mr", "Tamil": "ta",
    "Telugu": "te", "Bengali": "bn", "Gujarati": "gu",
    "Kannada": "kn", "Malayalam": "ml", "Punjabi": "pa",
    "Odia": "or", "English": "en",
}


def translate_text(text: str, target_language: str) -> str:
    if target_language == "English":
        return text
    if target_language not in SUPPORTED_LANGUAGES:
        return text

    from core.llm.groq_client import call_llm

    prompt = (
        f"Translate the following legal text into {target_language}. "
        f"Keep all section numbers (like BNS 303, BNSS 479), article numbers, "
        f"and legal terms exactly as they are. "
        f"Only translate the explanatory language.\n\n"
        f"Text:\n{text}\n\n"
        f"Return ONLY the translated text, nothing else."
    )

    return call_llm(
        system_prompt=f"You are a legal translator. Translate accurately into {target_language}.",
        user_prompt=prompt,
        temperature=0.1
    )


def detect_language(text: str) -> str:
    try:
        code        = detect(text)
        reverse_map = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
        return reverse_map.get(code, "English")
    except Exception:
        return "English"


def get_supported_languages() -> list:
    return list(SUPPORTED_LANGUAGES.keys())