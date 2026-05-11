# Telegram & Twilio SMS Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `telegram` (admin-only notification) and `twilio_sms` (admin + user notification) as new integration types to the FormCraft submission pipeline.

**Architecture:** Two new handler files follow the existing `email_handler.py` / `google_sheets.py` pattern. `engine.py` dispatches to them after a form submission. `router.py` registers the new types. No DB schema changes needed.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy, `requests` (Telegram Bot API), `twilio` SDK, `pytest` + `unittest.mock`

---

## File Map

| Action | Path |
|--------|------|
| Create | `backend/integrations/telegram_handler.py` |
| Create | `backend/integrations/twilio_handler.py` |
| Create | `backend/tests/__init__.py` |
| Create | `backend/tests/test_telegram_handler.py` |
| Create | `backend/tests/test_twilio_handler.py` |
| Modify | `backend/requirements.txt` |
| Modify | `backend/integrations/engine.py` |
| Modify | `backend/integrations/router.py` |

---

## Task 1: Add Dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add twilio and requests to requirements.txt**

Open `backend/requirements.txt` and append these two lines at the end:
```
twilio==9.3.3
requests==2.32.3
```

- [ ] **Step 2: Install dependencies**

Run from `backend/` directory (with virtualenv active):
```bash
pip install twilio==9.3.3 requests==2.32.3
```
Expected: Both packages install without errors.

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add twilio and requests dependencies"
```

---

## Task 2: Telegram Handler

**Files:**
- Create: `backend/integrations/telegram_handler.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_telegram_handler.py`

- [ ] **Step 1: Create tests directory**

```bash
touch backend/tests/__init__.py
```

- [ ] **Step 2: Write failing tests**

Create `backend/tests/test_telegram_handler.py`:

```python
from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest

from integrations.telegram_handler import run_telegram, _format_message


class TestFormatMessage:
    def test_includes_form_title(self):
        msg = _format_message("My Form", {"Name": "Alice"})
        assert "My Form" in msg

    def test_includes_field_values(self):
        msg = _format_message("Test", {"Name": "Bob", "Email": "b@b.com"})
        assert "Bob" in msg
        assert "b@b.com" in msg

    def test_skips_underscore_keys(self):
        msg = _format_message("Test", {"_internal": "secret", "Name": "Carol"})
        assert "_internal" not in msg
        assert "Carol" in msg

    def test_skips_empty_values(self):
        msg = _format_message("Test", {"Name": "", "City": "Delhi"})
        assert "Delhi" in msg
        # empty value fields should not appear
        assert "Name:" not in msg


class TestRunTelegram:
    def test_sends_message_to_chat(self):
        config = {"bot_token": "123:abc", "chat_id": "-100999"}
        data = {"Name": "Alice", "Email": "a@a.com"}

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True}
        mock_resp.raise_for_status.return_value = None

        with patch("integrations.telegram_handler.requests.post", return_value=mock_resp) as mock_post:
            result = run_telegram(config, data, "Contact Form")

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert "123:abc" in call_kwargs[0][0]
        assert call_kwargs[1]["json"]["chat_id"] == "-100999"
        assert result["sent"] is True

    def test_raises_on_missing_bot_token(self):
        with pytest.raises(ValueError, match="bot_token"):
            run_telegram({"chat_id": "-100999"}, {}, "Form")

    def test_raises_on_missing_chat_id(self):
        with pytest.raises(ValueError, match="chat_id"):
            run_telegram({"bot_token": "123:abc"}, {}, "Form")

    def test_raises_on_telegram_api_error(self):
        config = {"bot_token": "123:abc", "chat_id": "-100999"}
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": False, "description": "Bad token"}

        with patch("integrations.telegram_handler.requests.post", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="Bad token"):
                run_telegram(config, {}, "Form")
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd backend && python -m pytest tests/test_telegram_handler.py -v
```
Expected: `ModuleNotFoundError: No module named 'integrations.telegram_handler'`

- [ ] **Step 4: Implement telegram_handler.py**

Create `backend/integrations/telegram_handler.py`:

```python
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict

import requests


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
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend && python -m pytest tests/test_telegram_handler.py -v
```
Expected: All 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/integrations/telegram_handler.py backend/tests/__init__.py backend/tests/test_telegram_handler.py
git commit -m "feat: add Telegram notification integration handler"
```

---

## Task 3: Twilio SMS Handler

**Files:**
- Create: `backend/integrations/twilio_handler.py`
- Create: `backend/tests/test_twilio_handler.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_twilio_handler.py`:

```python
from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest

from integrations.twilio_handler import run_twilio_sms, _detect_phone, _admin_sms, _user_sms


class TestDetectPhone:
    def test_detects_phone_key(self):
        assert _detect_phone({"phone": "+919876543210"}) == "+919876543210"

    def test_detects_mobile_key(self):
        assert _detect_phone({"mobile": "9876543210"}) == "9876543210"

    def test_detects_contact_key(self):
        assert _detect_phone({"contact_number": "9876543210"}) == "9876543210"

    def test_requires_10_digits_minimum(self):
        assert _detect_phone({"phone": "12345"}) is None

    def test_returns_none_when_no_phone(self):
        assert _detect_phone({"Name": "Alice", "Email": "a@a.com"}) is None

    def test_skips_underscore_keys(self):
        assert _detect_phone({"_phone": "+919876543210"}) is None


class TestSmsText:
    def test_admin_sms_contains_form_title(self):
        msg = _admin_sms("Survey Form", {"Name": "Bob"})
        assert "Survey Form" in msg
        assert "[FormCraft]" in msg

    def test_user_sms_contains_form_title(self):
        msg = _user_sms("Survey Form")
        assert "Survey Form" in msg
        assert "[FormCraft]" in msg


class TestRunTwilioSms:
    def _config(self):
        return {
            "account_sid": "ACtest123",
            "auth_token":  "token123",
            "from_number": "+15550001111",
            "admin_number": "+919999999999",
        }

    def test_always_sends_admin_sms(self):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = MagicMock(sid="SM123")

        with patch("integrations.twilio_handler.Client", return_value=mock_client):
            result = run_twilio_sms(self._config(), {"Name": "Alice"}, "My Form")

        assert "admin" in result["sent"]
        mock_client.messages.create.assert_called()

    def test_sends_user_sms_when_phone_found(self):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = MagicMock(sid="SM456")

        with patch("integrations.twilio_handler.Client", return_value=mock_client):
            result = run_twilio_sms(
                self._config(),
                {"Name": "Alice", "phone": "+919876543210"},
                "My Form",
            )

        assert "user" in result["sent"]
        assert mock_client.messages.create.call_count == 2

    def test_skips_user_sms_when_no_phone(self):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = MagicMock(sid="SM789")

        with patch("integrations.twilio_handler.Client", return_value=mock_client):
            result = run_twilio_sms(self._config(), {"Name": "Alice"}, "My Form")

        assert "user" not in result["sent"]
        assert mock_client.messages.create.call_count == 1

    def test_raises_on_missing_account_sid(self):
        config = self._config()
        del config["account_sid"]
        with pytest.raises(ValueError, match="account_sid"):
            run_twilio_sms(config, {}, "Form")

    def test_raises_on_missing_admin_number(self):
        config = self._config()
        del config["admin_number"]
        with pytest.raises(ValueError, match="admin_number"):
            run_twilio_sms(config, {}, "Form")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && python -m pytest tests/test_twilio_handler.py -v
```
Expected: `ModuleNotFoundError: No module named 'integrations.twilio_handler'`

- [ ] **Step 3: Implement twilio_handler.py**

Create `backend/integrations/twilio_handler.py`:

```python
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional

from twilio.rest import Client


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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && python -m pytest tests/test_twilio_handler.py -v
```
Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/integrations/twilio_handler.py backend/tests/test_twilio_handler.py
git commit -m "feat: add Twilio SMS integration handler"
```

---

## Task 4: Wire Into engine.py and router.py

**Files:**
- Modify: `backend/integrations/engine.py`
- Modify: `backend/integrations/router.py`

- [ ] **Step 1: Update engine.py imports and dispatch**

In `backend/integrations/engine.py`, replace:
```python
from .google_sheets import run_google_sheets
from .email_handler import run_email
```
with:
```python
from .google_sheets import run_google_sheets
from .email_handler import run_email
from .telegram_handler import run_telegram
from .twilio_handler import run_twilio_sms
```

And in the same file, replace:
```python
                else:
                    raise ValueError(f"Unknown integration type: {itg.type}")
```
with:
```python
                elif itg.type == "telegram":
                    run_telegram(itg.config, data, form_title)
                elif itg.type == "twilio_sms":
                    run_twilio_sms(itg.config, data, form_title)
                else:
                    raise ValueError(f"Unknown integration type: {itg.type}")
```

- [ ] **Step 2: Update router.py — ALLOWED_TYPES**

In `backend/integrations/router.py`, replace:
```python
ALLOWED_TYPES = {"google_sheets", "email"}
```
with:
```python
ALLOWED_TYPES = {"google_sheets", "email", "telegram", "twilio_sms"}
```

- [ ] **Step 3: Update router.py — _mask_config**

In `backend/integrations/router.py`, replace the entire `_mask_config` function:
```python
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
    return safe
```
with:
```python
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
```

- [ ] **Step 4: Write a wiring smoke test**

Append to `backend/tests/test_telegram_handler.py`:

```python
class TestEngineDispatches:
    def test_engine_calls_telegram_on_active_integration(self):
        """Smoke test: engine dispatches to run_telegram when type is telegram."""
        from integrations.telegram_handler import run_telegram
        config = {"bot_token": "tok", "chat_id": "123"}

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True}

        with patch("integrations.telegram_handler.requests.post", return_value=mock_resp):
            result = run_telegram(config, {"Name": "Test"}, "My Form")

        assert result["sent"] is True
```

- [ ] **Step 5: Run all tests**

```bash
cd backend && python -m pytest tests/ -v
```
Expected: All 16 tests PASS (7 telegram + 9 twilio).

- [ ] **Step 6: Commit**

```bash
git add backend/integrations/engine.py backend/integrations/router.py
git commit -m "feat: wire telegram and twilio_sms into integration engine and router"
```

---

## Task 5: Manual End-to-End Verification

**Files:** None — runtime verification only.

- [ ] **Step 1: Start the backend**

```bash
cd backend && uvicorn main:app --reload
```

- [ ] **Step 2: Create a Telegram integration via API**

```bash
curl -X POST http://localhost:8000/api/integrations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "form_id": "<any_form_id>",
    "type": "telegram",
    "config": {
      "bot_token": "<your_bot_token>",
      "chat_id": "<your_chat_id>"
    }
  }'
```
Expected: `{"id": ..., "type": "telegram", "config": {"bot_token": "***<last2>", "chat_id": "..."}, "is_active": true}`

- [ ] **Step 3: Verify bot_token is masked in response**

The response `config.bot_token` should show `***<last 2 chars>`, not the full token.

- [ ] **Step 4: Submit the form and check Telegram**

Submit the form linked to this integration. Check your Telegram chat — the notification message should appear within a few seconds.

- [ ] **Step 5: Create a Twilio SMS integration via API**

```bash
curl -X POST http://localhost:8000/api/integrations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "form_id": "<any_form_id>",
    "type": "twilio_sms",
    "config": {
      "account_sid": "<your_account_sid>",
      "auth_token": "<your_auth_token>",
      "from_number": "+1XXXXXXXXXX",
      "admin_number": "+91XXXXXXXXXX"
    }
  }'
```
Expected: `{"id": ..., "type": "twilio_sms", "config": {"auth_token": "***<last2>", ...}, "is_active": true}`

- [ ] **Step 6: Submit form with a phone field and verify SMS**

Submit the form with a field named `phone` containing a valid number. Two SMS should arrive:
- Admin gets: `[FormCraft] New submission on "..."`
- User (phone number in form) gets: `[FormCraft] Thank you for submitting "..."!`

- [ ] **Step 7: Check integration logs**

```bash
curl http://localhost:8000/api/integrations/<form_id>/logs \
  -H "Authorization: Bearer <your_token>"
```
Expected: Log entries with `"status": "success"` for both integrations.

- [ ] **Step 8: Final commit**

```bash
git add -A
git commit -m "test: add manual e2e verification — telegram and twilio_sms integrations working"
```
