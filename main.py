from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import models, schemas, database

app = FastAPI(title="FormCraft API", version="1.0.0")

# CORS — allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production mein apna domain daalo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB tables create karo on startup
models.Base.metadata.create_all(bind=database.engine)


# ─── DB Dependency ────────────────────────────────────────────
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── HEALTH CHECK ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "FormCraft API is running"}


# ─── TEMPLATES ────────────────────────────────────────────────
@app.get("/api/templates", response_model=List[schemas.TemplateOut])
def get_templates(db: Session = Depends(get_db)):
    return db.query(models.Template).all()


@app.get("/api/templates/{template_id}", response_model=schemas.TemplateOut)
def get_template(template_id: str, db: Session = Depends(get_db)):
    t = db.query(models.Template).filter(models.Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return t


# ─── SUBMISSIONS ──────────────────────────────────────────────
@app.post("/api/submissions", response_model=schemas.SubmissionOut)
def create_submission(payload: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    sub = models.Submission(
        form_id=payload.form_id,
        form_title=payload.form_title,
        data=payload.data,
        submitted_at=datetime.utcnow(),
        status="new"
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@app.get("/api/submissions", response_model=List[schemas.SubmissionOut])
def get_submissions(
    status: Optional[str] = None,
    form_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.Submission)
    if status:
        q = q.filter(models.Submission.status == status)
    if form_id:
        q = q.filter(models.Submission.form_id == form_id)
    return q.order_by(models.Submission.submitted_at.desc()).all()


@app.get("/api/submissions/{sub_id}", response_model=schemas.SubmissionOut)
def get_submission(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    return sub


@app.patch("/api/submissions/{sub_id}/read")
def mark_read(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    sub.status = "read"
    db.commit()
    return {"message": "Marked as read"}


@app.delete("/api/submissions/{sub_id}")
def delete_submission(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    db.delete(sub)
    db.commit()
    return {"message": "Deleted"}


@app.delete("/api/submissions")
def delete_all_submissions(db: Session = Depends(get_db)):
    db.query(models.Submission).delete()
    db.commit()
    return {"message": "All submissions deleted"}


# ─── STATS ────────────────────────────────────────────────────
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Submission).count()
    new_count = db.query(models.Submission).filter(models.Submission.status == "new").count()
    today = datetime.utcnow().date()
    today_count = db.query(models.Submission).filter(
        models.Submission.submitted_at >= datetime(today.year, today.month, today.day)
    ).count()
    return {
        "total": total,
        "new": new_count,
        "today": today_count,
        "completion_rate": "87%"
    }


# ─── CUSTOM FORMS (Builder) ───────────────────────────────────
@app.post("/api/forms", response_model=schemas.CustomFormOut)
def save_custom_form(payload: schemas.CustomFormCreate, db: Session = Depends(get_db)):
    form = models.CustomForm(
        title=payload.title,
        fields=payload.fields,
        created_at=datetime.utcnow()
    )
    db.add(form)
    db.commit()
    db.refresh(form)
    return form


@app.get("/api/forms", response_model=List[schemas.CustomFormOut])
def get_custom_forms(db: Session = Depends(get_db)):
    return db.query(models.CustomForm).order_by(models.CustomForm.created_at.desc()).all()


@app.get("/api/forms/{form_id}", response_model=schemas.CustomFormOut)
def get_custom_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(models.CustomForm).filter(models.CustomForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form