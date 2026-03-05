# Baymax — Personal Health Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Academic%20Project-purple)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://baymax-joelg-007.streamlit.app)

**Live Demo:** [baymax-joelg-007.streamlit.app](https://baymax-joelg-007.streamlit.app)

> A modular, AI-powered health monitoring platform built with Streamlit, SQLite, and the Groq LLM API.  
> Logs symptoms, detects emergencies in real time, generates context-aware health advisories, and tracks your health over time — all in a secure, session-based web app.

---

## Features

| Feature | Description |
|---|---|
| **Secure Authentication** | Registration, bcrypt-hashed login, 30-minute session timeout, role-based access (User → Admin → Master) |
| **AI Health Chat** | 5-intent router (symptom, document, greeting, analytics, general) powered by `llama-3.1-8b-instant` via Groq |
| **Emergency Detection** | Deterministic `RuleEngine` evaluates every symptom against a curated red-flag library before any LLM call |
| **Analytics Dashboard** | Symptom frequency bar charts and severity trend line graphs via Plotly, with risk score computation |
| **Health Timeline** | Chronological, colour-coded severity timeline across all sessions |
| **Document Upload & OCR** | PDF/image report ingestion — pdfplumber for digital PDFs, Tesseract for scanned images |
| **Lab Parameter Extraction** | Universal LLM extractor pulls named parameters (Haemoglobin, HbA1c, CBC values, etc.) from any report type |
| **Lab Trends Table** | Pivot table view comparing extracted parameters across multiple uploaded reports over time |
| **Symptom Resolution Tracking** | Mark symptoms as resolved; `is_resolved` / `resolved_at` columns in DB |
| **Admin Panel** | View all user events, login audit log, suspend/activate accounts |
| **Master Panel** | Promote/revoke admin roles, full role audit trail |

---

## Architecture
```
baymax/
├── app.py                     # Entry point — Streamlit app + session bootstrap
├── .env                       # API keys (gitignored)
├── requirements.txt
├── baymax.db                  # SQLite database (auto-created on first run)
│
├── ui/                      # Presentation Layer
│   ├── router.py              # Security checks + page dispatch
│   ├── login.py
│   ├── dashboard.py
│   ├── chat.py
│   ├── timeline.py
│   ├── analytics.py
│   ├── documents.py
│   ├── parameters.py          # Lab parameter viewer + reference ranges
│   ├── profile.py
│   ├── admin.py
│   └── master.py
│
├── core/                    # Application Logic Layer
│   ├── ai_layer.py            # Groq API client + prompt engineering
│   ├── symptom_extractor.py
│   ├── rule_engine.py         # Deterministic red-flag detection
│   ├── risk_engine.py         # Risk score computation (0–100)
│   ├── analytics_engine.py
│   ├── timeline_engine.py
│   ├── document_parser.py     # pdfplumber + Tesseract routing
│   ├── document_extractor.py  # LLM parameter extraction
│   └── pdf_generator.py
│
├── auth/                    # Auth Layer
│   ├── auth_service.py
│   ├── security.py            # bcrypt hashing
│   └── session_manager.py     # 30-min timeout enforcement
│
└── database/                # Data Layer
    ├── models.py              # SQLAlchemy ORM definitions
    ├── db_init.py             # Engine + init_db()
    └── crud.py                # All DB read/write operations
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Tesseract OCR installed on your system ([install guide](https://github.com/tesseract-ocr/tesseract))
- A free [Groq API key](https://console.groq.com)

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/your-username/baymax.git
cd baymax

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Environment Variables

Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Run
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.  
The SQLite database (`baymax.db`) is created automatically on first run.

---

## Database Schema

| Table | Key Columns |
|---|---|
| `users` | `id`, `username`, `email`, `hashed_password`, `role`, `is_active` |
| `health_events` | `id`, `user_id` (FK), `symptom`, `severity`, `body_region`, `timestamp`, `is_resolved`, `resolved_at` |
| `documents` | `id`, `user_id` (FK), `file_path`, `original_filename`, `uploaded_at` |
| `document_summaries` | `id`, `user_id` (FK), `document_id` (FK), `report_type`, `extracted_summary`, `key_parameters_json`, `severity_flag` |
| `login_audit` | `id`, `identifier`, `success`, `timestamp` |
| `admin_audit` | `id`, `admin_id`, `target_table`, `old_value`, `new_value`, `timestamp` |
| `role_audit` | `id`, `actor_id`, `target_user_id`, `action`, `timestamp` |

All FK relationships cascade on delete. Foreign keys are enforced at connection time via SQLAlchemy's `event.listen`.

---

## How the AI Layer Works
```
User message
    │
    ▼
AILayer.classify_intent()     →  "symptom" | "document" | "analytics" | "greeting" | "general"
    │
    ├─ symptom ──▶  SymptomExtractor  ──▶  RuleEngine  ──┬─ Emergency? → ALERT (stop)
    │                                                     └─ Safe?      → AILayer.generate_advisory()
    │                                                                         │
    │                                                                    Groq LLM (context-injected)
    │                                                                         │
    │                                                                    Save to DB → Analytics refresh
    │
    ├─ document ──▶  DocumentParser (pdfplumber / Tesseract)
    │                     │
    │               DocumentExtractor (LLM: universal parameter extraction)
    │                     │
    │               DocumentSummary saved to DB
    │
    └─ analytics / greeting / general ──▶  AILayer.generate_advisory()
```

Every symptom advisory prompt is injected with the user's 5 most recent health events as context, ensuring the LLM response is always history-aware rather than session-isolated.

---

## 📦 Requirements
```
streamlit>=1.35.0
sqlalchemy>=2.0
groq
plotly>=5.0
pdfplumber
pytesseract
Pillow
bcrypt
python-dotenv
reportlab
```

Full pinned versions in `requirements.txt`.

---

## Security Notes

- Passwords are hashed with **bcrypt** (never stored in plaintext)
- All database queries use **parameterised SQLAlchemy ORM** calls (no raw SQL string interpolation)
- Sessions expire after **30 minutes** of inactivity, enforced server-side on every page load
- The `.env` file is gitignored — never commit your API key
- Role escalation (user → admin → master) is logged in `role_audit` with actor and timestamp

---

## ⚠️ Medical Disclaimer

Baymax is a **decision-support tool** intended for personal health awareness only.  
It does **not** provide medical diagnosis, prescription, or certified medical advice.  
Always consult a qualified healthcare professional for medical decisions.  
In a medical emergency, call your local emergency services immediately.

---

## Author - Joel Guedes

**Project Guide:** Prof. Umesh Ahire  
**Institution:** Nowrosjee Wadia College, Pune — Dept. of Computer Science  
**Course:** T.Y.B.Sc (Computer Science) NEP 1.0, Semester VI  
**Subject:** Operating System-II and Project Implementation (CSMJ364)

---

## 📄 License

This project is submitted as an academic project at Nowrosjee Wadia College, Pune, under T.Y.B.Sc Computer Science NEP 1.0 (2025–2026).

Licensed under the **MIT License** — see [LICENSE](LICENSE) for details.  
You are free to use, modify, and distribute this code with attribution.
