import json, os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chromadb_client import bns_collection, ipc_collection, rights_collection

def build_bns():
    with open("../../data/bns_sections.json") as f:
        sections = json.load(f)
    docs, metas, ids = [], [], []
    for s in sections:
        doc = f"Section {s['section']} BNS — {s['title']}: {s['text']} Plain language: {s['plain_language']}"
        docs.append(doc)
        metas.append({"section": s["section"], "title": s["title"],
                      "max_sentence_years": s["max_sentence_years"],
                      "bailable": s["bailable"], "law": s["law"]})
        ids.append(f"BNS_{s['section']}")
    bns_collection.add(documents=docs, metadatas=metas, ids=ids)
    print(f"BNS: {len(sections)} sections loaded")

def build_rights():
    rights = [
        {"id":"right_001","text":"Right to know reason of arrest — BNSS Section 47: Every person arrested must be informed of the grounds of arrest immediately.","category":"arrest"},
        {"id":"right_002","text":"Right to inform family — BNSS Section 50: The arrested person has the right to have one friend or relative informed of the arrest without delay.","category":"arrest"},
        {"id":"right_003","text":"Right to lawyer — BNSS Section 41D: Every person arrested has the right to meet an advocate of their choice during interrogation.","category":"legal_aid"},
        {"id":"right_004","text":"Right against 24-hour detention — BNSS Section 57: No person shall be detained in custody for more than 24 hours without being produced before a magistrate.","category":"detention"},
        {"id":"right_005","text":"Right to bail for bailable offences — BNSS Section 478: When any person accused of a bailable offence is arrested, they shall be released on bail as a right.","category":"bail"},
        {"id":"right_006","text":"Right to free legal aid — Article 39A Constitution: The State shall ensure that the operation of the legal system promotes justice on a basis of equal opportunity, and shall provide free legal aid to those who cannot afford it.","category":"legal_aid"},
        {"id":"right_007","text":"Women arrest rights — BNSS Section 46: No woman shall be arrested after sunset and before sunrise, and where such exceptional circumstances exist the arrest shall be made by a female police officer only.","category":"women"},
        {"id":"right_008","text":"Right against self-incrimination — Article 20(3) Constitution: No person accused of any offence shall be compelled to be a witness against himself.","category":"interrogation"},
    ]
    docs = [r["text"] for r in rights]
    metas = [{"id": r["id"], "category": r["category"]} for r in rights]
    ids = [r["id"] for r in rights]
    rights_collection.add(documents=docs, metadatas=metas, ids=ids)
    print(f"Rights: {len(rights)} entries loaded")

if __name__ == "__main__":
    print("Building knowledge base...")
    build_bns()
    build_rights()
    print("Done! Knowledge base ready.")