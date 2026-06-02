from typing import TypedDict, Optional


class BailState(TypedDict):

    # ── Input ──────────────────────────────────────────────────────────
    fir_image_path:     str
    months_in_custody:  int
    is_first_offender:  bool
    language:           str

    # ── Agent 1 output: OCR ────────────────────────────────────────────
    fir_data:           dict
    ocr_confidence:     float

    # ── Agent 2 output: Law router ─────────────────────────────────────
    applicable_law:     str        # "BNS" or "IPC"

    # ── Agent 3 output: RAG retriever ─────────────────────────────────
    retrieved_law:      list
    retrieved_precedents: list

    # ── Agent 4 output: Section 479 calculator ─────────────────────────
    bail_type:          str        # "section479", "standard", "bailable_as_right"
    bail_eligibility:   dict       # {eligible: bool, reason: str, section: str}

    # ── Agent 5 output: Drafter ────────────────────────────────────────
    draft_application:  str
    confidence_score:   float
    flagged_sections:   list

    # ── Agent 6 output: Translator ─────────────────────────────────────
    translated_application: str

    # ── Agent 7 output: PDF generator ─────────────────────────────────
    pdf_filename:       str
    pdf_path:           str

    # ── Error tracking ─────────────────────────────────────────────────
    error:              Optional[str]
    pipeline_status:    str        # "running", "completed", "failed"