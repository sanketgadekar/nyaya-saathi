import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.rag.chromadb_client  import (
    bns_collection, ipc_collection,
    rights_collection, precedents_collection,
    query_law, query_rights, query_precedents
)
from core.rag.law_router_util  import detect_applicable_law
from core.llm.groq_client      import call_llm


def explain_sections(sections: list, fir_date: str) -> str:
    """
    Takes a list of FIR sections and the FIR date.
    Returns a plain-language explanation of all charges.
    """
    law = detect_applicable_law(fir_date)

    if not sections:
        return "No sections found in the FIR. Please verify the image quality."

    # Retrieve plain-language info for each section
    retrieved = []
    for sec in sections:
        clean   = sec.replace("BNS","").replace("IPC","").replace("Section","").strip()
        results = query_law(f"section {clean} {law} punishment bailable", law, n=1)
        retrieved.extend(results)

    context = "\n".join(retrieved) if retrieved else "Section details not found in database."

    # Generate plain explanation using Groq
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
    Sections charged: {', '.join(sections)}
    Applicable law: {law}

    Section information from legal database:
    {context}

    Explain these charges in simple language.
    """

    explanation = call_llm(system_prompt, user_prompt, temperature=0.3)
    return explanation


def get_bail_context(sections: list, law: str) -> list:
    """
    Retrieves relevant law chunks for bail application drafting.
    """
    results = []
    for section in sections:
        clean = section.replace("BNS","").replace("IPC","").replace("Section","").strip()
        found = query_law(f"bail section {clean} punishment", law, n=2)
        results.extend(found)

    # Always add bail provisions
    bail_provisions = query_law("bail rights section 479 478 480 undertrial", law, n=3)
    results.extend(bail_provisions)

    # Deduplicate
    return list(dict.fromkeys(results))


def get_rights_for_situation(situation: str) -> list:
    return query_rights(situation, n=5)


def get_precedents_for_offence(offence_description: str) -> list:
    return query_precedents(offence_description, n=3)