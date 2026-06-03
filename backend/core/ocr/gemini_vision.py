import os, base64, json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_fir_data(image_path: str) -> dict:

    with open(image_path, "rb") as f:
        image_bytes = f.read()

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

    response = client.models.generate_content(
        model   = "gemini-2.0-flash",
        contents= [
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt
        ]
    )

    raw = response.text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw   = "\n".join(lines[1:-1])

    return json.loads(raw.strip())


def check_confidence(data: dict) -> float:
    required = ["fir_number", "sections_charged", "accused_name", "date_of_fir"]
    filled   = sum(1 for f in required if data.get(f))
    return filled / len(required)