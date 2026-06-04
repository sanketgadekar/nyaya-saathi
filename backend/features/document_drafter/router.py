import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.llm.groq_client        import call_llm
from core.rag.chromadb_client    import query_law
from core.translation.translator import translate_text


# ── All supported document types ────────────────────────────────────────────

DOCUMENT_TYPES = {
    "bail":             "Bail Application under BNSS Section 479/480",
    "anticipatory":     "Anticipatory Bail Application under BNSS Section 482",
    "rti":              "RTI Application under Right to Information Act 2005",
    "consumer":         "Consumer Complaint under Consumer Protection Act 2019",
    "police_complaint": "Police Complaint / FIR Application",
    "dv_complaint":     "Domestic Violence Complaint under PWDVA 2005",
    "maintenance":      "Maintenance Application under BNSS Section 144",
    "legal_notice":     "Legal Notice",
    "affidavit":        "General Affidavit",
}

# Key legal names so LLM never has to guess them
LAW_NAMES = """
OFFICIAL LEGAL NAMES — use these exactly, never guess:
- Bail after serving sentence     → BNSS Section 479 of Bharatiya Nagarik Suraksha Sanhita 2023
- Bail for non-bailable offence   → BNSS Section 480 of Bharatiya Nagarik Suraksha Sanhita 2023
- Anticipatory bail               → BNSS Section 482 of Bharatiya Nagarik Suraksha Sanhita 2023
- Bailable offence bail as right  → BNSS Section 478 of Bharatiya Nagarik Suraksha Sanhita 2023
- RTI                             → Right to Information Act 2005, Section 6(1)
- Consumer complaint              → Consumer Protection Act 2019, Section 35
- Domestic violence               → Protection of Women from Domestic Violence Act 2005
- Maintenance                     → BNSS Section 144 (replaces CrPC Section 125)
- Free legal aid                  → Legal Services Authorities Act 1987, Article 39A Constitution
- Right to know arrest reason     → BNSS Section 47
- Right to lawyer                 → BNSS Section 41D
- Right against self-incrimination→ Article 20(3) Constitution of India
"""


# ── Auto-detect document type from situation ─────────────────────────────────

def detect_document_type(situation: str) -> str:
    keywords = {
        "bail": [
            "bail", "arrested", "jail", "custody", "undertrial",
            "police station", "locked up", "detained", "FIR filed"
        ],
        "anticipatory": [
            "anticipatory", "might be arrested", "fear of arrest",
            "arrest warning", "pre-arrest"
        ],
        "rti": [
            "rti", "right to information", "government information",
            "public record", "government document", "transparency"
        ],
        "consumer": [
            "consumer", "product", "defective", "refund", "service complaint",
            "cheated by company", "online shopping", "warranty", "fraud by seller"
        ],
        "police_complaint": [
            "complaint", "fir", "lodge fir", "report crime",
            "police complaint", "register case"
        ],
        "dv_complaint": [
            "domestic violence", "husband beating", "wife beating",
            "physical abuse", "dowry", "498a", "cruelty by husband",
            "harassment at home"
        ],
        "maintenance": [
            "maintenance", "alimony", "child support",
            "monthly support", "nafqa", "financial support after divorce"
        ],
        "legal_notice": [
            "legal notice", "warn someone", "demand money back",
            "send notice", "final warning"
        ],
        "affidavit": [
            "affidavit", "sworn statement", "declaration",
            "self declaration", "notarized"
        ],
    }

    sit_lower = situation.lower()
    scores    = {doc_type: 0 for doc_type in keywords}

    for doc_type, words in keywords.items():
        for word in words:
            if word in sit_lower:
                scores[doc_type] += 1

    best  = max(scores, key=scores.get)
    score = scores[best]

    # Default to legal_notice if nothing matched
    return best if score > 0 else "legal_notice"


# ── Core drafting function ───────────────────────────────────────────────────

def draft_document(
    situation:    str,
    doc_type:     str,
    language:     str  = "English",
    user_details: dict = {}
) -> dict:

    print(f"[Document Drafter] Type: {doc_type} | Language: {language}")

    # Get user details with safe defaults
    name      = user_details.get("name",    "The Applicant")
    address   = user_details.get("address", "[Address to be filled by applicant]")
    court     = user_details.get("court",   "The Honourable Judicial Magistrate")
    district  = user_details.get("district","[District]")
    state_nm  = user_details.get("state",   "[State]")
    phone     = user_details.get("phone",   "[Phone number]")

    # Retrieve relevant law from ChromaDB
    query        = f"{DOCUMENT_TYPES.get(doc_type, doc_type)} {situation}"
    context_list = query_law(query, "BNS", n=3)
    context_text = "\n".join(context_list) if context_list else "No specific context retrieved."

    # Build system prompt with all law names pre-loaded
    system_prompt = f"""
You are a senior legal document drafting expert specializing in Indian law.
You are drafting a {DOCUMENT_TYPES.get(doc_type, doc_type)}.

{LAW_NAMES}

DOCUMENT FORMAT — use this exact structure:
1. To: [Court/Authority name]
2. Subject: [Brief subject line]
3. Respectfully Submitted,
4. Facts of the Case: (numbered list)
5. Grounds: (numbered list — legal arguments)
6. Prayer/Relief Sought: (what you want the court to do)
7. Verification: (standard declaration)
8. Date and Place: [Date], [Place]
9. Applicant signature block: {name}

DRAFTING RULES:
1. Use only section names from the LAW NAMES list above — never guess section numbers
2. Refer to applicant as "{name}" consistently throughout
3. For unknown details: write [To be filled by applicant] — never write [VERIFY WITH LAWYER]
4. Use formal, polite legal language
5. Keep facts section factual — do not admit guilt
6. Always address the court respectfully
7. Prayer should be specific — exactly what relief is requested
"""

    user_prompt = f"""
Draft a complete {DOCUMENT_TYPES.get(doc_type, doc_type)}.

Applicant details:
- Full name: {name}
- Address: {address}
- Phone: {phone}
- District: {district}
- State: {state_nm}
- Court/Authority: {court}

Situation (as described by applicant):
{situation}

Additional details provided:
{user_details}

Legal context from database:
{context_text}

Draft the complete formal document now.
Begin with "To," on the first line.
"""

    # Call LLM
    draft = call_llm(
        system_prompt = system_prompt,
        user_prompt   = user_prompt,
        temperature   = 0.15   # Very low — legal documents need consistency
    )

    # Translate if not English
    if language != "English":
        print(f"[Document Drafter] Translating to {language}...")
        draft = translate_text(draft, language)

    # Count any remaining verify flags (should be near 0 now)
    flagged = [
        line.strip() for line in draft.split("\n")
        if "[VERIFY" in line or "[FLAGGED" in line
    ]

    confidence = round(max(0.7, 1.0 - len(flagged) * 0.1), 2)

    print(f"[Document Drafter] Done. "
          f"Length: {len(draft)} | Flagged: {len(flagged)} | Confidence: {confidence}")

    return {
        "status":        "success",
        "document_type": doc_type,
        "document_name": DOCUMENT_TYPES.get(doc_type, doc_type),
        "draft":         draft,
        "flagged":       flagged,
        "confidence":    confidence,
        "language":      language
    }


# ── Public entry point — called by main.py ───────────────────────────────────

def route_and_draft(
    situation:    str,
    doc_type:     str  = "auto",
    language:     str  = "English",
    user_details: dict = {}
) -> dict:

    # Auto-detect if not specified
    if doc_type == "auto":
        doc_type = detect_document_type(situation)
        print(f"[Document Router] Auto-detected type: {doc_type}")

    return draft_document(
        situation    = situation,
        doc_type     = doc_type,
        language     = language,
        user_details = user_details
    )