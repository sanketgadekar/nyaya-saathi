import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.chromadb_client import (
    bns_collection, ipc_collection,
    rights_collection, precedents_collection,
    query_law, query_rights, query_precedents
)


def explain_sections(sections: list, fir_date: str) -> str:
    from law_router_util import detect_applicable_law
    law = detect_applicable_law(fir_date)

    if not sections:
        return "No sections found in the FIR. Please verify the image quality."

    explanations = []
    for section in sections:
        clean = section.replace("BNS", "").replace("IPC", "").replace("Section", "").strip()
        results = query_law(f"section {clean}", law, n=1)

        if results:
            explanations.append(f"Section {section}: {results[0]}")
        else:
            explanations.append(
                f"Section {section}: Could not retrieve details. "
                f"Please verify with a lawyer. [FLAGGED]"
            )

    intro = (
        "Based on the FIR, here is what each charge means:\n\n"
    )
    return intro + "\n\n".join(explanations)


def get_bail_context(sections: list, law: str) -> list:
    results = []
    for section in sections:
        clean = section.replace("BNS","").replace("IPC","").replace("Section","").strip()
        found = query_law(f"bail section {clean} punishment", law, n=2)
        results.extend(found)

    bail_provisions = query_law("bail rights section 479 478 480", law, n=3)
    results.extend(bail_provisions)
    return list(dict.fromkeys(results))


def get_rights_for_situation(situation: str) -> list:
    return query_rights(situation, n=5)


def get_precedents_for_offence(offence_description: str) -> list:
    return query_precedents(offence_description, n=3)