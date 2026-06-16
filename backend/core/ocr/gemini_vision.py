import json, re, os, base64
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq_client


def image_to_base64(image_path: str) -> tuple:
    """Convert image to base64 string and detect mime type."""
    ext = image_path.lower().split(".")[-1]
    mime_map = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "png": "image/png",  "webp": "image/webp"
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return b64, mime_type


def extract_fir_data(image_path: str) -> dict:
    """
    Extract FIR fields using Groq vision API.
    Uses llama-4-scout-17b-16e-instruct which supports image input.
    Zero memory overhead — API call only.
    """
    print("[OCR] Sending FIR image to Groq vision API...")

    client = get_groq_client()
    b64_image, mime_type = image_to_base64(image_path)

    prompt = """You are reading an Indian FIR (First Information Report).
Extract ALL fields from this document and return ONLY a valid JSON object.
No markdown, no explanation, no code blocks — just raw JSON.

Return exactly this structure:
{
    "fir_number": "string or null",
    "police_station": "string or null",
    "district": "string or null",
    "state": "string or null",
    "date_of_fir": "DD/MM/YYYY format or null",
    "date_of_offence": "DD/MM/YYYY format or null",
    "accused_name": "string or null",
    "accused_address": "string or null",
    "sections_charged": ["BNS 303", "BNS 318"],
    "complainant_name": "string or null",
    "brief_facts": "one paragraph or null"
}

For sections_charged: prefix with BNS if FIR date is after 01/07/2024, else IPC.
Return ONLY the JSON object. Nothing else."""

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{b64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )

        raw = response.choices[0].message.content.strip()
        print(f"[OCR] Groq vision raw response: {raw[:200]}")

        # Strip markdown fences if present
        if "```" in raw:
            lines = raw.split("\n")
            raw = "\n".join(
                l for l in lines
                if not l.strip().startswith("```")
            )

        data = json.loads(raw.strip())
        print(f"[OCR] Extracted: {json.dumps(data, indent=2)}")
        return data

    except json.JSONDecodeError as e:
        print(f"[OCR] JSON parse error: {e}. Raw: {raw[:300]}")
        return _fallback_extraction(raw)
    except Exception as e:
        print(f"[OCR] Groq vision error: {e}")
        return _empty_fir_data()


def _fallback_extraction(text: str) -> dict:
    """
    If JSON parsing fails, extract fields with regex from raw text.
    """
    print("[OCR] Using regex fallback extraction...")
    data = _empty_fir_data()

    # FIR number
    m = re.search(r'fir[_\s]*number["\s:]+([0-9/]+)', text, re.IGNORECASE)
    if m: data["fir_number"] = m.group(1).strip()

    # Date
    m = re.search(r'date[_\s]*of[_\s]*fir["\s:]+([0-9/]+)', text, re.IGNORECASE)
    if m: data["date_of_fir"] = m.group(1).strip()

    # Accused name
    m = re.search(r'accused[_\s]*name["\s:]+([^",\n]+)', text, re.IGNORECASE)
    if m: data["accused_name"] = m.group(1).strip().strip('"')

    # Sections
    sections = re.findall(r'(?:BNS|IPC)\s*\d+[A-Za-z]?', text, re.IGNORECASE)
    if sections:
        data["sections_charged"] = list(set(sections))
    else:
        data["sections_charged"] = ["BNS 303"]

    return data


def _empty_fir_data() -> dict:
    return {
        "fir_number": None,
        "police_station": None,
        "district": None,
        "state": None,
        "date_of_fir": None,
        "date_of_offence": None,
        "accused_name": None,
        "accused_address": None,
        "sections_charged": ["BNS 303"],
        "complainant_name": None,
        "brief_facts": None
    }


def check_confidence(data: dict) -> float:
    required = ["fir_number", "sections_charged", "accused_name", "date_of_fir"]
    filled   = sum(1 for f in required if data.get(f))
    return filled / len(required)