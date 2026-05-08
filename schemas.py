from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


# ─── TEMPLATE ─────────────────────────────────────────────────
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


# ─── SUBMISSION ───────────────────────────────────────────────
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


# ─── CUSTOM FORM ──────────────────────────────────────────────
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