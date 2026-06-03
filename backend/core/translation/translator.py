import os
from google import genai
from langdetect import detect
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SUPPORTED_LANGUAGES = {
    "Hindi":     "hi",
    "Marathi":   "mr",
    "Tamil":     "ta",
    "Telugu":    "te",
    "Bengali":   "bn",
    "Gujarati":  "gu",
    "Kannada":   "kn",
    "Malayalam": "ml",
    "Punjabi":   "pa",
    "Odia":      "or",
    "English":   "en",
}

def translate_text(text: str, target_language: str) -> str:
    if target_language == "English":
        return text
    if target_language not in SUPPORTED_LANGUAGES:
        return text

    prompt = (
        f"Translate the following legal text into {target_language}. "
        f"Keep all section numbers, article numbers, and legal terms exactly as they are. "
        f"Only translate the explanatory language, not the law citations.\n\n"
        f"Text to translate:\n{text}\n\n"
        f"Return ONLY the translated text, nothing else."
    )

    response = client.models.generate_content(
        model    = "gemini-2.0-flash",
        contents = prompt
    )
    return response.text.strip()


def detect_language(text: str) -> str:
    try:
        code        = detect(text)
        reverse_map = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
        return reverse_map.get(code, "English")
    except Exception:
        return "English"


def get_supported_languages() -> list:
    return list(SUPPORTED_LANGUAGES.keys())