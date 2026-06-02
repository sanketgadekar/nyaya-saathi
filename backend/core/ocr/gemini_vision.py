import os, base64, json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_fir_data(image_path: str) -> dict:
    model = genai.GenerativeModel("gemini-2.0-flash")
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    prompt = """
    This is an Indian FIR (First Information Report).
    Extract these fields and return ONLY a valid JSON object, nothing else:
    {
        "fir_number": "string or null",
        "police_station": "string or null",
        "district": "string or null",
        "state": "string or null",
        "date_of_fir": "DD/MM/YYYY or null",
        "date_of_offence": "DD/MM/YYYY or null",
        "accused_name": "string or null",
        "accused_address": "string or null",
        "sections_charged": ["list", "of", "sections"],
        "complainant_name": "string or null",
        "brief_facts": "one paragraph summary or null"
    }
    Return ONLY the JSON. No explanation. No markdown. No extra text.
    """

    response = model.generate_content([
        prompt,
        {"mime_type": "image/jpeg", "data": image_data}
    ])

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def check_confidence(data: dict) -> float:
    required = ["fir_number", "sections_charged", "accused_name", "date_of_fir"]
    filled = sum(1 for f in required if data.get(f))
    return filled / len(required)