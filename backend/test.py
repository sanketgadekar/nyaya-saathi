import sys
import os

sys.path.insert(0, os.getcwd())

print("=" * 50)
print("FIX 1 — Hinglish detection")
print("=" * 50)

from features.multilingual_chat.agent import detect_language_smart

tests = [
    ("Mujhe bail kaise milegi?", "Hindi"),
    ("My husband was arrested yesterday", "English"),
    ("Police ne mujhe arrest kiya hai", "Hindi"),
    ("What are my rights?", "English"),
    ("Bail application chahiye mujhe", "Hindi"),
]

all_pass = True

for text, expected in tests:
    result = detect_language_smart(text)
    status = "✓" if result == expected else "✗ FAIL"

    print(
        f'  {status} | "{text[:40]}" → {result} '
        f'(expected {expected})'
    )

    if result != expected:
        all_pass = False

print("Detection:", "ALL PASS" if all_pass else "SOME FAILED")

print()
print("=" * 50)
print("FIX 2 — Document drafter no [VERIFY] flags")
print("=" * 50)

from features.document_drafter.router import route_and_draft

d = route_and_draft(
    situation=(
        "I was arrested for theft and need bail. "
        "I have been in custody for 14 months."
    ),
    doc_type="bail",
    language="English",
    user_details={
        "name": "Raju Sharma",
        "address": "Nashik Road, Nashik, Maharashtra",
        "district": "Nashik",
        "state": "Maharashtra",
    },
)

print(
    "Flagged sections:",
    len(d["flagged"]),
    "(target: 0)"
)

print(
    "Confidence:",
    d["confidence"],
    "(target: 1.0)"
)

print()
print("--- First 400 chars of draft ---")
print(d["draft"][:400])
print("--------------------------------")

if "[VERIFY WITH LAWYER]" not in d["draft"]:
    print("No [VERIFY] flags found — Fix 2 PASSED")
else:
    print("Still has [VERIFY] flags — check system prompt")