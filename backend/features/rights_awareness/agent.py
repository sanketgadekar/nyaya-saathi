import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.rag.chromadb_client    import query_rights
from core.llm.groq_client        import call_llm
from core.translation.translator import translate_text


def get_rights(situation: str, language: str = "English") -> dict:
    print(f"[Rights Awareness] Situation: {situation[:60]}...")

    # Step 1 — Retrieve relevant rights from ChromaDB
    retrieved = query_rights(situation, n=5)
    context   = "\n".join(retrieved) if retrieved else ""

    # Step 2 — Hardcoded critical rights always shown
    always_show = """
    ALWAYS INCLUDE THESE CORE RIGHTS:
    - BNSS Section 47: Right to know reason of arrest immediately
    - BNSS Section 50: Right to inform one family member of arrest
    - BNSS Section 57: Cannot be detained more than 24 hours without magistrate order
    - Article 39A Constitution: Right to free legal aid if cannot afford lawyer
    - BNSS Section 41D: Right to meet a lawyer of your choice
    """

    system_prompt = """
    You are a legal rights advisor for Indian citizens.
    List the rights that apply to this person's situation.

    Format EXACTLY like this for each right:
    RIGHT: [Name of right]
    SECTION: [Exact BNSS/IPC/Constitution section]
    MEANING: [One sentence in simple language]
    ACTION: [What to do right now — one sentence]
    ---

    Be practical. These people need to act immediately.
    Use simple Hindi-friendly English. Short sentences only.
    """

    user_prompt = f"""
    Situation: {situation}

    Rights from legal database:
    {context}

    {always_show}

    List all applicable rights for this situation.
    """

    answer = call_llm(system_prompt, user_prompt, temperature=0.2)

    # Step 3 — Translate if needed
    if language != "English":
        answer = translate_text(answer, language)

    print(f"[Rights Awareness] Done. Retrieved {len(retrieved)} rights from RAG.")

    return {
        "status":   "success",
        "rights":   answer,
        "language": language,
        "situation": situation
    }