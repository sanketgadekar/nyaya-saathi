import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.ocr.gemini_vision       import extract_fir_data, check_confidence
from core.rag.chromadb_client     import query_law
from core.llm.groq_client         import call_llm
from core.translation.translator  import translate_text
from core.rag.law_router_util     import detect_applicable_law


def explain_fir(image_path: str, language: str = "English") -> dict:
    print("[FIR Explainer] Reading FIR image...")

    # Step 1 — OCR
    fir_data   = extract_fir_data(image_path)
    confidence = check_confidence(fir_data)

    if confidence < 0.5:
        return {
            "status":     "low_confidence",
            "message":    "Image too unclear. Please upload a sharper photo.",
            "confidence": round(confidence, 2)
        }

    sections = fir_data.get("sections_charged", [])
    law      = detect_applicable_law(fir_data.get("date_of_fir", ""))

    # Step 2 — Retrieve plain-language section info from RAG
    retrieved = []
    for sec in sections:
        clean   = sec.replace("BNS","").replace("IPC","").replace("Section","").strip()
        results = query_law(f"section {clean} {law}", law, n=1)
        retrieved.extend(results)

    context = "\n".join(retrieved) if retrieved else "No section details found in database."

    # Step 3 — Generate plain-language explanation
    system_prompt = """
    You are a legal literacy assistant helping common Indian citizens understand their FIR.
    Explain in extremely simple language — as if talking to someone with Class 8 education.
    Use short sentences. No legal jargon.

    For each section charged, explain:
    1. What this charge means in plain words (1-2 sentences)
    2. Maximum punishment
    3. Is bail a right (bailable) or up to judge (non-bailable)?
    4. What the person should do RIGHT NOW (one action)

    End with an URGENCY level: LOW / MEDIUM / HIGH
    HIGH = non-bailable with high punishment
    MEDIUM = non-bailable but lower punishment
    LOW = bailable offence
    """

    user_prompt = f"""
    FIR Details:
    - Accused: {fir_data.get('accused_name', 'The accused')}
    - Sections charged: {', '.join(sections)}
    - Date of FIR: {fir_data.get('date_of_fir', 'Not specified')}
    - Applicable law: {law}

    Section information from legal database:
    {context}

    Explain this FIR in simple language.
    """

    explanation = call_llm(system_prompt, user_prompt, temperature=0.3)

    # Step 4 — Translate if needed
    if language != "English":
        explanation = translate_text(explanation, language)

    # Step 5 — Detect urgency
    urgency = "HIGH" if "HIGH" in explanation else \
              "MEDIUM" if "MEDIUM" in explanation else "LOW"

    print(f"[FIR Explainer] Done. Urgency: {urgency}")

    return {
        "status":      "success",
        "fir_data":    fir_data,
        "confidence":  round(confidence, 2),
        "explanation": explanation,
        "urgency":     urgency,
        "sections":    sections,
        "law":         law,
        "language":    language
    }