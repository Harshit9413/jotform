# Merge FormCraft + QueryMind Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge FormCraft and QueryMind into one FastAPI backend (port 8000) and one React frontend (port 3000) with shared navigation.

**Architecture:** Backend splits into `backend/formcraft/` and `backend/querymind/` modules each with their own router, combined in one `backend/main.py`. Frontend adds React Router with a Navbar and converts FormCraft's HTML file to React pages (`TemplatesPage`, `BuilderPage`, `SubmissionsPage`) placed alongside the existing QueryMind components.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, React 18, Vite, react-router-dom, lucide-react

---

## File Map

**Create:**
- `backend/main.py` — merged FastAPI app
- `backend/requirements.txt` — merged deps
- `backend/seed.py` — moved + updated imports
- `backend/formcraft/__init__.py`
- `backend/formcraft/database.py`
- `backend/formcraft/models.py`
- `backend/formcraft/schemas.py`
- `backend/formcraft/router.py`
- `backend/querymind/__init__.py`
- `backend/querymind/router.py`
- `backend/querymind/db_connector.py` — moved
- `backend/querymind/ai_engine.py` — moved
- `frontend/src/components/Navbar.jsx`
- `frontend/src/pages/formcraft/formcraft.css`
- `frontend/src/pages/formcraft/TemplatesPage.jsx`
- `frontend/src/pages/formcraft/BuilderPage.jsx`
- `frontend/src/pages/formcraft/SubmissionsPage.jsx`
- `frontend/src/pages/querymind/ConnectScreen.jsx` — moved
- `frontend/src/pages/querymind/ChatScreen.jsx` — moved

**Modify:**
- `frontend/src/App.jsx`
- `frontend/src/index.css`
- `frontend/package.json`
- `frontend/vite.config.js`
- `start.sh`

**Delete (after confirming new files work):**
- `main.py`, `models.py`, `schemas.py`, `database.py`, `seed.py` (root)
- `backend/main.py` (old QueryMind-only main)
- `backend/db_connector.py`, `backend/ai_engine.py`
- `frontend/src/components/ConnectScreen.jsx`
- `frontend/src/components/ChatScreen.jsx`
- `Formcraft with backend .html`

---

## Task 1: Backend — FormCraft module

**Files:**
- Create: `backend/formcraft/__init__.py`
- Create: `backend/formcraft/database.py`
- Create: `backend/formcraft/models.py`
- Create: `backend/formcraft/schemas.py`

- [ ] **Step 1: Create the formcraft package**

```bash
mkdir -p /Users/vishaljangid/learning/harshit/jotform/backend/formcraft
```

- [ ] **Step 2: Create `backend/formcraft/__init__.py`**

```python
```
(empty file)

- [ ] **Step 3: Create `backend/formcraft/database.py`**

```python
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

- [ ] **Step 4: Create `backend/formcraft/models.py`**

```python
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Template(Base):
    __tablename__ = "templates"

    id          = Column(String, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    category    = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color       = Column(String, default="#1a56db")
    badge       = Column(String, nullable=True)
    tags        = Column(JSON, default=[])
    score       = Column(Integer, default=70)
    score_tip   = Column(String, nullable=True)
    fields      = Column(JSON, default=[])
    suggestions = Column(JSON, default=[])
    created_at  = Column(DateTime, default=datetime.utcnow)


class Submission(Base):
    __tablename__ = "submissions"

    id           = Column(Integer, primary_key=True, index=True, autoincrement=True)
    form_id      = Column(String, nullable=False)
    form_title   = Column(String, nullable=False)
    data         = Column(JSON, nullable=False)
    status       = Column(String, default="new")
    submitted_at = Column(DateTime, default=datetime.utcnow)


class CustomForm(Base):
    __tablename__ = "custom_forms"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title      = Column(String, nullable=False)
    fields     = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 5: Create `backend/formcraft/schemas.py`**

```python
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class TemplateOut(BaseModel):
    id:          str
    title:       str
    category:    str
    description: Optional[str]
    color:       str
    badge:       Optional[str]
    tags:        List[str]
    score:       int
    score_tip:   Optional[str]
    fields:      List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    form_id:    str
    form_title: str
    data:       Dict[str, Any]


class SubmissionOut(BaseModel):
    id:           int
    form_id:      str
    form_title:   str
    data:         Dict[str, Any]
    status:       str
    submitted_at: datetime

    class Config:
        from_attributes = True


class CustomFormCreate(BaseModel):
    title:  str
    fields: List[Dict[str, Any]]


class CustomFormOut(BaseModel):
    id:         int
    title:      str
    fields:     List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 6: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add backend/formcraft/
git commit -m "feat: add formcraft backend module (database, models, schemas)"
```

---

## Task 2: Backend — FormCraft router

**Files:**
- Create: `backend/formcraft/router.py`

- [ ] **Step 1: Create `backend/formcraft/router.py`**

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .models import Template, Submission, CustomForm
from .schemas import (
    TemplateOut, SubmissionCreate, SubmissionOut,
    CustomFormCreate, CustomFormOut,
)
from .database import SessionLocal

router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def root():
    return {"status": "ok", "message": "FormCraft API is running"}


@router.get("/templates", response_model=List[TemplateOut])
def get_templates(db: Session = Depends(get_db)):
    return db.query(Template).all()


@router.get("/templates/{template_id}", response_model=TemplateOut)
def get_template(template_id: str, db: Session = Depends(get_db)):
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return t


@router.post("/submissions", response_model=SubmissionOut)
def create_submission(payload: SubmissionCreate, db: Session = Depends(get_db)):
    sub = Submission(
        form_id=payload.form_id,
        form_title=payload.form_title,
        data=payload.data,
        submitted_at=datetime.utcnow(),
        status="new",
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.get("/submissions", response_model=List[SubmissionOut])
def get_submissions(
    status: Optional[str] = None,
    form_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Submission)
    if status:
        q = q.filter(Submission.status == status)
    if form_id:
        q = q.filter(Submission.form_id == form_id)
    return q.order_by(Submission.submitted_at.desc()).all()


@router.get("/submissions/{sub_id}", response_model=SubmissionOut)
def get_submission(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(Submission).filter(Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    return sub


@router.patch("/submissions/{sub_id}/read")
def mark_read(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(Submission).filter(Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    sub.status = "read"
    db.commit()
    return {"message": "Marked as read"}


@router.delete("/submissions/{sub_id}")
def delete_submission(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(Submission).filter(Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    db.delete(sub)
    db.commit()
    return {"message": "Deleted"}


@router.delete("/submissions")
def delete_all_submissions(db: Session = Depends(get_db)):
    db.query(Submission).delete()
    db.commit()
    return {"message": "All submissions deleted"}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Submission).count()
    new_count = db.query(Submission).filter(Submission.status == "new").count()
    today = datetime.utcnow().date()
    today_count = db.query(Submission).filter(
        Submission.submitted_at >= datetime(today.year, today.month, today.day)
    ).count()
    return {
        "total": total,
        "new": new_count,
        "today": today_count,
        "completion_rate": "87%",
    }


@router.post("/forms", response_model=CustomFormOut)
def save_custom_form(payload: CustomFormCreate, db: Session = Depends(get_db)):
    form = CustomForm(
        title=payload.title,
        fields=payload.fields,
        created_at=datetime.utcnow(),
    )
    db.add(form)
    db.commit()
    db.refresh(form)
    return form


@router.get("/forms", response_model=List[CustomFormOut])
def get_custom_forms(db: Session = Depends(get_db)):
    return db.query(CustomForm).order_by(CustomForm.created_at.desc()).all()


@router.get("/forms/{form_id}", response_model=CustomFormOut)
def get_custom_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(CustomForm).filter(CustomForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add backend/formcraft/router.py
git commit -m "feat: add formcraft router with all API endpoints"
```

---

## Task 3: Backend — QueryMind module

**Files:**
- Create: `backend/querymind/__init__.py`
- Create: `backend/querymind/db_connector.py` (copy from `backend/db_connector.py`)
- Create: `backend/querymind/ai_engine.py` (copy from `backend/ai_engine.py`)
- Create: `backend/querymind/router.py`

- [ ] **Step 1: Create the querymind package**

```bash
mkdir -p /Users/vishaljangid/learning/harshit/jotform/backend/querymind
```

- [ ] **Step 2: Create `backend/querymind/__init__.py`**

```python
```
(empty file)

- [ ] **Step 3: Copy `backend/db_connector.py` → `backend/querymind/db_connector.py`**

```bash
cp /Users/vishaljangid/learning/harshit/jotform/backend/db_connector.py \
   /Users/vishaljangid/learning/harshit/jotform/backend/querymind/db_connector.py
```

- [ ] **Step 4: Copy `backend/ai_engine.py` → `backend/querymind/ai_engine.py`**

```bash
cp /Users/vishaljangid/learning/harshit/jotform/backend/ai_engine.py \
   /Users/vishaljangid/learning/harshit/jotform/backend/querymind/ai_engine.py
```

- [ ] **Step 5: Create `backend/querymind/router.py`**

Note: Routes are updated from `/connect` → `/api/connect` etc. so the frontend's `/api/` calls work without a proxy rewrite.

```python
from __future__ import annotations
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .db_connector import DatabaseConnector
from .ai_engine import AIEngine

router = APIRouter(prefix="/api")

_EXPLICIT_COUNT_RE = re.compile(
    r'\b(top|first|last|recent|latest|only|just)\s+\d+'
    r'|\b\d+\s+(rows?|records?|results?|items?|entries?)'
    r'|\blimit\s+(to\s+)?\d+'
    r'|\bshow\s+(me\s+)?\d+',
    re.IGNORECASE,
)


def _strip_ai_limit(sql: str) -> str:
    cleaned = re.sub(
        r'\s+LIMIT\s+\d+(\s+OFFSET\s+\d+)?\s*;?\s*$',
        '',
        sql.strip(),
        flags=re.IGNORECASE,
    )
    return cleaned.strip().rstrip(';')


def _friendly_conn_error(exc: Exception) -> str:
    msg = str(exc)
    msg = re.sub(r'\(Background on this error.*', '', msg, flags=re.DOTALL).strip()
    msg = re.sub(r'^\([^)]+\)\s*', '', msg).strip()
    if 'Network is unreachable' in msg or 'No route to host' in msg:
        return (
            'Cannot reach the database host. Verify the hostname and port are '
            'accessible from your network.'
        )
    if 'password authentication failed' in msg or 'Access denied' in msg:
        return 'Authentication failed — check your username and password.'
    if 'Connection refused' in msg:
        return 'Connection refused — the server may be down or the port is blocked.'
    if 'could not translate host name' in msg or 'Name or service not known' in msg:
        return 'Hostname not found — check the host in your database URL.'
    if 'timeout' in msg.lower():
        return 'Connection timed out — the server may be unreachable or overloaded.'
    return msg or 'Unable to connect to the database.'


_sessions: dict[str, dict] = {}


class ConnectRequest(BaseModel):
    database_url: str
    groq_api_key: str
    session_id: str


class QueryRequest(BaseModel):
    session_id: str
    question: str
    conversation_history: list = []


class DisconnectRequest(BaseModel):
    session_id: str


@router.post("/connect")
async def connect(req: ConnectRequest):
    if req.session_id in _sessions:
        try:
            _sessions[req.session_id]["connector"].close()
        except Exception:
            pass
        del _sessions[req.session_id]

    try:
        connector = DatabaseConnector(req.database_url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_friendly_conn_error(exc))

    try:
        schema = connector.extract_schema()
    except Exception as exc:
        connector.close()
        raise HTTPException(status_code=400, detail=f"Schema extraction failed: {exc}")

    ai = AIEngine(req.groq_api_key, schema)
    _sessions[req.session_id] = {"connector": connector, "ai": ai, "schema": schema}

    total_columns = sum(len(t["columns"]) for t in schema.values())
    return {
        "status": "connected",
        "db_type": connector.db_type,
        "tables": list(schema.keys()),
        "schema": schema,
        "total_tables": len(schema),
        "total_columns": total_columns,
    }


@router.post("/query")
async def query(req: QueryRequest):
    session = _sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please reconnect.")

    connector: DatabaseConnector = session["connector"]
    ai: AIEngine = session["ai"]

    try:
        ai_resp = ai.generate_sql(req.question, req.conversation_history)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI error: {exc}")

    resp_type = ai_resp.get("type", "conversation")

    if resp_type == "conversation":
        return {
            "type": "conversation",
            "answer": ai_resp.get("answer", ""),
            "sql": None,
            "data": [],
            "columns": [],
            "row_count": 0,
        }

    sql: str = ai_resp.get("sql", "").strip()
    if not sql:
        raise HTTPException(status_code=400, detail="AI returned no SQL query.")

    if not _EXPLICIT_COUNT_RE.search(req.question):
        sql = _strip_ai_limit(sql)

    safe, reason = connector.is_safe_query(sql)
    if not safe:
        raise HTTPException(status_code=400, detail=reason)

    try:
        result = connector.execute_query(sql)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Query execution failed: {exc}")

    try:
        answer = ai.generate_answer(req.question, sql, result["data"], result["columns"])
    except Exception:
        answer = f"Found **{result['row_count']}** result(s)."

    return {
        "type": "sql",
        "answer": answer,
        "sql": sql,
        "data": result["data"],
        "columns": result["columns"],
        "row_count": result["row_count"],
        "truncated": result.get("truncated", False),
    }


@router.post("/disconnect")
async def disconnect(req: DisconnectRequest):
    session = _sessions.pop(req.session_id, None)
    if session:
        try:
            session["connector"].close()
        except Exception:
            pass
    return {"status": "disconnected"}


@router.get("/schema/{session_id}")
async def get_schema(session_id: str):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"schema": session["schema"]}


@router.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
```

- [ ] **Step 6: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add backend/querymind/
git commit -m "feat: add querymind backend module with updated /api prefix routes"
```

---

## Task 4: Backend — merged main.py + requirements.txt + seed.py

**Files:**
- Create: `backend/main.py`
- Create: `backend/requirements.txt`
- Create: `backend/seed.py`

- [ ] **Step 1: Create `backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from formcraft.router import router as formcraft_router
from formcraft.database import SessionLocal
from formcraft import models as fc_models
from formcraft.database import engine as fc_engine
from querymind.router import router as querymind_router

app = FastAPI(title="FormCraft + QueryMind API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fc_models.Base.metadata.create_all(bind=fc_engine)

app.include_router(formcraft_router)
app.include_router(querymind_router)
```

- [ ] **Step 2: Create `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
groq==0.13.1
psycopg2-binary==2.9.12
pymysql==1.1.1
pydantic==2.9.2
cryptography==42.0.7
python-dotenv==1.0.1
python-multipart==0.0.9
```

- [ ] **Step 3: Create `backend/seed.py`**

```python
"""
Run ONCE to seed templates into PostgreSQL:
  cd backend && python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from formcraft.database import SessionLocal, engine
from formcraft import models

models.Base.metadata.create_all(bind=engine)

TEMPLATES = [
    {
        "id": "payment",
        "title": "Order & Payment Form",
        "category": "payment",
        "description": "Complete checkout with shipping, card details & order summary.",
        "color": "#1a56db",
        "badge": "🔥 Popular",
        "tags": ["checkout", "payment", "order"],
        "score": 78,
        "score_tip": "Add UPI & promo code to reach 95+",
        "suggestions": [
            {"icon": "💳", "title": "Add UPI / Wallet field", "text": "Indian users prefer UPI."},
            {"icon": "🎁", "title": "Add promo code field", "text": "Promo codes increase conversions by 12%."},
            {"icon": "📦", "title": "Add delivery date picker", "text": "Reduces failed deliveries by 30%."},
        ],
        "fields": [],
    },
    {
        "id": "contact",
        "title": "Contact Us Form",
        "category": "contact",
        "description": "Simple contact form with name, email and message.",
        "color": "#059669",
        "badge": None,
        "tags": ["contact", "enquiry"],
        "score": 72,
        "score_tip": "Add phone field to increase reach",
        "suggestions": [
            {"icon": "📱", "title": "Add Phone field", "text": "Reach users on WhatsApp too."},
        ],
        "fields": [
            {"type": "row2", "fields": [
                {"type": "text", "label": "First Name", "placeholder": "John", "required": True},
                {"type": "text", "label": "Last Name", "placeholder": "Doe", "required": True},
            ]},
            {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
            {"type": "textarea", "label": "Message", "placeholder": "Write your message here...", "required": True},
            {"type": "submit", "label": "Send Message", "color": "#059669"},
        ],
    },
    {
        "id": "registration",
        "title": "Event Registration Form",
        "category": "registration",
        "description": "Register attendees for events, workshops or webinars.",
        "color": "#7c3aed",
        "badge": "⭐ New",
        "tags": ["event", "registration", "workshop"],
        "score": 80,
        "score_tip": "Add dietary preferences for 90+",
        "suggestions": [
            {"icon": "🍽️", "title": "Add Dietary Preferences", "text": "Important for catered events."},
            {"icon": "👥", "title": "Add +1 / Guest option", "text": "Allow attendees to bring guests."},
        ],
        "fields": [
            {"type": "row2", "fields": [
                {"type": "text", "label": "Full Name", "placeholder": "Your full name", "required": True},
                {"type": "email", "label": "Email", "placeholder": "you@email.com", "required": True},
            ]},
            {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": False},
            {"type": "select", "label": "Session", "options": ["Morning (9am-12pm)", "Afternoon (2pm-5pm)", "Evening (6pm-9pm)"], "required": True},
            {"type": "submit", "label": "Register Now", "color": "#7c3aed"},
        ],
    },
    {
        "id": "feedback",
        "title": "Customer Feedback Form",
        "category": "feedback",
        "description": "Collect ratings and feedback from customers.",
        "color": "#d97706",
        "badge": None,
        "tags": ["feedback", "rating", "review"],
        "score": 75,
        "score_tip": "Add NPS score question for 92+",
        "suggestions": [
            {"icon": "📊", "title": "Add NPS Score", "text": "Net Promoter Score is industry standard."},
            {"icon": "📸", "title": "Add Photo Upload", "text": "Visual feedback increases credibility."},
        ],
        "fields": [
            {"type": "text", "label": "Your Name", "placeholder": "Optional", "required": False},
            {"type": "rating", "label": "Overall Rating", "required": True},
            {"type": "select", "label": "What did you purchase?", "options": ["Product", "Service", "Subscription", "Other"], "required": True},
            {"type": "textarea", "label": "Your Feedback", "placeholder": "Tell us what you think...", "required": True},
            {"type": "submit", "label": "Submit Feedback", "color": "#d97706"},
        ],
    },
]

db = SessionLocal()
try:
    for t in TEMPLATES:
        existing = db.query(models.Template).filter(models.Template.id == t["id"]).first()
        if not existing:
            db.add(models.Template(**t))
    db.commit()
    print(f"✅ Seeded {len(TEMPLATES)} templates")
finally:
    db.close()
```

- [ ] **Step 4: Verify backend starts**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
source myvenv/bin/activate
pip install -r backend/requirements.txt
cd backend && uvicorn main:app --reload --port 8000
```

Expected: `Uvicorn running on http://0.0.0.0:8000`

- [ ] **Step 5: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add backend/main.py backend/requirements.txt backend/seed.py
git commit -m "feat: add merged backend main.py, requirements, and seed"
```

---

## Task 5: Frontend — install react-router-dom, create folders

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Install react-router-dom**

```bash
cd /Users/vishaljangid/learning/harshit/jotform/frontend
npm install react-router-dom
```

- [ ] **Step 2: Create page directories**

```bash
mkdir -p /Users/vishaljangid/learning/harshit/jotform/frontend/src/pages/formcraft
mkdir -p /Users/vishaljangid/learning/harshit/jotform/frontend/src/pages/querymind
mkdir -p /Users/vishaljangid/learning/harshit/jotform/frontend/src/components
```

- [ ] **Step 3: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/package.json frontend/package-lock.json
git commit -m "feat: add react-router-dom to frontend"
```

---

## Task 6: Frontend — Navbar component

**Files:**
- Create: `frontend/src/components/Navbar.jsx`

- [ ] **Step 1: Create `frontend/src/components/Navbar.jsx`**

```jsx
import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav style={{
      background: '#fff',
      borderBottom: '1px solid #e2e8f0',
      padding: '0 32px',
      display: 'flex',
      alignItems: 'center',
      height: '58px',
      position: 'sticky',
      top: 0,
      zIndex: 200,
      gap: '32px',
    }}>
      <div style={{
        fontFamily: "'Playfair Display', serif",
        fontSize: '20px',
        color: '#1a56db',
        fontWeight: 700,
        whiteSpace: 'nowrap',
      }}>
        Form<span style={{ color: '#0f172a' }}>Craft</span>
        <span style={{ color: '#94a3b8', margin: '0 10px', fontFamily: 'sans-serif', fontWeight: 300 }}>|</span>
        <span style={{ color: '#6c63ff', fontFamily: 'sans-serif', fontSize: '17px', fontWeight: 700 }}>Query</span>
        <span style={{ color: '#0f172a', fontFamily: 'sans-serif', fontSize: '17px', fontWeight: 700 }}>Mind</span>
      </div>

      <div style={{ display: 'flex', gap: '4px' }}>
        <NavLink to="/formcraft" style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
          📋 FormCraft
        </NavLink>
        <NavLink to="/querymind" style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
          🧠 QueryMind
        </NavLink>
      </div>
    </nav>
  )
}

const navStyle = {
  padding: '6px 14px',
  borderRadius: '8px',
  border: 'none',
  background: 'none',
  cursor: 'pointer',
  fontSize: '13px',
  fontWeight: 500,
  color: '#64748b',
  textDecoration: 'none',
  fontFamily: 'inherit',
}
```

- [ ] **Step 2: Add nav-active style to `frontend/src/index.css`**

Append at the end of `frontend/src/index.css`:

```css
/* Navbar active link */
.nav-active {
  background: #eff6ff !important;
  color: #1a56db !important;
}
```

- [ ] **Step 3: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/src/components/Navbar.jsx frontend/src/index.css
git commit -m "feat: add shared Navbar component"
```

---

## Task 7: Frontend — FormCraft CSS

**Files:**
- Create: `frontend/src/pages/formcraft/formcraft.css`

- [ ] **Step 1: Create `frontend/src/pages/formcraft/formcraft.css`**

```css
/* FormCraft scoped styles — wrap pages in .fc */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap');

.fc {
  --fc-blue: #1a56db;
  --fc-blue-d: #1240a8;
  --fc-blue-l: #e8f0fe;
  --fc-dark: #0f172a;
  --fc-muted: #64748b;
  --fc-border: #e2e8f0;
  --fc-bg: #f8fafc;
  --fc-white: #ffffff;
  --fc-green: #059669;
  --fc-green-l: #d1fae5;
  --fc-red: #dc2626;
  --fc-red-l: #fee2e2;
  --fc-amber: #d97706;
  --fc-radius: 14px;
  --fc-shadow: 0 8px 32px rgba(15,23,42,.10);
  font-family: 'DM Sans', sans-serif;
  background: var(--fc-bg);
  color: var(--fc-dark);
  min-height: calc(100vh - 58px);
}

/* LOADING */
.fc .fc-loading { text-align: center; padding: 60px; color: var(--fc-muted); }
.fc .fc-spinner { width: 32px; height: 32px; border: 3px solid var(--fc-border); border-top-color: var(--fc-blue); border-radius: 50%; animation: fcspin .8s linear infinite; margin: 0 auto 12px; }
@keyframes fcspin { to { transform: rotate(360deg); } }

/* HERO */
.fc .fc-hero { text-align: center; padding: 56px 20px 36px; background: var(--fc-white); border-bottom: 1px solid var(--fc-border); }
.fc .fc-hero-tag { display: inline-flex; align-items: center; gap: 6px; background: var(--fc-blue-l); color: var(--fc-blue); font-size: 11px; font-weight: 700; padding: 5px 14px; border-radius: 20px; margin-bottom: 18px; letter-spacing: .05em; text-transform: uppercase; }
.fc .fc-hero h1 { font-family: 'Playfair Display', serif; font-size: 40px; line-height: 1.2; color: var(--fc-dark); margin-bottom: 12px; }
.fc .fc-hero h1 em { color: var(--fc-blue); font-style: normal; }
.fc .fc-hero p { font-size: 15px; color: var(--fc-muted); max-width: 460px; margin: 0 auto 24px; line-height: 1.7; }
.fc .fc-search-wrap { display: flex; gap: 8px; max-width: 420px; margin: 0 auto; }
.fc .fc-search-wrap input { flex: 1; padding: 10px 14px; border: 1.5px solid var(--fc-border); border-radius: 10px; font-size: 14px; font-family: 'DM Sans', sans-serif; outline: none; }
.fc .fc-search-wrap input:focus { border-color: var(--fc-blue); }
.fc .fc-search-wrap button { background: var(--fc-blue); color: #fff; border: none; border-radius: 10px; padding: 10px 18px; font-size: 14px; font-weight: 600; cursor: pointer; }

/* FILTERS */
.fc .fc-filter-row { display: flex; gap: 8px; justify-content: center; padding: 18px 20px 24px; flex-wrap: wrap; background: var(--fc-white); }
.fc .fc-filter-pill { padding: 6px 16px; border-radius: 20px; border: 1.5px solid var(--fc-border); background: none; font-size: 13px; font-weight: 500; cursor: pointer; color: var(--fc-muted); font-family: 'DM Sans', sans-serif; transition: all .15s; }
.fc .fc-filter-pill.active, .fc .fc-filter-pill:hover { border-color: var(--fc-blue); background: var(--fc-blue); color: #fff; }

/* TEMPLATE GRID */
.fc .fc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; padding: 24px 36px 48px; max-width: 1200px; margin: 0 auto; }
.fc .fc-tcard { background: var(--fc-white); border: 1.5px solid var(--fc-border); border-radius: var(--fc-radius); overflow: hidden; cursor: pointer; transition: transform .2s, border-color .2s, box-shadow .2s; }
.fc .fc-tcard:hover { transform: translateY(-4px); border-color: var(--fc-blue); box-shadow: var(--fc-shadow); }
.fc .fc-tcard-preview { height: 160px; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 7px; padding: 16px; position: relative; }
.fc .fc-mf { width: 100%; max-width: 200px; height: 9px; border-radius: 4px; background: rgba(255,255,255,.35); }
.fc .fc-mf.lbl { height: 6px; width: 55%; background: rgba(255,255,255,.25); }
.fc .fc-mf.btn { height: 11px; width: 70px; border-radius: 5px; background: rgba(255,255,255,.9); margin-top: 5px; }
.fc .fc-mf.title { height: 9px; width: 38%; background: rgba(255,255,255,.5); margin-bottom: 3px; }
.fc .fc-badge-pill { position: absolute; top: 10px; right: 10px; font-size: 10px; font-weight: 700; padding: 3px 9px; border-radius: 20px; background: rgba(255,255,255,.9); }
.fc .fc-tcard-body { padding: 12px 14px 14px; border-top: 1px solid var(--fc-border); }
.fc .fc-tcard-cat { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; margin-bottom: 3px; color: var(--fc-blue); }
.fc .fc-tcard-title { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
.fc .fc-tcard-desc { font-size: 12px; color: var(--fc-muted); line-height: 1.5; margin-bottom: 10px; }
.fc .fc-tcard-foot { display: flex; align-items: center; justify-content: space-between; }
.fc .fc-tags { display: flex; gap: 4px; flex-wrap: wrap; }
.fc .fc-tag { font-size: 10px; background: var(--fc-bg); border: 1px solid var(--fc-border); border-radius: 5px; padding: 2px 7px; color: var(--fc-muted); }
.fc .fc-use-btn { font-size: 12px; font-weight: 600; color: var(--fc-blue); background: var(--fc-blue-l); border: none; border-radius: 7px; padding: 5px 12px; cursor: pointer; white-space: nowrap; }

/* OVERLAY & MODAL */
.fc .fc-overlay { display: none; position: fixed; inset: 0; background: rgba(15,23,42,.6); z-index: 300; align-items: flex-start; justify-content: center; padding: 20px 16px; overflow-y: auto; }
.fc .fc-overlay.open { display: flex; }
.fc .fc-modal { background: var(--fc-white); border-radius: 18px; width: 100%; max-width: 920px; overflow: hidden; margin: auto; animation: fcslideUp .22s ease; }
@keyframes fcslideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
.fc .fc-mhdr { display: flex; align-items: center; justify-content: space-between; padding: 16px 22px; border-bottom: 1px solid var(--fc-border); }
.fc .fc-mhdr-l h2 { font-size: 16px; font-weight: 700; }
.fc .fc-mhdr-l p { font-size: 12px; color: var(--fc-muted); margin-top: 2px; }
.fc .fc-mclose { background: var(--fc-bg); border: 1px solid var(--fc-border); border-radius: 8px; width: 30px; height: 30px; font-size: 15px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: var(--fc-muted); }
.fc .fc-mbody { display: grid; grid-template-columns: 1fr 290px; min-height: 480px; }
.fc .fc-mform { padding: 22px 26px; overflow-y: auto; max-height: 68vh; }
.fc .fc-mai { background: var(--fc-bg); border-left: 1px solid var(--fc-border); padding: 18px; display: flex; flex-direction: column; gap: 10px; overflow-y: auto; max-height: 68vh; }

/* FORM FIELDS */
.fc .fc-fsec { font-size: 11px; font-weight: 700; color: var(--fc-muted); text-transform: uppercase; letter-spacing: .06em; margin: 0 0 12px; padding-bottom: 7px; border-bottom: 1px solid var(--fc-border); }
.fc .fc-frow { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.fc .fc-frow3 { display: grid; grid-template-columns: 1fr 88px 78px; gap: 10px; }
.fc .fc-fg { display: flex; flex-direction: column; gap: 5px; margin-bottom: 12px; }
.fc .fc-fg label { font-size: 12px; font-weight: 600; color: var(--fc-dark); }
.fc .fc-req { color: var(--fc-red); }
.fc .fc-fg input, .fc .fc-fg select, .fc .fc-fg textarea { padding: 9px 11px; border: 1.5px solid var(--fc-border); border-radius: 9px; font-size: 14px; font-family: 'DM Sans', sans-serif; color: var(--fc-dark); background: var(--fc-white); outline: none; transition: border-color .15s; width: 100%; }
.fc .fc-fg input:focus, .fc .fc-fg select:focus, .fc .fc-fg textarea:focus { border-color: var(--fc-blue); }
.fc .fc-fg textarea { height: 74px; resize: none; }
.fc .fc-radio-g, .fc .fc-check-g { display: flex; flex-direction: column; gap: 7px; }
.fc .fc-radio-opt, .fc .fc-check-opt { display: flex; align-items: center; gap: 8px; font-size: 14px; color: var(--fc-dark); cursor: pointer; }
.fc .fc-star-row { display: flex; gap: 7px; font-size: 24px; cursor: pointer; }
.fc .fc-star { color: #cbd5e1; transition: color .1s; }
.fc .fc-star.on { color: #d97706; }
.fc .fc-submit-btn { width: 100%; padding: 12px; border: none; border-radius: 10px; background: var(--fc-blue); color: #fff; font-size: 15px; font-weight: 700; cursor: pointer; font-family: 'DM Sans', sans-serif; margin-top: 6px; }
.fc .fc-submit-btn:hover { opacity: .88; }
.fc .fc-submit-btn:disabled { opacity: .5; cursor: not-allowed; }
.fc .fc-form-success { background: var(--fc-green-l); border: 1.5px solid #6ee7b7; border-radius: 10px; padding: 16px; text-align: center; color: #065f46; font-weight: 600; display: none; }
.fc .fc-form-success.show { display: block; }

/* AI PANEL */
.fc .fc-ai-hdr { font-size: 13px; font-weight: 700; display: flex; align-items: center; gap: 6px; }
.fc .fc-ai-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--fc-green); animation: fcpulse 1.8s infinite; }
@keyframes fcpulse { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
.fc .fc-ai-score-box { background: var(--fc-green-l); border-radius: 10px; padding: 11px 13px; display: flex; align-items: center; gap: 10px; }
.fc .fc-score-n { font-size: 24px; font-weight: 800; color: var(--fc-green); }
.fc .fc-score-info strong { font-size: 13px; font-weight: 700; color: #065f46; }
.fc .fc-score-info p { font-size: 11px; color: #047857; margin-top: 2px; line-height: 1.5; }
.fc .fc-ai-section-lbl { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: var(--fc-muted); }
.fc .fc-ai-sug { background: var(--fc-white); border: 1.5px solid var(--fc-border); border-radius: 10px; padding: 11px 12px; }
.fc .fc-ai-sug h4 { font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 5px; margin-bottom: 4px; }
.fc .fc-ai-sug p { font-size: 11px; color: var(--fc-muted); line-height: 1.6; margin-bottom: 7px; }
.fc .fc-add-btn { width: 100%; padding: 7px; border: 1.5px dashed var(--fc-border); border-radius: 8px; background: none; font-size: 12px; font-weight: 600; color: var(--fc-blue); cursor: pointer; font-family: 'DM Sans', sans-serif; transition: all .15s; }
.fc .fc-add-btn:hover { border-color: var(--fc-blue); background: var(--fc-blue-l); }
.fc .fc-add-btn.done { border-color: var(--fc-green); background: var(--fc-green-l); color: #065f46; border-style: solid; }
.fc .fc-ai-ask-wrap { display: flex; gap: 6px; }
.fc .fc-ai-ask-wrap input { flex: 1; padding: 8px 10px; border: 1.5px solid var(--fc-border); border-radius: 8px; font-size: 13px; font-family: 'DM Sans', sans-serif; outline: none; }
.fc .fc-ai-ask-wrap input:focus { border-color: var(--fc-blue); }
.fc .fc-ask-btn { background: var(--fc-blue); color: #fff; border: none; border-radius: 8px; padding: 8px 12px; font-size: 13px; font-weight: 600; cursor: pointer; }
.fc .fc-ai-resp { background: var(--fc-white); border: 1.5px solid var(--fc-green); border-radius: 9px; padding: 10px 11px; font-size: 12px; color: var(--fc-dark); line-height: 1.7; display: none; }
.fc .fc-ai-resp.show { display: block; }

/* BUILDER */
.fc .fc-builder-wrap { display: grid; grid-template-columns: 210px 1fr 260px; height: calc(100vh - 104px); }
.fc .fc-b-sidebar { background: var(--fc-white); border-right: 1px solid var(--fc-border); overflow-y: auto; padding: 14px; }
.fc .fc-b-sidebar h3 { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: var(--fc-muted); margin-bottom: 8px; }
.fc .fc-field-types { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-bottom: 18px; }
.fc .fc-ft-item { background: var(--fc-bg); border: 1.5px solid var(--fc-border); border-radius: 8px; padding: 7px 5px; cursor: pointer; text-align: center; transition: all .15s; font-size: 11px; font-weight: 500; color: var(--fc-muted); }
.fc .fc-ft-item:hover { border-color: var(--fc-blue); color: var(--fc-blue); background: var(--fc-blue-l); }
.fc .fc-ft-icon { font-size: 14px; margin-bottom: 2px; }
.fc .fc-b-canvas { background: var(--fc-bg); overflow-y: auto; padding: 18px; }
.fc .fc-canvas-card { background: var(--fc-white); border: 1.5px solid var(--fc-border); border-radius: 10px; overflow: hidden; margin-bottom: 7px; }
.fc .fc-canvas-card.selected { border-color: var(--fc-blue); box-shadow: 0 0 0 3px rgba(26,86,219,.08); }
.fc .fc-canvas-card-hdr { background: var(--fc-bg); padding: 7px 10px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--fc-border); cursor: pointer; }
.fc .fc-canvas-card-label { font-size: 12px; font-weight: 600; color: var(--fc-dark); display: flex; align-items: center; gap: 5px; }
.fc .fc-ftbadge { font-size: 10px; padding: 2px 6px; border-radius: 4px; background: var(--fc-blue-l); color: var(--fc-blue); font-weight: 600; }
.fc .fc-canvas-card-actions { display: flex; gap: 3px; }
.fc .fc-ca-btn { width: 22px; height: 22px; border-radius: 5px; border: 1px solid var(--fc-border); background: var(--fc-white); cursor: pointer; font-size: 10px; display: flex; align-items: center; justify-content: center; color: var(--fc-muted); }
.fc .fc-ca-btn:hover { background: var(--fc-bg); }
.fc .fc-ca-btn.del:hover { background: var(--fc-red-l); border-color: var(--fc-red); color: var(--fc-red); }
.fc .fc-canvas-card-body { padding: 9px 11px; }
.fc .fc-drop-zone { border: 2px dashed var(--fc-border); border-radius: 10px; padding: 32px; text-align: center; color: var(--fc-muted); font-size: 13px; }
.fc .fc-b-props { background: var(--fc-white); border-left: 1px solid var(--fc-border); overflow-y: auto; padding: 14px; }
.fc .fc-b-props h3 { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: var(--fc-muted); margin-bottom: 10px; }
.fc .fc-prop-g { margin-bottom: 10px; }
.fc .fc-prop-lbl { font-size: 12px; font-weight: 600; color: var(--fc-dark); display: block; margin-bottom: 4px; }
.fc .fc-prop-input { width: 100%; padding: 7px 9px; border: 1.5px solid var(--fc-border); border-radius: 8px; font-size: 13px; font-family: 'DM Sans', sans-serif; outline: none; }
.fc .fc-prop-input:focus { border-color: var(--fc-blue); }
.fc .fc-toggle-row { display: flex; align-items: center; justify-content: space-between; padding: 4px 0; }
.fc .fc-toggle { width: 32px; height: 17px; border-radius: 20px; background: var(--fc-border); border: none; cursor: pointer; position: relative; transition: background .2s; }
.fc .fc-toggle.on { background: var(--fc-blue); }
.fc .fc-toggle::after { content: ''; position: absolute; top: 2px; left: 2px; width: 13px; height: 13px; border-radius: 50%; background: #fff; transition: transform .2s; }
.fc .fc-toggle.on::after { transform: translateX(15px); }
.fc .fc-no-sel { text-align: center; padding: 28px 14px; color: var(--fc-muted); }
.fc .fc-opt-row { display: flex; gap: 5px; margin-bottom: 5px; }
.fc .fc-opt-row input { flex: 1; padding: 6px 8px; border: 1.5px solid var(--fc-border); border-radius: 7px; font-size: 12px; font-family: 'DM Sans', sans-serif; outline: none; }
.fc .fc-del-opt { background: none; border: none; cursor: pointer; font-size: 13px; color: var(--fc-muted); }
.fc .fc-add-opt-btn { width: 100%; padding: 6px; border: 1.5px dashed var(--fc-border); border-radius: 7px; background: none; font-size: 12px; color: var(--fc-blue); cursor: pointer; font-family: 'DM Sans', sans-serif; margin-top: 3px; }

/* SUBMISSIONS */
.fc .fc-sub-page { padding: 24px 36px; }
.fc .fc-sub-hdr { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; }
.fc .fc-sub-hdr h2 { font-size: 20px; font-weight: 700; }
.fc .fc-stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.fc .fc-stat-card { background: var(--fc-white); border: 1.5px solid var(--fc-border); border-radius: 12px; padding: 14px 16px; }
.fc .fc-stat-lbl { font-size: 11px; color: var(--fc-muted); font-weight: 500; margin-bottom: 5px; }
.fc .fc-stat-val { font-size: 26px; font-weight: 800; color: var(--fc-dark); }
.fc .fc-stat-sub { font-size: 11px; color: var(--fc-green); margin-top: 3px; font-weight: 500; }
.fc .fc-sub-table { background: var(--fc-white); border: 1.5px solid var(--fc-border); border-radius: 12px; overflow: hidden; }
.fc .fc-sub-table-hdr { display: grid; grid-template-columns: 2fr 1.4fr 1fr 90px 80px; padding: 9px 14px; background: var(--fc-bg); border-bottom: 1px solid var(--fc-border); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: var(--fc-muted); }
.fc .fc-sub-row { display: grid; grid-template-columns: 2fr 1.4fr 1fr 90px 80px; padding: 11px 14px; border-bottom: 1px solid var(--fc-border); font-size: 13px; align-items: center; transition: background .12s; }
.fc .fc-sub-row:last-child { border-bottom: none; }
.fc .fc-sub-row:hover { background: var(--fc-bg); }
.fc .fc-status-new { font-size: 11px; padding: 3px 8px; border-radius: 20px; background: var(--fc-blue-l); color: var(--fc-blue); font-weight: 600; }
.fc .fc-status-read { font-size: 11px; padding: 3px 8px; border-radius: 20px; background: var(--fc-bg); color: var(--fc-muted); font-weight: 600; border: 1px solid var(--fc-border); }
.fc .fc-view-btn { font-size: 11px; padding: 4px 9px; border-radius: 6px; border: 1.5px solid var(--fc-border); background: none; cursor: pointer; color: var(--fc-muted); font-family: 'DM Sans', sans-serif; }
.fc .fc-view-btn:hover { border-color: var(--fc-blue); color: var(--fc-blue); }
.fc .fc-empty-state { text-align: center; padding: 44px; color: var(--fc-muted); }
.fc .fc-btn-ghost { padding: 7px 14px; border-radius: 8px; border: 1.5px solid var(--fc-border); background: none; cursor: pointer; font-size: 13px; font-weight: 500; color: var(--fc-dark); font-family: 'DM Sans', sans-serif; }
.fc .fc-btn-primary { padding: 7px 16px; border-radius: 8px; border: none; background: var(--fc-blue); color: #fff; cursor: pointer; font-size: 13px; font-weight: 600; font-family: 'DM Sans', sans-serif; }

/* DETAIL MODAL */
.fc .fc-detail-modal { background: var(--fc-white); border-radius: 16px; width: 100%; max-width: 540px; margin: auto; overflow: hidden; animation: fcslideUp .2s ease; }
.fc .fc-detail-body { padding: 20px 22px; overflow-y: auto; max-height: 68vh; }
.fc .fc-detail-field { border-bottom: 1px solid var(--fc-border); padding: 9px 0; }
.fc .fc-detail-field:last-child { border-bottom: none; }
.fc .fc-detail-key { font-size: 11px; font-weight: 700; color: var(--fc-muted); margin-bottom: 3px; text-transform: capitalize; }
.fc .fc-detail-val { font-size: 14px; color: var(--fc-dark); }

@media (max-width: 768px) {
  .fc .fc-grid { padding: 14px; grid-template-columns: 1fr; }
  .fc .fc-hero h1 { font-size: 28px; }
  .fc .fc-mbody { grid-template-columns: 1fr; }
  .fc .fc-mai { display: none; }
  .fc .fc-stats-grid { grid-template-columns: 1fr 1fr; }
  .fc .fc-sub-page { padding: 14px; }
  .fc .fc-builder-wrap { grid-template-columns: 1fr; }
  .fc .fc-b-sidebar, .fc .fc-b-props { display: none; }
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/src/pages/formcraft/formcraft.css
git commit -m "feat: add scoped FormCraft CSS"
```

---

## Task 8: Frontend — TemplatesPage

**Files:**
- Create: `frontend/src/pages/formcraft/TemplatesPage.jsx`

- [ ] **Step 1: Create `frontend/src/pages/formcraft/TemplatesPage.jsx`**

```jsx
import { useState, useEffect } from 'react'
import './formcraft.css'

const AI_RESPONSES = [
  "Great idea! Adding a WhatsApp opt-in will boost follow-up reach significantly.",
  "You can add a 'Preferred contact time' dropdown with Morning / Afternoon / Evening options.",
  "Consider adding a CAPTCHA or honeypot field to prevent spam submissions.",
  "A progress bar at the top increases form completion rate by up to 28%.",
  "Making phone field show +91 prefix by default reduces input errors.",
  "Adding 'How did you hear about us?' dropdown helps track marketing channels.",
]

function renderField(f, idx, starState, setStarState) {
  if (!f || !f.type) return null
  if (f.type === 'section') return <div key={idx} className="fc-fsec">{f.label}</div>
  if (f.type === 'cardicons') return (
    <div key={idx} style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
      {['VISA', 'MC', 'UPI', 'PayPal'].map(b => (
        <span key={b} style={{ fontSize: 11, fontWeight: 600, background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 5, padding: '3px 9px', color: '#64748b' }}>{b}</span>
      ))}
    </div>
  )
  if (f.type === 'cardnum') return (
    <div key={idx} className="fc-fg">
      <label>Card number <span className="fc-req">*</span></label>
      <input type="text" name="card_number" placeholder="1234  5678  9012  3456" maxLength={19} />
    </div>
  )
  if (f.type === 'row3card') return (
    <div key={idx} className="fc-frow3">
      <div className="fc-fg"><label>Expiry <span className="fc-req">*</span></label><input type="text" name="expiry" placeholder="MM / YY" /></div>
      <div className="fc-fg"><label>CVV <span className="fc-req">*</span></label><input type="text" name="cvv" placeholder="123" maxLength={4} /></div>
      <div className="fc-fg"><label>ZIP</label><input type="text" name="zip" placeholder="302001" /></div>
    </div>
  )
  if (f.type === 'submit') return null
  if (f.type === 'row2') return (
    <div key={idx} className="fc-frow">
      {(f.fields || []).map((ff, i) => renderField(ff, `${idx}_${i}`, starState, setStarState))}
    </div>
  )
  if (f.type === 'rating') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <div className="fc-star-row">
        {[1, 2, 3, 4, 5].map(v => (
          <span
            key={v}
            className={`fc-star${(starState[idx] || 0) >= v ? ' on' : ''}`}
            onClick={() => setStarState(s => ({ ...s, [idx]: v }))}
          >★</span>
        ))}
      </div>
    </div>
  )
  if (f.type === 'range') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <input type="range" name={f.label || 'range'} min="0" max="10" defaultValue="7" style={{ accentColor: '#d97706', width: '100%' }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#64748b', marginTop: 2 }}>
        <span>0</span><span>10</span>
      </div>
    </div>
  )
  if (f.type === 'radio') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <div className="fc-radio-g">
        {(f.options || []).map(o => (
          <label key={o} className="fc-radio-opt">
            <input type="radio" name={f.label || `radio_${idx}`} value={o} />{o}
          </label>
        ))}
      </div>
    </div>
  )
  if (f.type === 'checkbox') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}</label>
      <div className="fc-check-g">
        {(f.options || []).map(o => (
          <label key={o} className="fc-check-opt">
            <input type="checkbox" name={`${f.label || 'check'}_${idx}`} value={o} />{o}
          </label>
        ))}
      </div>
    </div>
  )
  if (f.type === 'select') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <select name={f.label || `select_${idx}`} required={f.required}>
        <option value="">Select...</option>
        {(f.options || []).map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  )
  if (f.type === 'textarea') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <textarea name={f.label || `textarea_${idx}`} placeholder={f.placeholder || ''} required={f.required} />
    </div>
  )
  if (f.type === 'file') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <input type="file" name={f.label || `file_${idx}`} style={{ padding: 6 }} required={f.required} />
    </div>
  )
  if (f.type === 'divider') return <hr key={idx} style={{ border: 'none', borderTop: '1.5px dashed #e2e8f0', margin: '8px 0 14px' }} />
  const itype = f.type === 'email' ? 'email' : f.type === 'phone' ? 'tel' : f.type === 'number' ? 'number' : 'text'
  return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <input type={itype} name={f.label || `${f.type}_${idx}`} placeholder={f.placeholder || ''} required={f.required} />
    </div>
  )
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState([])
  const [activeFilter, setActiveFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [currentTemplate, setCurrentTemplate] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [starState, setStarState] = useState({})
  const [addedSugs, setAddedSugs] = useState({})
  const [aiInput, setAiInput] = useState('')
  const [aiResp, setAiResp] = useState('')
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    fetch('/api/').then(r => r.ok ? setApiStatus('ok') : setApiStatus('err')).catch(() => setApiStatus('err'))
    fetch('/api/templates').then(r => r.json()).then(setTemplates).catch(() => {})
  }, [])

  const filtered = templates.filter(t => {
    const mc = activeFilter === 'all' || t.category === activeFilter
    const mq = !search || t.title.toLowerCase().includes(search.toLowerCase()) ||
      (t.tags || []).some(tg => tg.toLowerCase().includes(search.toLowerCase()))
    return mc && mq
  })

  const openModal = t => { setCurrentTemplate(t); setIsModalOpen(true); setSubmitted(false); setStarState({}); setAddedSugs({}); setAiResp('') }
  const closeModal = () => { setIsModalOpen(false); setCurrentTemplate(null) }

  const handleSubmit = async e => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const data = {}
    for (let [k, v] of formData.entries()) {
      if (data[k]) data[k] = Array.isArray(data[k]) ? [...data[k], v] : [data[k], v]
      else data[k] = v
    }
    Object.keys(data).forEach(k => { if (!data[k]) delete data[k] })
    if (!Object.keys(data).length) { alert('Please fill in at least one field!'); return }
    setSubmitting(true)
    try {
      await fetch('/api/submissions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_id: currentTemplate.id, form_title: currentTemplate.title, data }),
      })
      setSubmitted(true)
      setTimeout(closeModal, 2500)
    } catch { alert('Failed to save. Make sure the backend is running.') }
    finally { setSubmitting(false) }
  }

  const askAI = () => {
    if (!aiInput.trim()) return
    setAiResp('🤔 Thinking...')
    setTimeout(() => {
      setAiResp('🤖 ' + AI_RESPONSES[Math.floor(Math.random() * AI_RESPONSES.length)])
    }, 700)
    setAiInput('')
  }

  const submitLabel = currentTemplate?.fields?.find(f => f.type === 'submit')?.label || 'Submit'
  const submitColor = currentTemplate?.fields?.find(f => f.type === 'submit')?.color || '#1a56db'

  return (
    <div className="fc">
      {/* Hero */}
      <div className="fc-hero">
        <div className="fc-hero-tag">✦ Real PostgreSQL Backend</div>
        <h1>Forms that <em>convert</em><br />& impress</h1>
        <p>Click any template to preview it instantly. All submissions saved to PostgreSQL.</p>
        <div className="fc-search-wrap">
          <input placeholder="Search templates..." value={search} onChange={e => setSearch(e.target.value)} />
          <button onClick={() => {}}>Search</button>
        </div>
        <div style={{ marginTop: 12, fontSize: 12, color: apiStatus === 'ok' ? '#065f46' : '#991b1b' }}>
          {apiStatus === 'checking' ? '⚡ Checking API...' : apiStatus === 'ok' ? '🟢 API Connected' : '🔴 API Offline'}
        </div>
      </div>

      {/* Filters */}
      <div className="fc-filter-row">
        {[['all','All'],['payment','💳 Payment'],['contact','📬 Contact'],['registration','📝 Registration'],['feedback','⭐ Feedback'],['business','💼 Business']].map(([f, label]) => (
          <button key={f} className={`fc-filter-pill${activeFilter === f ? ' active' : ''}`} onClick={() => setActiveFilter(f)}>{label}</button>
        ))}
      </div>

      {/* Grid */}
      <div className="fc-grid">
        {filtered.length === 0 && <div className="fc-loading"><div className="fc-spinner" /><p>No templates found</p></div>}
        {filtered.map(t => (
          <div key={t.id} className="fc-tcard" onClick={() => openModal(t)}>
            <div className="fc-tcard-preview" style={{ background: `${t.color}18` }}>
              {t.badge && <div className="fc-badge-pill" style={{ color: t.color }}>{t.badge}</div>}
              <div className="fc-mf title" /><div className="fc-mf lbl" /><div className="fc-mf" />
              <div className="fc-mf lbl" style={{ width: '50%' }} /><div className="fc-mf" />
              <div className="fc-mf btn" style={{ background: `${t.color}cc` }} />
            </div>
            <div className="fc-tcard-body">
              <div className="fc-tcard-cat">{t.category}</div>
              <div className="fc-tcard-title">{t.title}</div>
              <div className="fc-tcard-desc">{t.description}</div>
              <div className="fc-tcard-foot">
                <div className="fc-tags">{(t.tags || []).map(tg => <span key={tg} className="fc-tag">{tg}</span>)}</div>
                <button className="fc-use-btn" onClick={e => { e.stopPropagation(); openModal(t) }}>Use →</button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {isModalOpen && currentTemplate && (
        <div className="fc-overlay open" onClick={e => e.target.classList.contains('fc-overlay') && closeModal()}>
          <div className="fc-modal">
            <div className="fc-mhdr">
              <div className="fc-mhdr-l">
                <h2>{currentTemplate.title}</h2>
                <p>{currentTemplate.description}</p>
              </div>
              <button className="fc-mclose" onClick={closeModal}>✕</button>
            </div>
            <div className="fc-mbody">
              <div className="fc-mform">
                {submitted ? (
                  <div className="fc-form-success show"><span style={{ display: 'block', fontSize: 28, marginBottom: 6 }}>✅</span>Submitted successfully!</div>
                ) : (
                  <form onSubmit={handleSubmit}>
                    {(currentTemplate.fields || []).filter(f => f.type !== 'submit').map((f, i) => renderField(f, i, starState, setStarState))}
                    <button type="submit" className="fc-submit-btn" style={{ background: submitColor }} disabled={submitting}>
                      {submitting ? '⏳ Saving...' : submitLabel}
                    </button>
                  </form>
                )}
              </div>
              <div className="fc-mai">
                <div className="fc-ai-hdr"><span className="fc-ai-dot" />AI Suggestions</div>
                <div className="fc-ai-score-box">
                  <div className="fc-score-n">{currentTemplate.score || 70}</div>
                  <div className="fc-score-info"><strong>Form Score</strong><p>{currentTemplate.score_tip || 'Keep improving!'}</p></div>
                </div>
                <div className="fc-ai-section-lbl">Recommended fields</div>
                {(currentTemplate.suggestions || []).map((s, i) => (
                  <div key={i} className="fc-ai-sug">
                    <h4>{s.icon} {s.title}</h4>
                    <p>{s.text}</p>
                    <button className={`fc-add-btn${addedSugs[i] ? ' done' : ''}`} onClick={() => setAddedSugs(p => ({ ...p, [i]: true }))}>
                      {addedSugs[i] ? '✓ Added' : '+ Add this field'}
                    </button>
                  </div>
                ))}
                <div className="fc-ai-section-lbl">Ask AI anything</div>
                <div className="fc-ai-ask-wrap">
                  <input placeholder="e.g. add a rating field..." value={aiInput} onChange={e => setAiInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && askAI()} />
                  <button className="fc-ask-btn" onClick={askAI}>Ask</button>
                </div>
                {aiResp && <div className="fc-ai-resp show">{aiResp}</div>}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/src/pages/formcraft/TemplatesPage.jsx
git commit -m "feat: add TemplatesPage React component"
```

---

## Task 9: Frontend — BuilderPage

**Files:**
- Create: `frontend/src/pages/formcraft/BuilderPage.jsx`

- [ ] **Step 1: Create `frontend/src/pages/formcraft/BuilderPage.jsx`**

```jsx
import { useState } from 'react'
import './formcraft.css'

const B_DEFAULTS = {
  text:     { label: 'Short Text',     placeholder: 'Type here...',         required: false },
  email:    { label: 'Email Address',  placeholder: 'you@email.com',        required: true  },
  phone:    { label: 'Phone Number',   placeholder: '+91 98765 43210',      required: false },
  textarea: { label: 'Long Text',      placeholder: 'Write here...',        required: false },
  select:   { label: 'Dropdown',       options: ['Option 1','Option 2','Option 3'], required: false },
  radio:    { label: 'Multiple Choice',options: ['Option 1','Option 2','Option 3'], required: false },
  checkbox: { label: 'Checkboxes',     options: ['Option A','Option B','Option C'], required: false },
  number:   { label: 'Number',         placeholder: '0',                    required: false },
  date:     { label: 'Date',           placeholder: '',                     required: false },
  file:     { label: 'File Upload',                                          required: false },
  rating:   { label: 'Star Rating',                                          required: false },
  divider:  { label: 'Divider' },
}

const FIELD_TYPES = [
  ['text','📝','Text'],['email','📧','Email'],['phone','📱','Phone'],
  ['textarea','📄','Long Text'],['select','📋','Dropdown'],['radio','🔘','Radio'],
  ['checkbox','☑️','Checkbox'],['number','🔢','Number'],['date','📅','Date'],
  ['file','📎','File'],['rating','⭐','Rating'],['divider','➖','Divider'],
]

let _counter = 0

function FieldPreview({ f }) {
  if (f.type === 'radio' || f.type === 'checkbox')
    return <div style={{ fontSize: 11, color: '#64748b' }}>{(f.options || []).map(o => `${f.type === 'radio' ? '◯' : '☐'} ${o}`).join('  ')}</div>
  if (f.type === 'rating')
    return <div style={{ fontSize: 16, color: '#d97706' }}>★★★★★</div>
  if (f.type === 'divider')
    return <hr style={{ border: 'none', borderTop: '2px dashed #e2e8f0' }} />
  if (f.type === 'textarea')
    return <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b', height: 36 }}>{f.placeholder || ''}</div>
  if (f.type === 'select')
    return <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b' }}>{(f.options || [])[0] || 'Select...'} ▾</div>
  if (f.type === 'file')
    return <div style={{ background: '#f8fafc', border: '1.5px dashed #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b', textAlign: 'center' }}>📎 Choose file</div>
  return <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b' }}>{f.placeholder || 'Input field'}</div>
}

export default function BuilderPage() {
  const [title, setTitle] = useState('Untitled Form')
  const [fields, setFields] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [saving, setSaving] = useState(false)

  const addField = type => {
    const id = `bf_${++_counter}`
    const newField = { id, type, ...JSON.parse(JSON.stringify(B_DEFAULTS[type] || { label: 'Field' })) }
    setFields(f => [...f, newField])
    setSelectedId(id)
  }

  const updateField = (id, key, value) =>
    setFields(f => f.map(fi => fi.id === id ? { ...fi, [key]: value } : fi))

  const moveField = (id, dir) => {
    setFields(f => {
      const idx = f.findIndex(fi => fi.id === id)
      const ni = idx + dir
      if (ni < 0 || ni >= f.length) return f
      const copy = [...f]
      ;[copy[idx], copy[ni]] = [copy[ni], copy[idx]]
      return copy
    })
  }

  const deleteField = id => {
    setFields(f => f.filter(fi => fi.id !== id))
    if (selectedId === id) setSelectedId(null)
  }

  const updateOption = (id, i, v) =>
    setFields(f => f.map(fi => {
      if (fi.id !== id) return fi
      const opts = [...(fi.options || [])]
      opts[i] = v
      return { ...fi, options: opts }
    }))

  const addOption = id =>
    setFields(f => f.map(fi => fi.id === id ? { ...fi, options: [...(fi.options || []), 'New option'] } : fi))

  const removeOption = (id, i) =>
    setFields(f => f.map(fi => {
      if (fi.id !== id) return fi
      const opts = [...(fi.options || [])]
      opts.splice(i, 1)
      return { ...fi, options: opts }
    }))

  const saveToDb = async () => {
    if (!fields.length) { alert('Add some fields first!'); return }
    setSaving(true)
    try {
      const res = await fetch('/api/forms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, fields }),
      })
      const data = await res.json()
      alert(`✅ Form "${data.title}" saved! ID: ${data.id}`)
    } catch { alert('❌ Save failed. Make sure the backend is running.') }
    finally { setSaving(false) }
  }

  const selected = fields.find(f => f.id === selectedId)
  const hasOpts = selected && ['radio', 'checkbox', 'select'].includes(selected.type)
  const hasPlaceholder = selected && !['radio', 'checkbox', 'select', 'rating', 'divider', 'file'].includes(selected.type)

  const aiTips = []
  if (!fields.some(f => f.type === 'email')) aiTips.push({ t: 'Add Email field', fn: () => addField('email') })
  if (!fields.some(f => f.type === 'phone')) aiTips.push({ t: 'Add Phone field', fn: () => addField('phone') })

  return (
    <div className="fc">
      {/* Builder toolbar */}
      <div style={{ background: '#fff', borderBottom: '1px solid #e2e8f0', padding: '9px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 12, color: '#64748b' }}>Form name:</span>
          <input value={title} onChange={e => setTitle(e.target.value)} style={{ border: 'none', outline: 'none', fontSize: 14, fontWeight: 600, fontFamily: "'DM Sans', sans-serif", color: '#0f172a' }} />
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="fc-btn-primary" onClick={saveToDb} disabled={saving}>{saving ? '⏳ Saving...' : '💾 Save to DB'}</button>
        </div>
      </div>

      <div className="fc-builder-wrap">
        {/* Left: field types */}
        <div className="fc-b-sidebar">
          <h3>Add Fields</h3>
          <div className="fc-field-types">
            {FIELD_TYPES.map(([type, icon, label]) => (
              <div key={type} className="fc-ft-item" onClick={() => addField(type)}>
                <div className="fc-ft-icon">{icon}</div>{label}
              </div>
            ))}
          </div>
          <h3>AI Tips</h3>
          {aiTips.length === 0
            ? <p style={{ fontSize: 11, color: '#64748b' }}>Form looks great! 🎉</p>
            : aiTips.slice(0, 2).map((tip, i) => (
              <div key={i} className="fc-ai-sug">
                <p style={{ margin: '0 0 5px', fontSize: 12, fontWeight: 600 }}>💡 {tip.t}</p>
                <button className="fc-add-btn" onClick={tip.fn}>+ Add</button>
              </div>
            ))}
        </div>

        {/* Center: canvas */}
        <div className="fc-b-canvas">
          {fields.length === 0 && <div className="fc-drop-zone">👈 Click a field type to add it here</div>}
          {fields.map(f => (
            <div key={f.id} className={`fc-canvas-card${selectedId === f.id ? ' selected' : ''}`} onClick={() => setSelectedId(f.id)}>
              <div className="fc-canvas-card-hdr">
                <div className="fc-canvas-card-label">
                  <span className="fc-ftbadge">{f.type}</span>
                  {f.label}{f.required && <span style={{ color: '#dc2626' }}>*</span>}
                </div>
                <div className="fc-canvas-card-actions">
                  <button className="fc-ca-btn" onClick={e => { e.stopPropagation(); moveField(f.id, -1) }}>↑</button>
                  <button className="fc-ca-btn" onClick={e => { e.stopPropagation(); moveField(f.id, 1) }}>↓</button>
                  <button className="fc-ca-btn del" onClick={e => { e.stopPropagation(); deleteField(f.id) }}>🗑</button>
                </div>
              </div>
              <div className="fc-canvas-card-body"><FieldPreview f={f} /></div>
            </div>
          ))}
        </div>

        {/* Right: props */}
        <div className="fc-b-props">
          <h3>Field Settings</h3>
          {!selected
            ? <div className="fc-no-sel"><p style={{ fontSize: 26, marginBottom: 8 }}>⚙️</p><p>Select a field to edit</p></div>
            : (
              <>
                <div className="fc-prop-g">
                  <label className="fc-prop-lbl">Label</label>
                  <input className="fc-prop-input" value={selected.label} onChange={e => updateField(selected.id, 'label', e.target.value)} />
                </div>
                {hasPlaceholder && (
                  <div className="fc-prop-g">
                    <label className="fc-prop-lbl">Placeholder</label>
                    <input className="fc-prop-input" value={selected.placeholder || ''} onChange={e => updateField(selected.id, 'placeholder', e.target.value)} />
                  </div>
                )}
                {hasOpts && (
                  <div className="fc-prop-g">
                    <label className="fc-prop-lbl">Options</label>
                    {(selected.options || []).map((o, i) => (
                      <div key={i} className="fc-opt-row">
                        <input value={o} onChange={e => updateOption(selected.id, i, e.target.value)} />
                        <button className="fc-del-opt" onClick={() => removeOption(selected.id, i)}>×</button>
                      </div>
                    ))}
                    <button className="fc-add-opt-btn" onClick={() => addOption(selected.id)}>+ Add option</button>
                  </div>
                )}
                {selected.type !== 'divider' && (
                  <div className="fc-prop-g">
                    <div className="fc-toggle-row">
                      <span style={{ fontSize: 12, fontWeight: 600 }}>Required</span>
                      <button className={`fc-toggle${selected.required ? ' on' : ''}`} onClick={() => updateField(selected.id, 'required', !selected.required)} />
                    </div>
                  </div>
                )}
                <button onClick={() => deleteField(selected.id)} style={{ width: '100%', padding: 8, border: '1.5px solid #dc2626', borderRadius: 8, background: '#fee2e2', color: '#dc2626', cursor: 'pointer', fontSize: 13, fontWeight: 600, fontFamily: "'DM Sans', sans-serif", marginTop: 4 }}>
                  Remove Field
                </button>
              </>
            )}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/src/pages/formcraft/BuilderPage.jsx
git commit -m "feat: add BuilderPage React component"
```

---

## Task 10: Frontend — SubmissionsPage

**Files:**
- Create: `frontend/src/pages/formcraft/SubmissionsPage.jsx`

- [ ] **Step 1: Create `frontend/src/pages/formcraft/SubmissionsPage.jsx`**

```jsx
import { useState, useEffect } from 'react'
import './formcraft.css'

export default function SubmissionsPage() {
  const [submissions, setSubmissions] = useState([])
  const [stats, setStats] = useState(null)
  const [selectedSub, setSelectedSub] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [subs, st] = await Promise.all([
        fetch('/api/submissions').then(r => r.json()),
        fetch('/api/stats').then(r => r.json()),
      ])
      setSubmissions(subs)
      setStats(st)
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const viewSub = async id => {
    const s = await fetch(`/api/submissions/${id}`).then(r => r.json())
    setSelectedSub(s)
    await fetch(`/api/submissions/${id}/read`, { method: 'PATCH' })
    load()
  }

  const clearAll = async () => {
    if (!confirm('Delete ALL submissions? This cannot be undone.')) return
    await fetch('/api/submissions', { method: 'DELETE' })
    load()
  }

  const exportCSV = () => {
    if (!submissions.length) { alert('No submissions to export.'); return }
    const rows = [['ID', 'Form', 'Date', 'Status', 'Data']]
    submissions.forEach(s => rows.push([s.id, s.form_title, s.submitted_at, s.status, JSON.stringify(s.data)]))
    const csv = rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n')
    const a = document.createElement('a')
    a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv)
    a.download = 'formcraft_submissions.csv'
    a.click()
  }

  return (
    <div className="fc">
      <div className="fc-sub-page">
        <div className="fc-sub-hdr">
          <h2>📊 Submissions</h2>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="fc-btn-ghost" onClick={exportCSV}>⬇️ Export CSV</button>
            <button className="fc-btn-ghost" style={{ borderColor: '#dc2626', color: '#dc2626' }} onClick={clearAll}>🗑 Clear All</button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="fc-stats-grid">
            {[
              { l: 'Total Submissions', v: stats.total, s: 'All time' },
              { l: 'New (Unread)', v: stats.new, s: 'Needs review' },
              { l: 'Today', v: stats.today, s: 'Submitted today' },
              { l: 'Completion Rate', v: stats.completion_rate, s: 'This week' },
            ].map(s => (
              <div key={s.l} className="fc-stat-card">
                <div className="fc-stat-lbl">{s.l}</div>
                <div className="fc-stat-val">{s.v}</div>
                <div className="fc-stat-sub">{s.s}</div>
              </div>
            ))}
          </div>
        )}

        {/* Table */}
        <div className="fc-sub-table">
          <div className="fc-sub-table-hdr">
            <div>Submission</div><div>Form</div><div>Date</div><div>Status</div><div>Action</div>
          </div>
          {loading
            ? <div className="fc-loading"><div className="fc-spinner" /></div>
            : submissions.length === 0
            ? <div className="fc-empty-state"><div style={{ fontSize: 36, marginBottom: 10 }}>📭</div><p>No submissions yet.</p></div>
            : submissions.map(s => (
              <div key={s.id} className="fc-sub-row">
                <div style={{ fontWeight: 500 }}>#{s.id} — {Object.values(s.data || {})[0] || 'Anonymous'}</div>
                <div style={{ color: '#64748b', fontSize: 12 }}>{s.form_title}</div>
                <div style={{ color: '#64748b', fontSize: 12 }}>{new Date(s.submitted_at).toLocaleDateString('en-IN')}</div>
                <div><span className={`fc-status-${s.status}`}>{s.status === 'new' ? '🔵 New' : '✅ Read'}</span></div>
                <div><button className="fc-view-btn" onClick={() => viewSub(s.id)}>View</button></div>
              </div>
            ))
          }
        </div>
      </div>

      {/* Detail modal */}
      {selectedSub && (
        <div className="fc-overlay open" onClick={e => e.target.classList.contains('fc-overlay') && setSelectedSub(null)}>
          <div className="fc-detail-modal">
            <div className="fc-mhdr">
              <div className="fc-mhdr-l"><h2>Submission Detail</h2></div>
              <button className="fc-mclose" onClick={() => setSelectedSub(null)}>✕</button>
            </div>
            <div className="fc-detail-body">
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 11, color: '#64748b', marginBottom: 3 }}>Form</div>
                <div style={{ fontWeight: 600 }}>{selectedSub.form_title}</div>
              </div>
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 11, color: '#64748b', marginBottom: 3 }}>Submitted</div>
                <div>{new Date(selectedSub.submitted_at).toLocaleString('en-IN')}</div>
              </div>
              {Object.entries(selectedSub.data || {}).map(([k, v]) => (
                <div key={k} className="fc-detail-field">
                  <div className="fc-detail-key">{k}</div>
                  <div className="fc-detail-val">{Array.isArray(v) ? v.join(', ') : String(v)}</div>
                </div>
              ))}
              <button className="fc-btn-primary" style={{ width: '100%', marginTop: 18, padding: 11 }} onClick={() => setSelectedSub(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/src/pages/formcraft/SubmissionsPage.jsx
git commit -m "feat: add SubmissionsPage React component"
```

---

## Task 11: Frontend — Move QueryMind components

**Files:**
- Create: `frontend/src/pages/querymind/ConnectScreen.jsx`
- Create: `frontend/src/pages/querymind/ChatScreen.jsx`

- [ ] **Step 1: Copy ConnectScreen**

```bash
cp /Users/vishaljangid/learning/harshit/jotform/frontend/src/components/ConnectScreen.jsx \
   /Users/vishaljangid/learning/harshit/jotform/frontend/src/pages/querymind/ConnectScreen.jsx
```

- [ ] **Step 2: Copy ChatScreen**

```bash
cp /Users/vishaljangid/learning/harshit/jotform/frontend/src/components/ChatScreen.jsx \
   /Users/vishaljangid/learning/harshit/jotform/frontend/src/pages/querymind/ChatScreen.jsx
```

- [ ] **Step 3: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/src/pages/querymind/
git commit -m "feat: move QueryMind components to pages/querymind"
```

---

## Task 12: Frontend — Update App.jsx

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Replace `frontend/src/App.jsx` with full routing**

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Navbar from './components/Navbar'
import TemplatesPage from './pages/formcraft/TemplatesPage'
import BuilderPage from './pages/formcraft/BuilderPage'
import SubmissionsPage from './pages/formcraft/SubmissionsPage'
import ConnectScreen from './pages/querymind/ConnectScreen'
import ChatScreen from './pages/querymind/ChatScreen'

function QueryMindApp() {
  const [session, setSession] = useState(null)
  return session
    ? <ChatScreen session={session} onDisconnect={() => setSession(null)} />
    : <ConnectScreen onConnect={setSession} />
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to="/formcraft" replace />} />
        <Route path="/formcraft" element={<TemplatesPage />} />
        <Route path="/formcraft/builder" element={<BuilderPage />} />
        <Route path="/formcraft/submissions" element={<SubmissionsPage />} />
        <Route path="/querymind" element={<QueryMindApp />} />
        <Route path="*" element={<Navigate to="/formcraft" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/src/App.jsx
git commit -m "feat: add React Router with FormCraft and QueryMind routes"
```

---

## Task 13: Frontend — Update vite.config.js

**Files:**
- Modify: `frontend/vite.config.js`

- [ ] **Step 1: Update `frontend/vite.config.js`**

Remove the `rewrite` — both apps now use `/api/` prefix on the merged backend.

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/vite.config.js
git commit -m "feat: update vite proxy — remove rewrite, all /api/* → backend:8000"
```

---

## Task 14: Update start.sh

**Files:**
- Modify: `start.sh`

- [ ] **Step 1: Update `start.sh`**

```bash
#!/bin/bash

ROOT="$(cd "$(dirname "$0")" && pwd)"

source "$ROOT/myvenv/bin/activate"

mkdir -p "$ROOT/logs"

echo "Starting Backend   → http://localhost:8000"
echo "Starting Frontend  → http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all."
echo ""

cd "$ROOT/backend" && uvicorn main:app --reload --port 8000 > "$ROOT/logs/backend.log" 2>&1 &
BACKEND_PID=$!

cd "$ROOT/frontend" && npm run dev > "$ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!

trap "echo ''; echo 'Stopping all...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

wait
```

- [ ] **Step 2: Make executable and commit**

```bash
chmod +x /Users/vishaljangid/learning/harshit/jotform/start.sh
cd /Users/vishaljangid/learning/harshit/jotform
git add start.sh
git commit -m "feat: update start.sh for merged single backend"
```

---

## Task 15: Add FormCraft nav tabs to TemplatesPage

The FormCraft section needs its own sub-navigation (Templates / Builder / Submissions).

**Files:**
- Modify: `frontend/src/pages/formcraft/TemplatesPage.jsx`
- Modify: `frontend/src/pages/formcraft/BuilderPage.jsx`
- Modify: `frontend/src/pages/formcraft/SubmissionsPage.jsx`

- [ ] **Step 1: Create `frontend/src/pages/formcraft/FormCraftNav.jsx`**

```jsx
import { NavLink } from 'react-router-dom'
import './formcraft.css'

export default function FormCraftNav() {
  const style = ({ isActive }) => ({
    padding: '6px 14px',
    borderRadius: 8,
    background: isActive ? '#e8f0fe' : 'none',
    color: isActive ? '#1a56db' : '#64748b',
    fontWeight: 500,
    fontSize: 13,
    textDecoration: 'none',
    border: 'none',
    cursor: 'pointer',
    fontFamily: "'DM Sans', sans-serif",
  })
  return (
    <div style={{ background: '#fff', borderBottom: '1px solid #e2e8f0', padding: '0 32px', display: 'flex', gap: 4, height: 46, alignItems: 'center' }}>
      <NavLink to="/formcraft" end style={style}>📋 Templates</NavLink>
      <NavLink to="/formcraft/builder" style={style}>🛠 Builder</NavLink>
      <NavLink to="/formcraft/submissions" style={style}>📊 Submissions</NavLink>
    </div>
  )
}
```

- [ ] **Step 2: Add `<FormCraftNav />` to the top of TemplatesPage, BuilderPage, SubmissionsPage**

In `TemplatesPage.jsx`, add at top of return after `<div className="fc">`:
```jsx
import FormCraftNav from './FormCraftNav'
// ...
return (
  <div className="fc">
    <FormCraftNav />
    {/* rest of content */}
```

In `BuilderPage.jsx`, add at top of return after `<div className="fc">`:
```jsx
import FormCraftNav from './FormCraftNav'
// ...
return (
  <div className="fc">
    <FormCraftNav />
    {/* builder toolbar and wrap */}
```

In `SubmissionsPage.jsx`, add at top of return after `<div className="fc">`:
```jsx
import FormCraftNav from './FormCraftNav'
// ...
return (
  <div className="fc">
    <FormCraftNav />
    <div className="fc-sub-page">
```

- [ ] **Step 3: Commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add frontend/src/pages/formcraft/FormCraftNav.jsx \
         frontend/src/pages/formcraft/TemplatesPage.jsx \
         frontend/src/pages/formcraft/BuilderPage.jsx \
         frontend/src/pages/formcraft/SubmissionsPage.jsx
git commit -m "feat: add FormCraft sub-navigation tabs"
```

---

## Task 16: Cleanup old files

- [ ] **Step 1: Delete old root Python files**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
rm main.py models.py schemas.py database.py seed.py
```

- [ ] **Step 2: Delete old backend files**

```bash
rm backend/main.py backend/db_connector.py backend/ai_engine.py
```

- [ ] **Step 3: Delete old frontend components**

```bash
rm frontend/src/components/ConnectScreen.jsx
rm frontend/src/components/ChatScreen.jsx
```

- [ ] **Step 4: Delete old HTML file**

```bash
rm "Formcraft with backend .html"
```

- [ ] **Step 5: Final commit**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
git add -A
git commit -m "chore: remove old files after merge — FormCraft + QueryMind unified"
```

---

## Task 17: Final verification

- [ ] **Step 1: Start everything**

```bash
cd /Users/vishaljangid/learning/harshit/jotform
./start.sh
```

- [ ] **Step 2: Verify backend health**

```bash
curl http://localhost:8000/api/
# Expected: {"status":"ok","message":"FormCraft API is running"}

curl http://localhost:8000/api/health
# Expected: {"status":"ok","version":"2.0.0"}

curl http://localhost:8000/api/templates
# Expected: JSON array of templates
```

- [ ] **Step 3: Verify frontend**

Open `http://localhost:3000` in browser.
- Should redirect to `/formcraft`
- FormCraft templates should load
- Clicking QueryMind nav link should show QueryMind connect screen
- Builder page at `/formcraft/builder` should work
- Submissions at `/formcraft/submissions` should show stats

- [ ] **Step 4: Seed templates if empty**

```bash
cd /Users/vishaljangid/learning/harshit/jotform/backend
python seed.py
# Expected: ✅ Seeded 4 templates
```
