from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Text, ForeignKey
from datetime import datetime
from formcraft.database import Base


class Integration(Base):
    __tablename__ = "integrations"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    form_id      = Column(String, nullable=False, index=True)
    type         = Column(String, nullable=False)   # google_sheets | email
    config       = Column(JSON, nullable=False, default=dict)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)


class IntegrationLog(Base):
    __tablename__ = "integration_logs"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    integration_id = Column(Integer, ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False, index=True)
    submission_id  = Column(Integer, nullable=False)
    status         = Column(String, nullable=False)   # success | failed
    error_message  = Column(Text, nullable=True)
    triggered_at   = Column(DateTime, default=datetime.utcnow)
