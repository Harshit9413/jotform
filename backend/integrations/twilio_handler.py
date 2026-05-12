from __future__ import annotations
import re
from typing import Any, Dict, List, Optional


_PHONE_KEYWORDS = {"phone", "mobile", "contact", "number"}


def _detect_phone(form_data: Dict[str, Any]) -> Optional[str]:
    for k, v in form_data.items():
        if str(k).startswith("_"):
            continue
        key_lower = str(k).lower()
        if any(kw in key_lower for kw in _PHONE_KEYWORDS):
            digits = re.sub(r"\D", "", str(v))
            if len(digits) >= 10:
                return str(v).strip()
    return None


def _admin_sms(form_title: str, form_data: Dict[str, Any]) -> str:
    parts = []
    for k, v in form_data.items():
        if str(k).startswith("_") or v in ("", None):
            continue
        parts.append(f"{k}: {v}")
        if len(parts) == 2:
            break
    summary = ", ".join(parts)
    return f'[FormCraft] New submission on "{form_title}"\n{summary}\nView dashboard for full details.'


def _user_sms(form_title: str) -> str:
    return (
        f'[FormCraft] Thank you for submitting "{form_title}"!\n'
        "We received your response and will get back to you soon."
    )


def run_twilio_sms(config: Dict[str, Any], form_data: Dict[str, Any], form_title: str) -> Dict[str, Any]:
    try:
        from twilio.rest import Client
    except ImportError:
        raise RuntimeError(
            "twilio is not installed. Run: pip install twilio"
        )

    account_sid  = config.get("account_sid", "").strip()
    auth_token   = config.get("auth_token", "").strip()
    from_number  = config.get("from_number", "").strip()
    admin_number = config.get("admin_number", "").strip()

    if not account_sid:
        raise ValueError("account_sid is required")
    if not auth_token:
        raise ValueError("auth_token is required")
    if not from_number:
        raise ValueError("from_number is required")
    if not admin_number:
        raise ValueError("admin_number is required")

    client: Client = Client(account_sid, auth_token)
    sent: List[str] = []

    client.messages.create(
        body=_admin_sms(form_title, form_data),
        from_=from_number,
        to=admin_number,
    )
    sent.append("admin")

    user_phone = _detect_phone(form_data)
    if user_phone and user_phone != admin_number:
        client.messages.create(
            body=_user_sms(form_title),
            from_=from_number,
            to=user_phone,
        )
        sent.append("user")

    return {"sent": sent}
