import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import shutil, uuid

load_dotenv()

app = FastAPI(title="Nyaya Saathi API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("output",  exist_ok=True)
os.makedirs("legal_db", exist_ok=True)

# ── Request models ──────────────────────────────────────────────────────────

class RightsRequest(BaseModel):
    situation: str
    language:  str = "English"

class ChatRequest(BaseModel):
    message:  str
    language: str = "English"
    history:  list = []

class DocumentRequest(BaseModel):
    situation:    str
    document_type: str = "auto"
    language:     str = "English"
    user_details: dict = {}

class BailRequest(BaseModel):
    months_in_custody:    int
    is_first_offender:    bool = True
    language:             str  = "English"

class LegalAidRequest(BaseModel):
    situation: str
    district:  str
    state:     str

class ReminderRequest(BaseModel):
    cnr_number: str
    phone:      str
    name:       str


# ── Route 1: FIR Explainer ───────────────────────────────────────────────────

@app.post("/api/explain-fir")
async def explain_fir(
    file:     UploadFile = File(...),
    language: str        = Form(default="English")
):
    ext      = file.filename.split(".")[-1]
    filename = f"uploads/{uuid.uuid4()}.{ext}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        from features.fir_explainer.agent import explain_fir as run_explainer
        result = run_explainer(filename, language)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@app.post("/api/my-rights")
async def my_rights(req: RightsRequest):
    started = time.perf_counter()
    stage = "initialization"

    try:
        from core.rag.retriever import query_rights
        from core.llm.groq_client import call_llm
        from core.translation.translator import translate_text

        # Stage 1: Retrieve relevant legal rights
        stage = "retrieval"
        step_started = time.perf_counter()
        logger.info("my-rights: retrieval started")

        retrieved = query_rights(req.situation)
        context = "\n".join(retrieved)

        logger.info(
            "my-rights: retrieval completed in %.2fs; documents=%d",
            time.perf_counter() - step_started,
            len(retrieved),
        )

        if not context.strip():
            raise RuntimeError("Rights retrieval returned empty context")

        # Stage 2: Generate the legal explanation
        stage = "llm"
        step_started = time.perf_counter()
        logger.info("my-rights: LLM request started")

        answer = call_llm(
            system_prompt=(
                "You are a legal rights information assistant for "
                "Indian citizens. Use ONLY the rights listed in the "
                "context. Explain which rights may apply, using "
                "simple language and exact section numbers. "
                "Do not invent rights not present in the context. "
                "If the context is insufficient, say so."
            ),
            user_prompt=(
                f"Situation: {req.situation}\n\n"
                f"Context:\n{context}"
            ),
        )

        logger.info(
            "my-rights: LLM completed in %.2fs",
            time.perf_counter() - step_started,
        )

        if not answer or not answer.strip():
            raise RuntimeError("LLM returned an empty answer")

        # Stage 3: Translate only when necessary
        if req.language != "English":
            stage = "translation"
            step_started = time.perf_counter()
            logger.info("my-rights: translation started")

            answer = translate_text(answer, req.language)

            logger.info(
                "my-rights: translation completed in %.2fs",
                time.perf_counter() - step_started,
            )

        logger.info(
            "my-rights: completed successfully in %.2fs",
            time.perf_counter() - started,
        )

        return {
            "status": "success",
            "rights": answer,
            "language": req.language,
        }

    except Exception as exc:
        logger.exception(
            "my-rights failed at stage=%s after %.2fs (%s)",
            stage,
            time.perf_counter() - started,
            type(exc).__name__,
        )

        raise HTTPException(status_code=502,
            detail=f"Rights service failed during {stage}",
        ) from exc
# ── Route 3: Multilingual Legal Chat ────────────────────────────────────────

@app.post("/api/legal-chat")
async def legal_chat(req: ChatRequest):
    from langdetect                  import detect
    from core.rag.retriever          import query_law, query_rights
    from core.llm.groq_client        import call_llm
    from core.translation.translator import translate_text

    try:
        detected_lang = detect(req.message)
    except Exception:
        detected_lang = "en"

    retrieved = query_law(req.message) + query_rights(req.message)
    context   = "\n".join(retrieved[:5])

    history_text = ""
    for turn in req.history[-4:]:
        history_text += f"User: {turn.get('user','')}\nAssistant: {turn.get('assistant','')}\n"

    answer = call_llm(
        system_prompt=(
            "You are Nyaya Saathi, an Indian legal accessibility assistant. "
            "Answer ONLY based on Indian law. Use the context provided. "
            "Be simple, clear, and practical. Always mention relevant section numbers. "
            "If you don't know, say so — never guess. "
            f"Respond in the same language as the user's message."
        ),
        user_prompt=(
            f"Previous conversation:\n{history_text}\n"
            f"User message: {req.message}\n\n"
            f"Legal context:\n{context}"
        ),
        temperature=0.3
    )

    return {"status": "success", "answer": answer, "detected_language": detected_lang}


# ── Route 4: Document Drafter ────────────────────────────────────────────────

@app.post("/api/draft-document")
async def draft_document(req: DocumentRequest):
    from features.document_drafter.router import route_and_draft
    result = route_and_draft(
        req.situation,
        req.document_type,
        req.language,
        req.user_details
    )
    return result


# ── Route 5: Bail Application (core pipeline) ───────────────────────────────

@app.post("/api/bail-application")
async def bail_application(
    file:              UploadFile = File(...),
    months_in_custody: int        = Form(...),
    is_first_offender: bool       = Form(default=True),
    language:          str        = Form(default="English")
):
    ext      = file.filename.split(".")[-1]
    filename = f"uploads/{uuid.uuid4()}.{ext}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        from features.bail_assistant.pipeline import run_bail_pipeline
        result = run_bail_pipeline(filename, language, months_in_custody, is_first_offender)
        return result
    finally:
        if os.path.exists(filename):
            os.remove(filename)


# ── Route 6: Download PDF ────────────────────────────────────────────────────

@app.get("/api/download-pdf/{filename}")
async def download_pdf(filename: str):
    path = f"output/{filename}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(path, media_type="application/pdf",
                        filename=filename)


# ── Route 7: Legal Aid Connector ─────────────────────────────────────────────

@app.post("/api/find-legal-aid")
async def find_legal_aid(req: LegalAidRequest):
    from features.legal_aid_connector.matcher import find_aid
    result = find_aid(req.situation, req.district, req.state)
    return result


# ── Route 8: Court Reminders ─────────────────────────────────────────────────

@app.post("/api/register-reminder")
async def register_reminder(req: ReminderRequest):
    from features.court_reminders.njdg_fetcher import fetch_case_status
    from features.court_reminders.scheduler    import schedule_reminders

    case_data = fetch_case_status(req.cnr_number)
    if not case_data:
        return {"status": "error", "message": "Case not found in NJDG. Check CNR number."}

    schedule_reminders(req.cnr_number, req.phone, req.name, case_data)
    return {"status": "success", "case_data": case_data,
            "message": f"Reminders set for {req.name}. You will get WhatsApp alerts."}


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Nyaya Saathi API is running",
            "docs": "/docs", "version": "1.0.0"}