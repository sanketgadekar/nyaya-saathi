from datetime import datetime

BNS_START_DATE = datetime(2024, 7, 1)

def detect_applicable_law(fir_date_str: str) -> str:
    if not fir_date_str:
        return "BNS"
    try:
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                fir_date = datetime.strptime(fir_date_str.strip(), fmt)
                return "BNS" if fir_date >= BNS_START_DATE else "IPC"
            except ValueError:
                continue
        return "BNS"
    except Exception:
        return "BNS"


def get_bail_section(law: str, bail_type: str) -> str:
    mapping = {
        "BNS": {
            "bailable":        "BNSS Section 478",
            "non_bailable":    "BNSS Section 480",
            "time_served":     "BNSS Section 479",
            "anticipatory":    "BNSS Section 482",
        },
        "IPC": {
            "bailable":        "CrPC Section 436",
            "non_bailable":    "CrPC Section 437",
            "time_served":     "CrPC Section 436A",
            "anticipatory":    "CrPC Section 438",
        }
    }
    return mapping.get(law, mapping["BNS"]).get(bail_type, "BNSS Section 479")