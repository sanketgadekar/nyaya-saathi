import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.llm.groq_client import call_llm


# Pre-loaded legal aid directory
# In production this comes from Supabase — for now hardcoded for testing
LEGAL_AID_DIRECTORY = [
    {
        "name":           "DLSA Nashik — District Legal Services Authority",
        "type":           "NALSA",
        "district":       "Nashik",
        "state":          "Maharashtra",
        "address":        "District Court Complex, Nashik, Maharashtra 422001",
        "phone":          "0253-2310234",
        "specialisation": ["bail","criminal","undertrial","general"],
        "free":           True,
        "timing":         "Mon-Sat 10am-5pm"
    },
    {
        "name":           "Maharashtra State Legal Services Authority (MSLSA)",
        "type":           "SLSA",
        "district":       "All Maharashtra",
        "state":          "Maharashtra",
        "address":        "Bombay High Court Campus, Mumbai 400001",
        "phone":          "022-22630941",
        "specialisation": ["bail","criminal","civil","family","general"],
        "free":           True,
        "timing":         "Mon-Fri 10am-5pm"
    },
    {
        "name":           "Majlis Manch — Women's Legal Aid",
        "type":           "NGO",
        "district":       "Mumbai / Pan Maharashtra",
        "state":          "Maharashtra",
        "address":        "Majlis, Mumbai",
        "phone":          "022-23755696",
        "specialisation": ["domestic_violence","498a","women","divorce","maintenance"],
        "free":           True,
        "timing":         "Mon-Sat 10am-6pm"
    },
    {
        "name":           "Tele-Law CSC Centre — Nashik",
        "type":           "Tele-Law",
        "district":       "Nashik",
        "state":          "Maharashtra",
        "address":        "Common Service Centre, Nashik Road, Nashik",
        "phone":          "1800-103-3933",
        "specialisation": ["general","rti","consumer","criminal"],
        "free":           True,
        "timing":         "Mon-Sat 9am-6pm"
    },
    {
        "name":           "NALSA Toll-Free Helpline",
        "type":           "Helpline",
        "district":       "All India",
        "state":          "All India",
        "address":        "National Legal Services Authority, New Delhi",
        "phone":          "15100",
        "specialisation": ["general","bail","undertrial","criminal","civil"],
        "free":           True,
        "timing":         "24/7"
    },
    {
        "name":           "Nyaya Bandhu Pro-Bono Portal",
        "type":           "Pro-Bono",
        "district":       "All India",
        "state":          "All India",
        "address":        "Online — nyayabandhu.gov.in",
        "phone":          "Apply online at nyayabandhu.gov.in",
        "specialisation": ["civil","criminal","family","property","general"],
        "free":           True,
        "timing":         "Online 24/7"
    },
]


def detect_case_type(situation: str) -> list:
    keywords = {
        "bail":             ["bail","arrested","jail","custody","fir","undertrial"],
        "domestic_violence":["domestic","husband","wife","abuse","violence","dowry","498"],
        "consumer":         ["consumer","product","defect","refund","fraud","company"],
        "rti":              ["rti","information","government","record","document"],
        "women":            ["woman","wife","divorce","maintenance","harassment"],
        "criminal":         ["arrest","case","fir","police","court","crime"],
        "civil":            ["property","land","contract","dispute","money"],
        "family":           ["divorce","custody","child","maintenance","alimony"],
    }

    sit_lower = situation.lower()
    detected  = []

    for case_type, words in keywords.items():
        if any(w in sit_lower for w in words):
            detected.append(case_type)

    return detected if detected else ["general"]


def find_aid(situation: str, district: str, state: str) -> dict:
    print(f"[Legal Aid] Situation: {situation[:50]} | District: {district}")

    case_types = detect_case_type(situation)
    print(f"[Legal Aid] Detected case types: {case_types}")

    # Score each aid organisation
    scored = []
    for org in LEGAL_AID_DIRECTORY:
        score = 0

        # Location match
        if district.lower() in org["district"].lower():
            score += 3
        if state.lower() in org["state"].lower():
            score += 2
        if org["district"] == "All India" or org["state"] == "All India":
            score += 1

        # Specialisation match
        for ct in case_types:
            if ct in org["specialisation"]:
                score += 2

        scored.append({"org": org, "score": score})

    # Sort by score and take top 3
    scored.sort(key=lambda x: x["score"], reverse=True)
    top3 = [item["org"] for item in scored[:3]]

    # Generate what to say when calling
    system_prompt = "You are a legal aid advisor. Write a 2-sentence script of what to say when calling a legal aid helpline. Be specific to their situation. Simple language."
    script = call_llm(
        system_prompt,
        f"Situation: {situation}\nWrite what to say when calling for legal help.",
        temperature=0.3
    )

    print(f"[Legal Aid] Found {len(top3)} organisations")

    return {
        "status":      "success",
        "case_types":  case_types,
        "district":    district,
        "state":       state,
        "options":     top3,
        "what_to_say": script,
        "situation":   situation
    }