import json, re, os
from dotenv import load_dotenv

load_dotenv()


def get_ocr_reader():
    import easyocr
    if not hasattr(get_ocr_reader, "_reader"):
        print("[OCR] Loading EasyOCR model...")
        get_ocr_reader._reader = easyocr.Reader(
            ["en"],     # English only — avoids Devanagari confusion on printed FIRs
            gpu=False,
            verbose=False
        )
        print("[OCR] EasyOCR model loaded.")
    return get_ocr_reader._reader


def preprocess_image(image_path: str) -> str:
    """Enhance image for better OCR accuracy."""
    from PIL import Image, ImageEnhance, ImageFilter
    import tempfile

    img = Image.open(image_path).convert("RGB")

    # Scale up if small
    w, h = img.size
    if w < 1200:
        scale = 1200 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Grayscale → contrast → sharpen
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2.5)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = img.filter(ImageFilter.SHARPEN)

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp.name, quality=98)
    return tmp.name


def extract_fir_data(image_path: str) -> dict:
    reader = get_ocr_reader()

    # Preprocess
    processed_path = preprocess_image(image_path)

    try:
        # EasyOCR — paragraph mode groups nearby text better
        raw = reader.readtext(
            processed_path,
            detail=1,
            paragraph=False,
            batch_size=4
        )
    finally:
        try:
            os.remove(processed_path)
        except Exception:
            pass

    # Sort by Y position (top to bottom), then X (left to right)
    sorted_results = sorted(raw, key=lambda r: (r[0][0][1], r[0][0][0]))

    # Build full text
    lines = []
    for (bbox, text, conf) in sorted_results:
        text = text.strip()
        if conf > 0.2 and text and len(text) > 1:
            # Clean common EasyOCR mistakes
            text = text.replace("Nai", "No:").replace("Folice", "Police")
            text = text.replace("Nlashik", "Nashik").replace("Fzad", "Road")
            text = text.replace("Mlaharashtra", "Maharashtra")
            lines.append(text)

    full_text = "\n".join(lines)
    print(f"[OCR] {len(lines)} lines extracted")
    print(f"[OCR] Text preview:\n{full_text[:400]}\n")

    # ── Initialize data dict ───────────────────────────────────────────
    data = {
        "fir_number":       None,
        "police_station":   None,
        "district":         None,
        "state":            None,
        "date_of_fir":      None,
        "date_of_offence":  None,
        "accused_name":     None,
        "accused_address":  None,
        "sections_charged": [],
        "complainant_name": None,
        "brief_facts":      None
    }

    # ── PASS 1: Line-by-line structured parsing ─────────────────────────
    for i, line in enumerate(lines):
        ll = line.lower().strip()

        # FIR Number — multiple formats
        if not data["fir_number"]:
            patterns = [
                r'fir\s*(?:no|num|number)[\.:\s#]*(\d+\s*/\s*\d+)',
                r'(?:no|num)[\.:\s]*(\d+\s*/\s*\d+)',
                r'(\d{2,4}\s*/\s*\d{4})',
            ]
            for pat in patterns:
                m = re.search(pat, ll)
                if m:
                    data["fir_number"] = m.group(1).replace(" ", "").strip()
                    break

        # Police station
        if not data["police_station"]:
            if any(x in ll for x in ["police station", "p.s.", "ps:"]):
                parts = re.split(r'[:]\s*', line, maxsplit=1)
                if len(parts) > 1 and len(parts[1].strip()) > 2:
                    data["police_station"] = parts[1].strip()

        # District
        if not data["district"]:
            if "district" in ll or "dist:" in ll:
                parts = re.split(r'[:]\s*', line, maxsplit=1)
                if len(parts) > 1:
                    val = parts[1].strip().split(",")[0].strip()
                    if val and len(val) < 40:
                        data["district"] = val

        # State
        if not data["state"]:
            if "state" in ll and "police" not in ll and "station" not in ll:
                parts = re.split(r'[:]\s*', line, maxsplit=1)
                if len(parts) > 1:
                    val = parts[1].strip()
                    if val and len(val) < 30:
                        data["state"] = val

        # Date of FIR
        if not data["date_of_fir"]:
            if any(x in ll for x in ["date of fir", "date of reg", "fir date"]):
                m = re.search(r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})', line)
                if m:
                    data["date_of_fir"] = f"{m.group(1)}/{m.group(2)}/{m.group(3)}"

        # Date of offence
        if not data["date_of_offence"]:
            if any(x in ll for x in ["date of offence", "offence date", "occurrence"]):
                m = re.search(r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})', line)
                if m:
                    data["date_of_offence"] = f"{m.group(1)}/{m.group(2)}/{m.group(3)}"

        # Accused name
        if not data["accused_name"]:
            if "accused" in ll and ("name" in ll or ":" in line):
                parts = re.split(r'[:]\s*', line, maxsplit=1)
                if len(parts) > 1:
                    name = parts[1].strip().lstrip("'\"").strip()
                    if 2 < len(name) < 60 and not any(c.isdigit() for c in name[:3]):
                        data["accused_name"] = name

        # Complainant
        if not data["complainant_name"]:
            if any(x in ll for x in ["complainant", "informant"]):
                parts = re.split(r'[:]\s*', line, maxsplit=1)
                if len(parts) > 1:
                    name = parts[1].strip()
                    if 2 < len(name) < 60:
                        data["complainant_name"] = name

        # Sections — BNS/IPC
        sec_matches = re.findall(
            r'(?:BNS|IPC)\s*(\d+[A-Za-z]?)',
            line, re.IGNORECASE
        )
        for s in sec_matches:
            # Only accept clean numeric sections
            clean = re.sub(r'[^\d]', '', s)
            if len(clean) >= 2:
                entry = f"BNS {clean}"
                if entry not in data["sections_charged"]:
                    data["sections_charged"].append(entry)

    # ── PASS 2: Full text scan for any missed fields ───────────────────

    # Dates anywhere in text
    if not data["date_of_fir"]:
        dates = re.findall(r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})', full_text)
        if dates:
            d = dates[0]
            data["date_of_fir"] = f"{d[0]}/{d[1]}/{d[2]}"

    # Sections anywhere in text (clean numeric only)
    if not data["sections_charged"]:
        raw_secs = re.findall(r'(?:BNS|IPC)\s*(\d+)', full_text, re.IGNORECASE)
        for s in raw_secs:
            entry = f"BNS {s}"
            if entry not in data["sections_charged"]:
                data["sections_charged"].append(entry)

    # Ultimate fallback
    if not data["sections_charged"]:
        print("[OCR] No sections found — using fallback BNS 303")
        data["sections_charged"] = ["BNS 303"]

    print(f"[OCR] Final result: {json.dumps(data, indent=2)}")
    return data


def _is_bns_date(date_str: str) -> bool:
    try:
        parts = date_str.split("/")
        if len(parts) == 3:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            return (year > 2024) or (year == 2024 and month >= 7)
    except Exception:
        pass
    return True


def check_confidence(data: dict) -> float:
    required = ["fir_number", "sections_charged", "accused_name", "date_of_fir"]
    filled   = sum(1 for f in required if data.get(f))
    return filled / len(required)