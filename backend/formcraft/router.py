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
