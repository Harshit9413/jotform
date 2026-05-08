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
        return 'Cannot reach the database host. Verify the hostname and port are accessible from your network.'
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
