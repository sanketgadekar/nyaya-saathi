import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.ocr.gemini_vision      import extract_fir_data, check_confidence
from core.rag.chromadb_client    import query_law
from core.llm.groq_client        import call_llm
from core.translation.translator import translate_text
from core.rag.law_router_util    import detect_applicable_law


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

    # Step 2 — Retrieve section info from RAG
    retrieved = []
    for sec in sections:
        clean   = sec.replace("BNS","").replace("IPC","").replace("Section","").strip()
        results = query_law(f"section {clean} {law} punishment bailable", law, n=1)
        retrieved.extend(results)

    context = "\n".join(retrieved) if retrieved else "No section details found."

    # Step 3 — Generate plain explanation via Groq
    system_prompt = """
    You are a legal literacy assistant helping common Indian citizens understand their FIR.
    Explain in extremely simple language — Class 8 level. Short sentences. No jargon.

    For each section charged, explain:
    1. What this charge means in plain words (1-2 sentences)
    2. Maximum punishment
    3. Is bail a RIGHT (bailable) or up to judge (non-bailable)?
    4. What the person should do RIGHT NOW — one clear action

    End your response with one of these urgency levels on its own line:
    URGENCY: HIGH
    URGENCY: MEDIUM
    URGENCY: LOW

    HIGH = non-bailable with high punishment (7+ years)
    MEDIUM = non-bailable but lower punishment
    LOW = bailable offence
    """

    user_prompt = f"""
    FIR Details:
    - Accused: {fir_data.get('accused_name', 'The accused')}
    - Sections charged: {', '.join(sections)}
    - Date of FIR: {fir_data.get('date_of_fir', 'Not specified')}
    - Applicable law: {law}

    Section info from database:
    {context}

    Explain in simple language.
    """

    explanation = call_llm(system_prompt, user_prompt, temperature=0.3)

    # Step 4 — Translate if needed
    if language != "English":
        explanation = translate_text(explanation, language)

    # Step 5 — Extract urgency from explanation
    urgency = "LOW"
    if "URGENCY: HIGH"   in explanation: urgency = "HIGH"
    elif "URGENCY: MEDIUM" in explanation: urgency = "MEDIUM"

    # Clean urgency line from visible output
    clean_explanation = explanation.replace("URGENCY: HIGH","").replace(
        "URGENCY: MEDIUM","").replace("URGENCY: LOW","").strip()

    print(f"[FIR Explainer] Done. Urgency: {urgency} | Sections: {sections}")

    return {
        "status":      "success",
        "fir_data":    fir_data,
        "confidence":  round(confidence, 2),
        "explanation": clean_explanation,
        "urgency":     urgency,
        "sections":    sections,
        "law":         law,
        "language":    language
    }