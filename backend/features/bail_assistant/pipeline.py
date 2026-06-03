import os, sys, uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langgraph.graph import StateGraph, END
from features.bail_assistant.state               import BailState
from features.bail_assistant.law_router          import law_router_agent
from features.bail_assistant.section479_calculator import section479_calculator_agent
from features.bail_assistant.prompts             import (
    BAIL_SYSTEM_PROMPT, BAIL_USER_PROMPT_TEMPLATE
)
from core.ocr.gemini_vision                      import extract_fir_data, check_confidence
from core.rag.retriever                          import get_bail_context, get_precedents_for_offence
from core.llm.groq_client                       import call_llm
from core.translation.translator                import translate_text
from core.pdf.generator                         import generate_bail_pdf


# ═══════════════════════════════════════════════════════════════════
# AGENT 1 — OCR Agent
# Reads the FIR photo using Gemini Vision
# Writes: fir_data, ocr_confidence
# ═══════════════════════════════════════════════════════════════════
def ocr_agent(state: BailState) -> BailState:
    print("[Agent 1: OCR] Reading FIR image...")

    try:
        fir_data   = extract_fir_data(state["fir_image_path"])
        confidence = check_confidence(fir_data)
        print(f"[Agent 1: OCR] Confidence: {confidence:.2f} | Sections: {fir_data.get('sections_charged')}")

        return {
            **state,
            "fir_data":        fir_data,
            "ocr_confidence":  confidence,
            "pipeline_status": "ocr_complete"
        }
    except Exception as e:
        return {
            **state,
            "error":           f"OCR failed: {str(e)}",
            "pipeline_status": "failed"
        }


# ═══════════════════════════════════════════════════════════════════
# AGENT 3 — RAG Retriever Agent
# Queries ChromaDB for relevant law + Supreme Court precedents
# Writes: retrieved_law, retrieved_precedents
# ═══════════════════════════════════════════════════════════════════
def rag_retriever_agent(state: BailState) -> BailState:
    print("[Agent 3: RAG] Retrieving law and precedents...")

    sections = state["fir_data"].get("sections_charged", [])
    law      = state["applicable_law"]

    retrieved_law         = get_bail_context(sections, law)
    retrieved_precedents  = get_precedents_for_offence(
        " ".join(sections) + " bail"
    )

    print(f"[Agent 3: RAG] Retrieved {len(retrieved_law)} law chunks, "
          f"{len(retrieved_precedents)} precedents")

    return {
        **state,
        "retrieved_law":         retrieved_law,
        "retrieved_precedents":  retrieved_precedents,
        "pipeline_status":       "rag_complete"
    }


# ═══════════════════════════════════════════════════════════════════
# AGENT 5 — Drafter Agent
# Uses Groq LLM to generate the bail application
# Only uses retrieved text — no hallucination
# Writes: draft_application, confidence_score, flagged_sections
# ═══════════════════════════════════════════════════════════════════
def drafter_agent(state: BailState) -> BailState:
    print("[Agent 5: Drafter] Generating bail application...")

    fir          = state["fir_data"]
    eligibility  = state["bail_eligibility"]
    law_chunks   = state["retrieved_law"]
    precedents   = state["retrieved_precedents"]

    user_prompt = BAIL_USER_PROMPT_TEMPLATE.format(
        fir_number              = fir.get("fir_number",     "Not specified"),
        police_station          = fir.get("police_station", "Not specified"),
        district                = fir.get("district",       "Not specified"),
        state                   = fir.get("state",          "Not specified"),
        date_of_fir             = fir.get("date_of_fir",    "Not specified"),
        accused_name            = fir.get("accused_name",   "The Applicant"),
        sections                = ", ".join(fir.get("sections_charged", [])),
        months_in_custody       = state["months_in_custody"],
        is_first_offender       = "Yes" if state["is_first_offender"] else "No",
        bail_type               = state["bail_type"],
        bail_eligibility_reason = eligibility.get("reason", ""),
        bail_section            = eligibility.get("section", ""),
        retrieved_law           = "\n".join(law_chunks[:6]),
        retrieved_precedents    = "\n".join(precedents[:3])
    )

    draft = call_llm(
        system_prompt = BAIL_SYSTEM_PROMPT,
        user_prompt   = user_prompt,
        temperature   = 0.2
    )

    # Detect flagged sections (where LLM couldn't find grounding)
    flagged = []
    for line in draft.split("\n"):
        if "[VERIFY" in line or "[FLAGGED" in line:
            flagged.append(line.strip())

    # Confidence: penalise for each flagged section
    confidence = max(0.6, 1.0 - (len(flagged) * 0.1))

    print(f"[Agent 5: Drafter] Draft length: {len(draft)} chars | "
          f"Flagged: {len(flagged)} | Confidence: {confidence:.2f}")

    return {
        **state,
        "draft_application": draft,
        "confidence_score":  round(confidence, 2),
        "flagged_sections":  flagged,
        "pipeline_status":   "draft_complete"
    }


# ═══════════════════════════════════════════════════════════════════
# AGENT 6 — Translator Agent
# Translates the draft to the user's chosen language
# Writes: translated_application
# ═══════════════════════════════════════════════════════════════════
def translator_agent(state: BailState) -> BailState:
    language = state["language"]
    draft    = state["draft_application"]

    print(f"[Agent 6: Translator] Translating to {language}...")

    if language == "English":
        translated = draft
    else:
        translated = translate_text(draft, language)

    return {
        **state,
        "translated_application": translated,
        "pipeline_status":        "translation_complete"
    }


# ═══════════════════════════════════════════════════════════════════
# AGENT 7 — PDF Generator Agent
# Builds court-formatted PDF using ReportLab
# Writes: pdf_filename, pdf_path
# ═══════════════════════════════════════════════════════════════════
def pdf_generator_agent(state: BailState) -> BailState:
    print("[Agent 7: PDF] Generating court-formatted PDF...")

    os.makedirs("output", exist_ok=True)
    filename = f"bail_application_{uuid.uuid4().hex[:8]}.pdf"
    path     = f"output/{filename}"

    generate_bail_pdf(
        application_text = state["translated_application"],
        fir_data         = state["fir_data"],
        bail_eligibility = state["bail_eligibility"],
        confidence_score = state["confidence_score"],
        flagged_sections = state["flagged_sections"],
        output_path      = path,
        language         = state["language"]
    )

    print(f"[Agent 7: PDF] PDF saved: {path}")

    return {
        **state,
        "pdf_filename":    filename,
        "pdf_path":        path,
        "pipeline_status": "completed"
    }


# ═══════════════════════════════════════════════════════════════════
# ROUTING FUNCTIONS — conditional edges in LangGraph
# ═══════════════════════════════════════════════════════════════════

def route_after_ocr(state: BailState) -> str:
    if state.get("error") or state.get("pipeline_status") == "failed":
        return "failed"
    if state["ocr_confidence"] < 0.5:
        return "low_confidence"
    return "continue"


def route_after_section479(state: BailState) -> str:
    bail_type = state.get("bail_type", "standard")
    if bail_type == "section479":
        return "section479_path"
    return "standard_path"


def handle_low_confidence(state: BailState) -> BailState:
    return {
        **state,
        "error": (
            "FIR image quality is too low to extract all required fields. "
            "Please upload a clearer photo with better lighting. "
            "All four fields must be visible: FIR number, accused name, "
            "sections charged, and date."
        ),
        "pipeline_status": "failed"
    }


def handle_failed(state: BailState) -> BailState:
    return {**state, "pipeline_status": "failed"}


# ═══════════════════════════════════════════════════════════════════
# BUILD THE LANGGRAPH STATE GRAPH
# This is the complete 7-agent pipeline wired together
# ═══════════════════════════════════════════════════════════════════

def build_bail_graph() -> StateGraph:
    graph = StateGraph(BailState)

    # Add all nodes (agents)
    graph.add_node("ocr",              ocr_agent)
    graph.add_node("law_router",       law_router_agent)
    graph.add_node("rag_retriever",    rag_retriever_agent)
    graph.add_node("section479_calc",  section479_calculator_agent)
    graph.add_node("drafter",          drafter_agent)
    graph.add_node("translator",       translator_agent)
    graph.add_node("pdf_generator",    pdf_generator_agent)
    graph.add_node("low_confidence",   handle_low_confidence)
    graph.add_node("failed",           handle_failed)

    # Entry point
    graph.set_entry_point("ocr")

    # After OCR — check confidence before continuing
    graph.add_conditional_edges(
        "ocr",
        route_after_ocr,
        {
            "continue":       "law_router",
            "low_confidence": "low_confidence",
            "failed":         "failed"
        }
    )

    # Low confidence and failed both end the pipeline
    graph.add_edge("low_confidence", END)
    graph.add_edge("failed",         END)

    # Law router always goes to RAG retriever
    graph.add_edge("law_router", "rag_retriever")

    # RAG retriever always goes to Section 479 calculator
    graph.add_edge("rag_retriever", "section479_calc")

    # Section 479 — both paths go to drafter
    # (drafter knows which type from state["bail_type"])
    graph.add_conditional_edges(
        "section479_calc",
        route_after_section479,
        {
            "section479_path": "drafter",
            "standard_path":   "drafter"
        }
    )

    # Linear from drafter to end
    graph.add_edge("drafter",       "translator")
    graph.add_edge("translator",    "pdf_generator")
    graph.add_edge("pdf_generator", END)

    return graph.compile()


# Cache compiled graph (expensive to rebuild each request)
_bail_graph = None

def get_bail_graph():
    global _bail_graph
    if _bail_graph is None:
        _bail_graph = build_bail_graph()
    return _bail_graph


# ═══════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT — called by main.py
# ═══════════════════════════════════════════════════════════════════

def run_bail_pipeline(
    image_path:        str,
    language:          str  = "English",
    months_in_custody: int  = 0,
    is_first_offender: bool = True
) -> dict:

    initial_state: BailState = {
        "fir_image_path":        image_path,
        "months_in_custody":     months_in_custody,
        "is_first_offender":     is_first_offender,
        "language":              language,
        "fir_data":              {},
        "ocr_confidence":        0.0,
        "applicable_law":        "BNS",
        "retrieved_law":         [],
        "retrieved_precedents":  [],
        "bail_type":             "standard",
        "bail_eligibility":      {},
        "draft_application":     "",
        "confidence_score":      0.0,
        "flagged_sections":      [],
        "translated_application": "",
        "pdf_filename":          "",
        "pdf_path":              "",
        "error":                 None,
        "pipeline_status":       "running"
    }

    print("\n" + "="*60)
    print("NYAYA SAATHI — BAIL PIPELINE STARTED")
    print("="*60)

    graph  = get_bail_graph()
    result = graph.invoke(initial_state)

    print("="*60)
    print(f"PIPELINE STATUS: {result['pipeline_status'].upper()}")
    print("="*60 + "\n")

    if result["pipeline_status"] == "failed":
        return {
            "status":  "error",
            "message": result.get("error", "Pipeline failed"),
        }

    return {
        "status":           "success",
        "pdf_filename":     result["pdf_filename"],
        "pdf_url":          f"/api/download-pdf/{result['pdf_filename']}",
        "bail_type":        result["bail_type"],
        "bail_eligibility": result["bail_eligibility"],
        "confidence_score": result["confidence_score"],
        "flagged_sections": result["flagged_sections"],
        "fir_data":         result["fir_data"],
        "applicable_law":   result["applicable_law"],
        "language":         language
    }