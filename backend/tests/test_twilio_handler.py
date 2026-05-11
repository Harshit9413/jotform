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
