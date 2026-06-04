import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.rag.chromadb_client    import query_law, query_rights
from core.llm.groq_client        import call_llm


# ── Smart language detector — handles Hinglish and mixed script ──────────────

def detect_language_smart(text: str) -> str:

    # Check for actual Devanagari characters (Hindi/Marathi script)
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    if hindi_chars > 2:
        return "Hindi"

    # Check for Tamil script
    tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    if tamil_chars > 2:
        return "Tamil"

    # Check for Telugu script
    telugu_chars = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')
    if telugu_chars > 2:
        return "Telugu"

    # Check for Bengali script
    bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
    if bengali_chars > 2:
        return "Bengali"

    # Check for Gujarati script
    gujarati_chars = sum(1 for c in text if '\u0A80' <= c <= '\u0AFF')
    if gujarati_chars > 2:
        return "Gujarati"

    # Check for Punjabi/Gurmukhi script
    punjabi_chars = sum(1 for c in text if '\u0A00' <= c <= '\u0A7F')
    if punjabi_chars > 2:
        return "Punjabi"

    # Hinglish detection — common Hindi words written in English letters
    hinglish_words = [
        "mujhe", "kaise", "hai", "nahi", "kya", "aur", "mera", "meri",
        "hoga", "milegi", "karein", "batao", "chahiye", "tha", "thi",
        "mere", "tumhara", "aapka", "hum", "tum", "woh", "yeh", "isko",
        "usko", "lekin", "kyunki", "isliye", "theek", "achha", "nahin",
        "abhi", "phir", "bahut", "thoda", "zyada", "sirf", "bilkul",
        "zaroor", "samajh", "pata", "maloom", "jaana", "aana", "dena",
        "lena", "karna", "rehna", "milna", "bolna", "sunna", "dekhna"
    ]

    text_lower  = text.lower()
    hindi_count = sum(1 for w in hinglish_words if w in text_lower.split())
    # Also check substrings for common endings
    if hindi_count == 0:
        hindi_count = sum(1 for w in ["mujhe","kaise","milegi","karein","chahiye","lekin","kyunki"]
                          if w in text_lower)

    if hindi_count >= 1:
        return "Hindi"

    # Marathi-specific words
    marathi_words = ["aahe", "nahi", "kay", "kuthe", "kasa", "aplya",
                     "mazha", "tumcha", "tyacha", "ithe", "tithe"]
    marathi_count = sum(1 for w in marathi_words if w in text_lower)
    if marathi_count >= 1:
        return "Marathi"

    # Fall back to langdetect library
    try:
        from langdetect import detect
        code = detect(text)
        lang_map = {
            "hi": "Hindi",
            "mr": "Marathi",
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi",
            "or": "Odia",
            "en": "English"
        }
        return lang_map.get(code, "English")
    except Exception:
        return "English"


# ── Main chat function ───────────────────────────────────────────────────────

def legal_chat(
    message:  str,
    history:  list = [],
    language: str  = "English"
) -> dict:

    print(f"[Legal Chat] Message: {message[:80]}...")

    # Step 1 — Detect language from message
    detected = detect_language_smart(message)
    print(f"[Legal Chat] Detected language: {detected}")

    # Step 2 — Retrieve relevant law + rights from ChromaDB
    law_results    = query_law(message,    "BNS", n=3)
    rights_results = query_rights(message, n=2)
    all_context    = law_results + rights_results
    context        = "\n".join(all_context) if all_context else "No specific context found."

    print(f"[Legal Chat] Context chunks: {len(all_context)}")

    # Step 3 — Build conversation history (last 4 turns only)
    history_text = ""
    for turn in history[-4:]:
        u = turn.get("user",      "")
        a = turn.get("assistant", "")
        if u:
            history_text += f"User: {u}\n"
        if a:
            history_text += f"Assistant: {a}\n"

    # Step 4 — Build system prompt
    system_prompt = f"""
You are Nyaya Saathi — India's free AI legal companion for common citizens.
You help people understand Indian law, their rights, and legal procedures.

LANGUAGE RULE: The user is writing in {detected}. You MUST respond in {detected}.
If the user writes in Hindi or Hinglish, respond in simple Hindi.
If the user writes in Marathi, respond in Marathi.
Always match the user's language exactly.

CONTENT RULES:
1. Only answer questions about Indian law
2. Always cite the exact section number — BNS, BNSS, IPC, or Constitution article
3. Use simple everyday language — imagine explaining to a farmer or daily wage worker
4. Keep answers under 200 words
5. If you are not sure, say: "Please consult a free NALSA lawyer for this — call 15100"
6. Never give advice that could harm the user
7. Always mention if something is free (like NALSA legal aid)

IMPORTANT LAW NAMES:
- New criminal law = BNS (Bharatiya Nyaya Sanhita) 2023
- New criminal procedure = BNSS (Bharatiya Nagarik Suraksha Sanhita) 2023
- Bail after serving time = BNSS Section 479
- Right to know arrest reason = BNSS Section 47
- Free legal aid = NALSA, call 15100
"""

    # Step 5 — Build user prompt
    user_prompt = f"""
Previous conversation:
{history_text if history_text else "No previous conversation."}

User's question: {message}

Relevant legal information:
{context}

Answer the question clearly in {detected} language.
"""

    # Step 6 — Call Groq LLM
    answer = call_llm(
        system_prompt = system_prompt,
        user_prompt   = user_prompt,
        temperature   = 0.3
    )

    print(f"[Legal Chat] Done. Response: {len(answer)} chars")

    return {
        "status":            "success",
        "answer":            answer,
        "detected_language": detected,
        "context_used":      len(all_context),
        "language":          detected
    }