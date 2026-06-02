import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.rag.law_router_util import detect_applicable_law
from features.bail_assistant.state import BailState


def law_router_agent(state: BailState) -> BailState:
    fir_date = state["fir_data"].get("date_of_fir", "")
    applicable_law = detect_applicable_law(fir_date)

    print(f"[Law Router] FIR date: {fir_date} → Applicable law: {applicable_law}")

    return {**state, "applicable_law": applicable_law}