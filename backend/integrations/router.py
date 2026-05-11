from __future__ import annotations
import copy
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from formcraft.database import SessionLocal
from auth.utils import decode_token
from .models import Integration, IntegrationLog
from .schemas import IntegrationOut, IntegrationLogOut

router = APIRouter(prefix="/api/integrations")

ALLOWED_TYPES = {"google_sheets", "email", "telegram", "twilio_sms"}


# ── DB dependency ─────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Auth helper ───────────────────────────────────────────────────────────────
def _require_user(authorization: Optional[str]) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    data = decode_token(authorization.split(" ", 1)[1])
    if not data:
        raise HTTPException(status_code=401, detail="Invalid token")
    uid = int(data.get("sub", 0))
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    return uid


# ── Mask sensitive fields before returning to client ─────────────────────────
def _mask_config(type_: str, config: Dict[str, Any]) -> Dict[str, Any]:
    safe = copy.deepcopy(config)
    if type_ == "google_sheets" and "service_account_json" in safe:
        sa = safe["service_account_json"]
        if isinstance(sa, dict):
            safe["service_account_json"] = {
                "client_email": sa.get("client_email", ""),
                "project_id":   sa.get("project_id", ""),
                "_masked":      True,
            }
        else:
            safe["service_account_json"] = {"_masked": True}
    if type_ == "email" and "password" in safe:
        pw = str(safe["password"])
        safe["password"] = "***" + pw[-2:] if len(pw) > 2 else "****"
    if type_ == "telegram" and "bot_token" in safe:
        tok = str(safe["bot_token"])
        safe["bot_token"] = "***" + tok[-2:] if len(tok) > 2 else "****"
    if type_ == "twilio_sms" and "auth_token" in safe:
        tok = str(safe["auth_token"])
        safe["auth_token"] = "***" + tok[-2:] if len(tok) > 2 else "****"
    return safe


def _out(itg: Integration) -> Dict[str, Any]:
    return {
        "id":         itg.id,
        "form_id":    itg.form_id,
        "type":       itg.type,
        "config":     _mask_config(itg.type, itg.config or {}),
        "is_active":  itg.is_active,
        "created_at": itg.created_at,
    }


# ── Schemas ───────────────────────────────────────────────────────────────────
class CreateIntegrationReq(BaseModel):
    form_id: str
    type: str
    config: Dict[str, Any]


class UpdateConfigReq(BaseModel):
    config: Dict[str, Any]


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("")
def create_integration(
    req: CreateIntegrationReq,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    _require_user(authorization)
    if req.type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"type must be one of {ALLOWED_TYPES}")

    # Parse JSON string if client sent it as a string (service account upload)
    config = req.config
    if "service_account_json" in config and isinstance(config["service_account_json"], str):
        raw = config["service_account_json"].strip()
        parsed = None
        # Try direct parse first
        try:
            parsed = json.loads(raw)
        except Exception:
            pass
        # Fallback: fix actual newlines only inside the private_key value (common copy-paste issue).
        # We deliberately avoid replacing structural newlines because that corrupts the JSON.
        if parsed is None:
            try:
                import re
                def _fix_pk(m):
                    return m.group(1) + m.group(2).replace('\r', '').replace('\n', '\\n') + m.group(3)
                fixed = re.sub(r'("private_key"\s*:\s*")(.*?)(")', _fix_pk, raw, flags=re.DOTALL)
                parsed = json.loads(fixed)
            except Exception:
                pass
        if parsed is None:
            raise HTTPException(status_code=400, detail="service_account_json is not valid JSON. Paste the entire contents of your service-account.json file.")
        config["service_account_json"] = parsed

    itg = Integration(form_id=req.form_id, type=req.type, config=config, is_active=True)
    db.add(itg)
    db.commit()
    db.refresh(itg)
    return _out(itg)


@router.get("/{form_id}")
def list_integrations(
    form_id: str,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    _require_user(authorization)
    itgs = db.query(Integration).filter(Integration.form_id == form_id).order_by(Integration.id).all()
    return [_out(i) for i in itgs]


@router.patch("/{integration_id}/toggle")
def toggle_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    _require_user(authorization)
    itg = db.query(Integration).filter(Integration.id == integration_id).first()
    if not itg:
        raise HTTPException(status_code=404, detail="Integration not found")
    itg.is_active = not itg.is_active
    db.commit()
    return _out(itg)


@router.delete("/{integration_id}")
def delete_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    _require_user(authorization)
    itg = db.query(Integration).filter(Integration.id == integration_id).first()
    if not itg:
        raise HTTPException(status_code=404, detail="Integration not found")
    db.query(IntegrationLog).filter(IntegrationLog.integration_id == integration_id).delete()
    db.delete(itg)
    db.commit()
    return {"status": "deleted"}


@router.get("/{form_id}/logs")
def get_logs(
    form_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    _require_user(authorization)
    itg_ids = [
        row.id
        for row in db.query(Integration.id).filter(Integration.form_id == form_id).all()
    ]
    if not itg_ids:
        return []
    logs = (
        db.query(IntegrationLog)
        .filter(IntegrationLog.integration_id.in_(itg_ids))
        .order_by(IntegrationLog.triggered_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id":             lg.id,
            "integration_id": lg.integration_id,
            "submission_id":  lg.submission_id,
            "status":         lg.status,
            "error_message":  lg.error_message,
            "triggered_at":   lg.triggered_at,
        }
        for lg in logs
    ]
