from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from formcraft.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), default="")
    groq_api_key = Column(String(300), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class KBDocument(Base):
    __tablename__ = "kb_documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    filename = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
