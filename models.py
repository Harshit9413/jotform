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
    status       = Column(String, default="new")   # new | read
    submitted_at = Column(DateTime, default=datetime.utcnow)


class CustomForm(Base):
    __tablename__ = "custom_forms"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title      = Column(String, nullable=False)
    fields     = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)