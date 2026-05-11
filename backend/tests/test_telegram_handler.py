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


class TestEngineDispatches:
    def test_engine_calls_telegram_on_active_integration(self):
        from integrations.telegram_handler import run_telegram
        config = {"bot_token": "tok", "chat_id": "123"}

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True}

        with patch("integrations.telegram_handler.requests.post", return_value=mock_resp):
            result = run_telegram(config, {"Name": "Test"}, "My Form")

        assert result["sent"] is True
