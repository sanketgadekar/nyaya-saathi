# ⚖️ Nyaya Saathi — AI Legal Accessibility Platform

> Justice should not depend on your wallet.

**Live Demo:** [nyaya-saathi.vercel.app](https://nyaya-saathi.vercel.app)
**Backend API:** [nyaya-saathi-backend.onrender.com/docs](https://nyaya-saathi-backend.onrender.com/docs)

Nyaya Saathi is a free, multilingual, agentic AI platform that gives every Indian citizen the legal tools that previously only money could buy — FIR explanation, rights awareness, document drafting, bail eligibility calculation, legal aid matching, and court date reminders. Built end-to-end with a 7-agent LangGraph pipeline grounded in Indian law (BNS, BNSS, IPC, Constitution).

---

## 📊 Why This Exists

| Statistic | Reality |
|---|---|
| 3.75 lakh+ | undertrials in Indian prisons — not yet convicted |
| 74% | of all prisoners in India are undertrials |
| 4 in 5 | Indians do not know their free legal rights exist |
| 5.4 crore | cases pending across Indian courts |
| ₹0 | what it costs to use Nyaya Saathi |

A new legal right — **Section 479 BNSS (2023)** — entitles undertrials who have served half (or one-third, for first-time offenders) of their maximum sentence to bail **as a right**, not at the court's discretion. The Supreme Court made this retrospective in August 2024. Most eligible undertrials don't know it exists. Nyaya Saathi finds them.

---

## ✨ Features

| # | Feature | What it does |
|---|---|---|
| 1 | **FIR Explainer** | Upload an FIR photo → get a plain-language explanation of every charge, in your language |
| 2 | **Rights Awareness** | Describe your situation → get the exact legal rights that apply, with BNSS section numbers |
| 3 | **Multilingual Legal Chat** | Ask any legal question in Hindi, Marathi, Tamil, or English — get grounded, cited answers |
| 4 | **Document Drafter** | Auto-generates bail applications, RTI requests, consumer complaints, and 6 other document types |
| 5 | **Bail Assistant** | FIR photo in → court-ready bail application PDF out, in under 90 seconds |
| 6 | **Legal Aid Connector** | Finds the nearest free legal aid centre matched to your case type and district |
| 7 | **Court Date Reminders** | Register your case (CNR) → get WhatsApp alerts 7, 3, and 1 day before every hearing |

---

## 🧠 How It Works — The Bail Pipeline

The core engine is a 7-agent [LangGraph](https://github.com/langchain-ai/langgraph) `StateGraph` with conditional routing:

```
FIR Photo
   │
   ▼
[1] OCR Agent (Groq Vision) ──► extracts FIR fields as structured JSON
   │
   ▼
[2] Law Router ──► routes to IPC or BNS based on FIR date (July 1, 2024 cutoff)
   │
   ▼
[3] RAG Retriever ──► pulls relevant law + precedents from ChromaDB
   │
   ▼
[4] Section 479 Calculator ──► computes bail eligibility (time served ÷ max sentence)
   │
   ▼
[5] Drafter Agent (Groq LLM) ──► generates bail application, grounded only in retrieved text
   │
   ▼
[6] Translator ──► translates to user's chosen language (10 supported)
   │
   ▼
[7] PDF Generator (ReportLab) ──► court-formatted PDF with confidence flags
```

Every legal citation is **retrieved, never invented** — if the RAG layer can't find a section, the drafter flags it `[VERIFY WITH LAWYER]` instead of hallucinating a case reference.

---

## 🏗️ Architecture

```
┌─────────────┐      HTTPS       ┌──────────────┐      Agents      ┌─────────────┐
│   Next.js    │ ───────────────► │   FastAPI    │ ───────────────► │  LangGraph  │
│  (Vercel)   │ ◄─────────────── │  (Render)    │ ◄─────────────── │   Agents    │
└─────────────┘                  └──────┬───────┘                  └──────┬──────┘
                                         │                                 │
                          ┌──────────────┼──────────────┐                 │
                          ▼              ▼               ▼                ▼
                    ┌──────────┐  ┌─────────────┐  ┌──────────┐   ┌─────────────┐
                    │ Supabase │  │  ChromaDB    │  │  Groq    │   │   Twilio    │
                    │ (cases,  │  │ (BNS, BNSS,  │  │ (Llama   │   │ (WhatsApp   │
                    │ reminders)│  │ IPC, Rights) │  │ 3.3 70B) │   │ reminders)  │
                    └──────────┘  └─────────────┘  └──────────┘   └─────────────┘
```

---

## 🛠️ Tech Stack

**Agentic AI**
- [LangGraph](https://github.com/langchain-ai/langgraph) — multi-agent orchestration with conditional edges and shared state
- [Groq](https://groq.com) — Llama 3.3 70B for reasoning, drafting, and vision-based OCR
- [ChromaDB](https://www.trychroma.com) — vector store for RAG over Indian legal text

**Backend**
- FastAPI + Uvicorn
- ReportLab — court-formatted PDF generation
- Supabase (PostgreSQL) — reminders, case data
- Twilio WhatsApp API — court date alerts

**Frontend**
- Next.js + Tailwind CSS
- Deployed as a PWA — works on low-bandwidth connections

**Deployment**
- Frontend → [Vercel](https://vercel.com)
- Backend → [Render](https://render.com)
- **Total infrastructure cost: ₹0**

---

## 📂 Project Structure

```
nyaya-saathi/
├── backend/
│   ├── main.py                     # FastAPI app — all 8 API routes
│   ├── startup.py                  # Builds ChromaDB knowledge base on boot
│   ├── core/
│   │   ├── llm/groq_client.py      # Shared Groq wrapper
│   │   ├── ocr/gemini_vision.py    # FIR image → structured JSON (Groq Vision)
│   │   ├── rag/                    # ChromaDB client, retriever, law router
│   │   ├── translation/            # 10-language translation layer
│   │   └── pdf/generator.py        # ReportLab court-format PDF builder
│   ├── features/
│   │   ├── bail_assistant/         # ⭐ The 7-agent LangGraph pipeline
│   │   ├── fir_explainer/
│   │   ├── rights_awareness/
│   │   ├── multilingual_chat/
│   │   ├── document_drafter/
│   │   ├── legal_aid_connector/
│   │   └── court_reminders/
│   └── data/                       # BNS/IPC sections, rights, mappings (JSON)
├── frontend/
│   ├── pages/                      # One page per feature
│   └── components/                 # Shared UI components
└── README.md
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- Free API keys: [Groq](https://console.groq.com), [Supabase](https://supabase.com), [Twilio](https://twilio.com)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
cp .env.example .env           # fill in your API keys

python startup.py              # builds the ChromaDB knowledge base
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local     # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Visit `http://localhost:3000`.

---

## ⚖️ Legal Foundation

| Provision | What it means |
|---|---|
| **BNSS Section 479** | Bail as a right after serving 1/2 (or 1/3 for first-time offenders) of max sentence |
| **BNSS Section 478** | Bail as a right for bailable offences |
| **BNSS Section 47** | Right to know the reason for arrest, immediately |
| **BNSS Section 50** | Right to inform a family member of arrest |
| **BNSS Section 57** | Cannot be detained beyond 24 hours without magistrate order |
| **Article 39A, Constitution** | Right to free legal aid |

The platform automatically detects whether a case falls under the old IPC/CrPC framework (pre–July 1, 2024) or the new BNS/BNSS framework, and routes accordingly.

---

## ⚠️ Disclaimer

Nyaya Saathi generates AI-assisted legal drafts and information for educational and accessibility purposes. **It is not a substitute for professional legal advice.** All AI-generated documents must be reviewed by a qualified advocate before filing. For immediate free legal aid in India, call **NALSA: 15100**.

---

## 🗺️ Roadmap

- [ ] Integrate Indian Kanoon API for live Supreme Court precedent retrieval
- [ ] Add state-specific court document formatting
- [ ] Offline-first PWA mode for 2G connectivity
- [ ] Warrant status checker feature
- [ ] Expand legal aid directory to all 36 states/UTs

---

## 👤 Author

**Sanket Gadekar**
B.E. Artificial Intelligence & Machine Learning, ISBM College of Engineering, Pune (2026)
[LinkedIn](https://linkedin.com/in/sanket-gadekar-14a915378) · [GitHub](https://github.com/sanketgadekar) · gadekarsanket31@gmail.com

---

## 📄 License

This project is built for educational and social impact purposes. Feel free to fork and adapt it to help more people access justice.
