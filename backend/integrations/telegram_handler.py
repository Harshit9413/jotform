from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict


def _format_message(form_title: str, form_data: Dict[str, Any]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"📋 <b>New Form Submission</b>",
        f"Form: {form_title}",
        f"Submitted At: {now}",
        "",
    ]
    for k, v in form_data.items():
        if str(k).startswith("_") or v in ("", None):
            continue
        lines.append(f"• {k}: {v}")
    return "\n".join(lines)


def run_telegram(config: Dict[str, Any], form_data: Dict[str, Any], form_title: str) -> Dict[str, Any]:
    try:
        import requests
    except ImportError:
        raise RuntimeError(
            "requests is not installed. Run: pip install requests"
        )

    bot_token = config.get("bot_token", "").strip()
    chat_id   = str(config.get("chat_id", "")).strip()

    if not bot_token:
        raise ValueError("bot_token is required")
    if not chat_id:
        raise ValueError("chat_id is required")

    url  = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    text = _format_message(form_title, form_data)

    resp = requests.post(
        url,
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        timeout=10,
    )
    body = resp.json()
    if not body.get("ok"):
        raise RuntimeError(body.get("description", "Telegram API error"))

    return {"sent": True, "chat_id": chat_id}
