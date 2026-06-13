"""
Runs once on server startup to build the ChromaDB knowledge base.
Called before uvicorn starts via the start command.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def build_if_empty():
    from core.rag.chromadb_client import bns_collection, rights_collection, mapping_collection

    # Check if already built
    if bns_collection.count() > 0:
        print(f"[Startup] Knowledge base already built ({bns_collection.count()} BNS sections). Skipping.")
        return

    print("[Startup] Building knowledge base...")

    # BNS sections
    data_path = os.path.join(os.path.dirname(__file__), "data", "bns_sections.json")
    with open(data_path, encoding="utf-8") as f:
        sections = json.load(f)

    docs, metas, ids = [], [], []
    for s in sections:
        doc = f"Section {s['section']} BNS — {s['title']}: {s['text']} Plain language: {s['plain_language']}"
        docs.append(doc)
        metas.append({
            "section":            s["section"],
            "title":              s["title"],
            "max_sentence_years": int(s["max_sentence_years"]),
            "bailable":           str(s["bailable"]),
            "law":                s["law"]
        })
        ids.append(f"BNS_{s['section']}")
    bns_collection.add(documents=docs, metadatas=metas, ids=ids)
    print(f"[Startup] BNS: {len(sections)} sections loaded")

    # Rights
    rights = [
        {"id":"r001","text":"Right to know reason of arrest — BNSS Section 47: Every person arrested must be informed of the grounds of arrest immediately.","category":"arrest"},
        {"id":"r002","text":"Right to inform family — BNSS Section 50: The arrested person has the right to have one friend or relative informed of the arrest without delay.","category":"arrest"},
        {"id":"r003","text":"Right to lawyer — BNSS Section 41D: Every person arrested has the right to meet an advocate of their choice during interrogation.","category":"legal_aid"},
        {"id":"r004","text":"Right against 24-hour detention — BNSS Section 57: No person shall be detained in custody for more than 24 hours without being produced before a magistrate.","category":"detention"},
        {"id":"r005","text":"Right to bail for bailable offences — BNSS Section 478: When any person accused of a bailable offence is arrested, they shall be released on bail as a right.","category":"bail"},
        {"id":"r006","text":"Section 479 BNSS — bail after serving half sentence: Undertrial prisoners who have served half (or one-third for first offenders) of maximum sentence are entitled to bail as a right.","category":"bail"},
        {"id":"r007","text":"Right to free legal aid — Article 39A Constitution: The State shall ensure that the operation of the legal system promotes justice and shall provide free legal aid to those who cannot afford it.","category":"legal_aid"},
        {"id":"r008","text":"Women arrest rights — BNSS Section 46: No woman shall be arrested after sunset and before sunrise. Arrest shall be made by a female police officer only.","category":"women"},
        {"id":"r009","text":"Right against self-incrimination — Article 20(3) Constitution: No person accused of any offence shall be compelled to be a witness against himself.","category":"interrogation"},
        {"id":"r010","text":"Juvenile rights — Juvenile Justice Act: A child in conflict with law cannot be sent to jail. They must be produced before Juvenile Justice Board, not regular court.","category":"juvenile"},
    ]
    rights_collection.add(
        documents=[r["text"] for r in rights],
        metadatas=[{"id": r["id"], "category": r["category"]} for r in rights],
        ids=[r["id"] for r in rights]
    )
    print(f"[Startup] Rights: {len(rights)} entries loaded")

    # IPC-BNS mapping
    mapping = [
        {"id":"m001","text":"IPC Section 302 Murder maps to BNS Section 101 Murder.","ipc":"302","bns":"101"},
        {"id":"m002","text":"IPC Section 307 Attempt to murder maps to BNS Section 109.","ipc":"307","bns":"109"},
        {"id":"m003","text":"IPC Section 376 Rape maps to BNS Section 63.","ipc":"376","bns":"63"},
        {"id":"m004","text":"IPC Section 379 Theft maps to BNS Section 303.","ipc":"379","bns":"303"},
        {"id":"m005","text":"IPC Section 420 Cheating maps to BNS Section 318.","ipc":"420","bns":"318"},
        {"id":"m006","text":"IPC Section 406 Criminal breach of trust maps to BNS Section 316.","ipc":"406","bns":"316"},
        {"id":"m007","text":"IPC Section 323 Voluntarily causing hurt maps to BNS Section 115.","ipc":"323","bns":"115"},
        {"id":"m008","text":"IPC Section 498A Cruelty by husband maps to BNS Section 85.","ipc":"498A","bns":"85"},
    ]
    mapping_collection.add(
        documents=[m["text"] for m in mapping],
        metadatas=[{"ipc": m["ipc"], "bns": m["bns"]} for m in mapping],
        ids=[m["id"] for m in mapping]
    )
    print(f"[Startup] Mapping: {len(mapping)} entries loaded")
    print("[Startup] Knowledge base ready!")
    # Preload EasyOCR model so first user request is fast
    print("[Startup] Preloading EasyOCR model...")
    try:
        from core.ocr.gemini_vision import get_ocr_reader
        get_ocr_reader()
        print("[Startup] EasyOCR ready.")
    except Exception as e:
        print(f"[Startup] EasyOCR preload warning: {e}")
if __name__ == "__main__":
    build_if_empty()