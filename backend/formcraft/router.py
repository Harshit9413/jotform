from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import datetime
import json

from .models import Template, Submission, CustomForm
from .schemas import (
    TemplateOut, SubmissionCreate, SubmissionOut,
    CustomFormCreate, CustomFormOut,
)
from .database import SessionLocal
from auth.utils import decode_token

router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/public/{form_id}")
def get_public_form(form_id: str, db: Session = Depends(get_db)):
    if form_id.startswith("custom_"):
        try:
            cf_id = int(form_id.replace("custom_", ""))
        except ValueError:
            raise HTTPException(status_code=404, detail="Form not found")
        cf = db.query(CustomForm).filter(CustomForm.id == cf_id).first()
        if not cf:
            raise HTTPException(status_code=404, detail="Form not found")
        return {
            "id": form_id,
            "title": cf.title,
            "description": f"{len(cf.fields)} field{'s' if len(cf.fields) != 1 else ''}",
            "color": "#6c63ff",
            "fields": cf.fields,
        }
    t = db.query(Template).filter(Template.id == form_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Form not found")
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "color": t.color,
        "fields": t.fields,
    }


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
def create_submission(payload: SubmissionCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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

    # Email notification for custom form submissions
    if payload.form_id and payload.form_id.startswith("custom_"):
        try:
            form_id_int = int(payload.form_id.replace("custom_", ""))
            form = db.query(CustomForm).filter(CustomForm.id == form_id_int).first()
            if form and form.user_id:
                from auth.models import User
                from .email_notify import send_submission_notification
                user = db.query(User).filter(User.id == form.user_id).first()
                if user:
                    background_tasks.add_task(
                        send_submission_notification,
                        user.email,
                        payload.form_title,
                        payload.data if isinstance(payload.data, dict) else {},
                        sub.id,
                    )
        except Exception:
            pass  # never fail submission because of notification logic

    # Fire all active integrations (Google Sheets, Email) in background
    try:
        from integrations.engine import trigger_all_integrations
        background_tasks.add_task(
            trigger_all_integrations,
            submission_id=sub.id,
            form_id=payload.form_id,
            form_title=payload.form_title,
            data=payload.data if isinstance(payload.data, dict) else {},
        )
    except Exception:
        pass

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


@router.get("/settings/notifications")
def notification_settings():
    import os
    return {"email_enabled": bool(os.getenv("RESEND_API_KEY", ""))}


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
def save_custom_form(payload: CustomFormCreate, db: Session = Depends(get_db), authorization: Optional[str] = Header(default=None)):
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token_data = decode_token(authorization.split(" ")[1])
        if token_data:
            user_id = int(token_data.get("sub", 0)) or None
    form = CustomForm(
        title=payload.title,
        fields=payload.fields,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )
    db.add(form)
    db.commit()
    db.refresh(form)
    return form


@router.get("/forms", response_model=List[CustomFormOut])
def get_custom_forms(db: Session = Depends(get_db), authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        return []
    token_data = decode_token(authorization.split(" ")[1])
    if not token_data:
        return []
    user_id = int(token_data.get("sub", 0))
    return db.query(CustomForm).filter(CustomForm.user_id == user_id).order_by(CustomForm.created_at.desc()).all()


@router.get("/stats/user")
def user_stats(db: Session = Depends(get_db), authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"total_forms": 0, "total_submissions": 0, "recent_forms": []}
    token_data = decode_token(authorization.split(" ")[1])
    if not token_data:
        return {"total_forms": 0, "total_submissions": 0, "recent_forms": []}
    user_id = int(token_data.get("sub", 0))

    user_forms = db.query(CustomForm).filter(CustomForm.user_id == user_id).order_by(CustomForm.created_at.desc()).all()
    form_ids = [f"custom_{f.id}" for f in user_forms]

    sub_count = 0
    if form_ids:
        sub_count = db.query(Submission).filter(Submission.form_id.in_(form_ids)).count()

    recent = [
        {
            "id": f.id,
            "title": f.title,
            "created_at": f.created_at.isoformat(),
            "field_count": len(f.fields),
        }
        for f in user_forms[:5]
    ]

    return {
        "total_forms": len(user_forms),
        "total_submissions": sub_count,
        "recent_forms": recent,
    }


@router.get("/forms/{form_id}", response_model=CustomFormOut)
def get_custom_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(CustomForm).filter(CustomForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form


from pydantic import BaseModel as _BaseModel


class TranslateRequest(_BaseModel):
    title: str
    fields: List[Any]
    target_language: str
    groq_api_key: str


@router.post("/translate")
def translate_form(req: TranslateRequest):
    from groq import Groq

    extractable = {
        "title": req.title,
        "fields": [
            {
                "label": f.get("label", ""),
                "placeholder": f.get("placeholder", ""),
                "options": f.get("options", []),
            }
            for f in req.fields
        ],
    }

    prompt = (
        f"Translate the following JSON form data from English to {req.target_language}.\n"
        "Rules:\n"
        "- Translate ONLY text values (title, label, placeholder, option strings)\n"
        "- Do NOT change keys, field types, IDs, or booleans\n"
        "- Keep empty strings empty\n"
        "- Return ONLY valid JSON, no explanation\n\n"
        f"Input:\n{json.dumps(extractable, ensure_ascii=False, indent=2)}"
    )

    try:
        client = Groq(api_key=req.groq_api_key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.1,
        )
        raw = resp.choices[0].message.content.strip()
        # strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        translated = json.loads(raw.strip())
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"AI returned invalid JSON: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Translation error: {exc}")

    translated_fields = []
    for orig, tr in zip(req.fields, translated.get("fields", [])):
        merged = dict(orig)
        if tr.get("label"):
            merged["label"] = tr["label"]
        if tr.get("placeholder"):
            merged["placeholder"] = tr["placeholder"]
        if tr.get("options") and isinstance(tr["options"], list) and len(tr["options"]) == len(orig.get("options", [])):
            merged["options"] = tr["options"]
        translated_fields.append(merged)

    return {
        "title": translated.get("title", req.title),
        "fields": translated_fields,
    }
