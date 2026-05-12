from __future__ import annotations
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from groq import Groq

from formcraft.database import SessionLocal
from auth.utils import decode_token
from .models import KnowledgeBase, KBDocument
from .retriever import retrieve

router = APIRouter(prefix="/api/rag")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _user_id(authorization: Optional[str]) -> Optional[int]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    data = decode_token(authorization.split(" ", 1)[1])
    if not data:
        return None
    return int(data.get("sub", 0)) or None


class CreateKBRequest(BaseModel):
    name: str
    description: str = ""
    groq_api_key: str


class ChatRequest(BaseModel):
    question: str
    history: List[dict] = []


@router.post("/kb")
def create_kb(
    req: CreateKBRequest,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    user_id = _user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    kb = KnowledgeBase(
        user_id=user_id,
        name=req.name.strip(),
        description=req.description.strip(),
        groq_api_key=req.groq_api_key.strip(),
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return {"id": kb.id, "name": kb.name, "description": kb.description, "created_at": kb.created_at, "doc_count": 0}


@router.get("/kb")
def list_kbs(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    user_id = _user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    kbs = db.query(KnowledgeBase).filter(KnowledgeBase.user_id == user_id).order_by(KnowledgeBase.id.desc()).all()
    result = []
    for kb in kbs:
        doc_count = db.query(KBDocument).filter(KBDocument.kb_id == kb.id).count()
        result.append({"id": kb.id, "name": kb.name, "description": kb.description, "created_at": kb.created_at, "doc_count": doc_count})
    return result


@router.get("/kb/{kb_id}")
def get_kb(
    kb_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    user_id = _user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    docs = db.query(KBDocument).filter(KBDocument.kb_id == kb_id).order_by(KBDocument.id.desc()).all()
    return {
        "id": kb.id,
        "name": kb.name,
        "description": kb.description,
        "created_at": kb.created_at,
        "documents": [{"id": d.id, "filename": d.filename, "chars": len(d.content), "created_at": d.created_at} for d in docs],
    }


@router.post("/kb/{kb_id}/docs")
async def upload_doc(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    user_id = _user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    raw = await file.read()
    filename = (file.filename or "document.txt").strip()

    if filename.lower().endswith(".pdf"):
        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(raw))
            text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"PDF read failed: {exc}")
    else:
        try:
            text = raw.decode("utf-8")
        except Exception:
            text = raw.decode("latin-1")

    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Document appears to be empty")

    doc = KBDocument(kb_id=kb_id, filename=filename, content=text)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "filename": doc.filename, "chars": len(text), "created_at": doc.created_at}


@router.delete("/kb/{kb_id}/docs/{doc_id}")
def delete_doc(
    kb_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    user_id = _user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    doc = db.query(KBDocument).filter(KBDocument.id == doc_id, KBDocument.kb_id == kb_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"status": "deleted"}


@router.delete("/kb/{kb_id}")
def delete_kb(
    kb_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    user_id = _user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    db.query(KBDocument).filter(KBDocument.kb_id == kb_id).delete()
    db.delete(kb)
    db.commit()
    return {"status": "deleted"}


@router.get("/public/{kb_id}")
def kb_public_info(kb_id: int, db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    doc_count = db.query(KBDocument).filter(KBDocument.kb_id == kb_id).count()
    return {"id": kb.id, "name": kb.name, "description": kb.description, "doc_count": doc_count}


@router.post("/chat/{kb_id}")
def chat(kb_id: int, req: ChatRequest, db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    docs = db.query(KBDocument).filter(KBDocument.kb_id == kb_id).all()
    if not docs:
        raise HTTPException(status_code=400, detail="This knowledge base has no documents yet.")

    chunks = retrieve(req.question, [{"content": d.content} for d in docs], top_k=3)
    context = "\n\n---\n\n".join(chunks) if chunks else "No relevant context found in the documents."

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a helpful AI assistant for '{kb.name}'. "
                "Answer questions based solely on the provided context. "
                "If the answer isn't in the context, say so politely and suggest the user contact support.\n\n"
                f"Context:\n{context}"
            ),
        }
    ]
    for h in req.history[-6:]:
        if h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": req.question})

    try:
        client = Groq(api_key=kb.groq_api_key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=512,
            temperature=0.3,
        )
        answer = resp.choices[0].message.content
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI error: {str(exc)}")

    return {"answer": answer, "sources_found": len(chunks)}
