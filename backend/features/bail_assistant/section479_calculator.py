import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from features.bail_assistant.state import BailState
from core.rag.chromadb_client import bns_collection, ipc_collection


MAX_SENTENCES = {
    # BNS sections → max sentence years (999 = life/death)
    "101": 999, "102": 999, "103": 999,
    "115": 1,   "118": 7,   "126": 3,
    "303": 3,   "304": 7,   "305": 10,
    "316": 3,   "318": 3,   "319": 7,
    "336": 2,   "351": 2,
    "63":  999, "64":  999,
    # IPC sections (for backward compat)
    "302": 999, "307": 10, "376": 999,
    "379": 3,   "420": 7,  "406": 3,
    "323": 1,   "324": 3,  "498A": 3,
}

NON_BAILABLE_ALWAYS = {"101","102","103","63","64","302","307","376"}


def get_max_sentence(sections: list, law: str) -> tuple:
    max_yrs   = 0
    worst_sec = None

    for sec in sections:
        clean = sec.replace("BNS","").replace("IPC","").replace("Section","").strip()
        yrs   = MAX_SENTENCES.get(clean, 3)
        if yrs > max_yrs:
            max_yrs   = yrs
            worst_sec = clean

    return max_yrs, worst_sec


def section479_calculator_agent(state: BailState) -> BailState:
    fir_data          = state["fir_data"]
    months_in_custody = state["months_in_custody"]
    is_first_offender = state["is_first_offender"]
    law               = state["applicable_law"]
    sections          = fir_data.get("sections_charged", [])

    max_sentence_yrs, worst_section = get_max_sentence(sections, law)

    print(f"[S.479 Calc] Sections: {sections} | Max sentence: {max_sentence_yrs}yrs | "
          f"In custody: {months_in_custody}mo | First offender: {is_first_offender}")

    # Capital/life offences — Section 479 does not apply
    if max_sentence_yrs >= 999:
        return {
            **state,
            "bail_type": "standard",
            "bail_eligibility": {
                "eligible":   False,
                "reason":     "Charged with offence punishable by death or life imprisonment. "
                              "Section 479 does not apply. Standard bail arguments apply.",
                "section":    "BNSS Section 480" if law == "BNS" else "CrPC Section 437",
                "max_years":  "Life/Death",
                "months_served": months_in_custody
            }
        }

    max_months = max_sentence_yrs * 12

    # Threshold: 1/3 for first offenders, 1/2 for others
    threshold     = max_months / 3 if is_first_offender else max_months / 2
    threshold_pct = round((1/3 * 100) if is_first_offender else 50)
    served_pct    = round((months_in_custody / max_months) * 100, 1)

    bail_section = "BNSS Section 479" if law == "BNS" else "CrPC Section 436A"

    if months_in_custody >= threshold:
        return {
            **state,
            "bail_type": "section479",
            "bail_eligibility": {
                "eligible":      True,
                "reason": (
                    f"Accused has served {months_in_custody} months "
                    f"({served_pct}% of {max_sentence_yrs}-year max sentence). "
                    f"Threshold for {'first-time offender' if is_first_offender else 'accused'}: "
                    f"{threshold_pct}%. Bail is a RIGHT under {bail_section}."
                ),
                "section":       bail_section,
                "max_years":     max_sentence_yrs,
                "months_served": months_in_custody,
                "threshold_pct": threshold_pct,
                "served_pct":    served_pct,
                "is_first_offender": is_first_offender
            }
        }
    else:
        remaining = round(threshold - months_in_custody)
        return {
            **state,
            "bail_type": "standard",
            "bail_eligibility": {
                "eligible":   False,
                "reason": (
                    f"Accused has served {months_in_custody} months "
                    f"({served_pct}% of {max_sentence_yrs}-year max). "
                    f"Needs {threshold_pct}% to qualify under {bail_section}. "
                    f"Approximately {remaining} more months needed. "
                    f"Standard bail arguments apply under "
                    f"{'BNSS Section 480' if law == 'BNS' else 'CrPC Section 437'}."
                ),
                "section":    "BNSS Section 480" if law == "BNS" else "CrPC Section 437",
                "max_years":  max_sentence_yrs,
                "months_served":    months_in_custody,
                "months_remaining": remaining,
                "served_pct": served_pct
            }
        }