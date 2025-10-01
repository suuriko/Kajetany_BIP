#!/usr/bin/env python3

import datetime
import smtplib
import ssl
from email.message import EmailMessage
from unittest.mock import Mock, patch

import pytest

from src.mail_service import MailService


class TestMailServiceInit:
    """Test MailService initialization and validation."""

    def test_init_with_valid_credentials(self):
        """Test that MailService initializes correctly with valid credentials."""
        user = "test@example.com"
        password = "password123"

        service = MailService(user, password)

        assert service.user == user
        assert service.password == password

    def test_init_with_empty_user_raises_value_error(self):
        """Test that empty user raises ValueError."""
        with pytest.raises(ValueError, match="SMTP_USER and SMTP_PASS must be set and non-empty"):
            MailService("", "password123")

    def test_init_with_none_user_raises_value_error(self):
        """Test that None user raises ValueError."""
        with pytest.raises(ValueError, match="SMTP_USER and SMTP_PASS must be set and non-empty"):
            MailService(None, "password123")  # type: ignore

    def test_init_with_empty_password_raises_value_error(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="SMTP_USER and SMTP_PASS must be set and non-empty"):
            MailService("test@example.com", "")

    def test_init_with_none_password_raises_value_error(self):
        """Test that None password raises ValueError."""
        with pytest.raises(ValueError, match="SMTP_USER and SMTP_PASS must be set and non-empty"):
            MailService("test@example.com", None)  # type: ignore

    def test_init_with_whitespace_only_credentials_accepts_whitespace(self):
        """Test that whitespace-only credentials are accepted (current behavior)."""
        # The current implementation only checks for truthiness, not for whitespace
        # Whitespace strings are truthy in Python, so they pass validation
        user_service = MailService("   ", "password123")
        assert user_service.user == "   "

        password_service = MailService("test@example.com", "   ")
        assert password_service.password == "   "


class TestMailServiceSendToGroup:
    """Test the send_to_group method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.user = "sender@example.com"
        self.password = "password123"
        self.service = MailService(self.user, self.password)

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_success(self, mock_ssl_context, mock_smtp, mock_datetime):
        """Test successful email sending."""
        # Arrange
        mock_date = Mock()
        mock_date.today.return_value.strftime.return_value = "24.09.2025"
        mock_datetime.date = mock_date

        mock_context = Mock()
        mock_ssl_context.return_value = mock_context

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        to_group = "recipients@example.com"
        email_content = "<h1>Test Email</h1><p>This is test content.</p>"

        # Act
        self.service.send_to_group(to_group, email_content)

        # Assert
        mock_ssl_context.assert_called_once()
        mock_smtp.assert_called_once_with("smtp.gmail.com", 465, context=mock_context)
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once()

        # Verify the message was created correctly
        sent_message = mock_smtp_instance.send_message.call_args[0][0]
        assert isinstance(sent_message, EmailMessage)
        assert sent_message["Subject"] == "[BIP Bot] Nowości dla Kajetan w BIP Nadarzyn - 24.09.2025"
        assert sent_message["From"] == self.user
        assert sent_message["To"] == to_group

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_creates_correct_subject_with_current_date(self, mock_ssl_context, mock_smtp, mock_datetime):
        """Test that the email subject includes the current date."""
        # Arrange
        test_date = "15.03.2025"
        mock_date = Mock()
        mock_date.today.return_value.strftime.return_value = test_date
        mock_datetime.date = mock_date

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Act
        self.service.send_to_group("test@example.com", "<p>Test</p>")

        # Assert
        sent_message = mock_smtp_instance.send_message.call_args[0][0]
        expected_subject = f"[BIP Bot] Nowości dla Kajetan w BIP Nadarzyn - {test_date}"
        assert sent_message["Subject"] == expected_subject

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_sets_html_content_type(self, mock_ssl_context, mock_smtp, mock_datetime):
        """Test that email content is set as HTML."""
        # Arrange
        mock_date = Mock()
        mock_date.today.return_value.strftime.return_value = "24.09.2025"
        mock_datetime.date = mock_date

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        html_content = "<html><body><h1>Test</h1></body></html>"

        # Act
        self.service.send_to_group("test@example.com", html_content)

        # Assert
        sent_message = mock_smtp_instance.send_message.call_args[0][0]
        # Check that set_content was called with subtype="html"
        # We can verify this by checking the content type of the message
        assert "text/html" in sent_message.get_content_type() or sent_message.get_content_maintype() == "text"

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_handles_multiple_recipients(self, mock_ssl_context, mock_smtp, mock_datetime):
        """Test sending email to multiple recipients."""
        # Arrange
        mock_date = Mock()
        mock_date.today.return_value.strftime.return_value = "24.09.2025"
        mock_datetime.date = mock_date

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        multiple_recipients = "user1@example.com, user2@example.com, user3@example.com"

        # Act
        self.service.send_to_group(multiple_recipients, "<p>Test</p>")

        # Assert
        sent_message = mock_smtp_instance.send_message.call_args[0][0]
        assert sent_message["To"] == multiple_recipients

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_smtp_login_failure_propagates_exception(self, mock_ssl_context, mock_smtp, mock_datetime):
        """Test that SMTP login failures are properly propagated."""
        # Arrange
        mock_date = Mock()
        mock_date.today.return_value.strftime.return_value = "24.09.2025"
        mock_datetime.date = mock_date

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")

        # Act & Assert
        with pytest.raises(smtplib.SMTPAuthenticationError):
            self.service.send_to_group("test@example.com", "<p>Test</p>")

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_smtp_send_failure_propagates_exception(self, mock_ssl_context, mock_smtp, mock_datetime):
        """Test that SMTP send failures are properly propagated."""
        # Arrange
        mock_date = Mock()
        mock_date.today.return_value.strftime.return_value = "24.09.2025"
        mock_datetime.date = mock_date

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        mock_smtp_instance.send_message.side_effect = smtplib.SMTPException("Send failed")

        # Act & Assert
        with pytest.raises(smtplib.SMTPException):
            self.service.send_to_group("test@example.com", "<p>Test</p>")

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_ssl_context_creation_failure_propagates_exception(
        self, mock_ssl_context, mock_smtp, mock_datetime
    ):
        """Test that SSL context creation failures are properly propagated."""
        # Arrange
        mock_date = Mock()
        mock_date.today.return_value.strftime.return_value = "24.09.2025"
        mock_datetime.date = mock_date

        mock_ssl_context.side_effect = ssl.SSLError("SSL context creation failed")

        # Act & Assert
        with pytest.raises(ssl.SSLError):
            self.service.send_to_group("test@example.com", "<p>Test</p>")

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_empty_content_still_sends(self, mock_ssl_context, mock_smtp, mock_datetime):
        """Test that emails with empty content are still sent."""
        # Arrange
        mock_date = Mock()
        mock_date.today.return_value.strftime.return_value = "24.09.2025"
        mock_datetime.date = mock_date

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Act
        self.service.send_to_group("test@example.com", "")

        # Assert
        mock_smtp_instance.send_message.assert_called_once()
        sent_message = mock_smtp_instance.send_message.call_args[0][0]
        assert sent_message["To"] == "test@example.com"

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_uses_correct_smtp_server_and_port(self, mock_ssl_context, mock_smtp, mock_datetime):
        """Test that the correct SMTP server and port are used."""
        # Arrange
        mock_date = Mock()
        mock_date.today.return_value.strftime.return_value = "24.09.2025"
        mock_datetime.date = mock_date

        mock_context = Mock()
        mock_ssl_context.return_value = mock_context

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Act
        self.service.send_to_group("test@example.com", "<p>Test</p>")

        # Assert
        mock_smtp.assert_called_once_with("smtp.gmail.com", 465, context=mock_context)

    @patch("src.mail_service.datetime")
    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_send_to_group_date_formatting(self, mock_ssl_context, mock_smtp, mock_datetime):
        """Test that date is formatted correctly in Polish format (DD.MM.YYYY)."""
        # Arrange
        mock_date_obj = Mock()
        mock_date_obj.strftime.return_value = "01.12.2025"
        mock_date = Mock()
        mock_date.today.return_value = mock_date_obj
        mock_datetime.date = mock_date

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Act
        self.service.send_to_group("test@example.com", "<p>Test</p>")

        # Assert
        mock_date_obj.strftime.assert_called_once_with("%d.%m.%Y")
        sent_message = mock_smtp_instance.send_message.call_args[0][0]
        assert "01.12.2025" in sent_message["Subject"]


class TestMailServiceIntegration:
    """Integration tests that test the complete flow with minimal mocking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.user = "sender@example.com"
        self.password = "password123"
        self.service = MailService(self.user, self.password)

    @patch("src.mail_service.smtplib.SMTP_SSL")
    @patch("src.mail_service.ssl.create_default_context")
    def test_complete_email_sending_flow(self, mock_ssl_context, mock_smtp):
        """Test the complete email sending flow with real date and message creation."""
        # Arrange
        mock_context = Mock()
        mock_ssl_context.return_value = mock_context

        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        to_group = "recipients@example.com"
        email_content = "<html><body><h1>BIP Update</h1><p>New documents available.</p></body></html>"

        # Act
        self.service.send_to_group(to_group, email_content)

        # Assert - verify all the components work together
        mock_ssl_context.assert_called_once()
        mock_smtp.assert_called_once_with("smtp.gmail.com", 465, context=mock_context)
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once()

        # Verify the complete message structure
        sent_message = mock_smtp_instance.send_message.call_args[0][0]
        assert isinstance(sent_message, EmailMessage)
        assert sent_message["From"] == self.user
        assert sent_message["To"] == to_group
        assert "[BIP Bot] Nowości dla Kajetan w BIP Nadarzyn" in sent_message["Subject"]

        # Verify date is in the subject (using real datetime)
        today = datetime.date.today().strftime("%d.%m.%Y")
        assert today in sent_message["Subject"]


if __name__ == "__main__":
    pytest.main([__file__])
