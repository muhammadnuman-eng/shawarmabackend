from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailProvider(ABC):
    """Abstract base class for email providers"""

    @abstractmethod
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email to recipient"""
        pass

class SMTPEmailProvider(EmailProvider):
    """SMTP email provider implementation"""

    def __init__(self):
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Support both naming conventions
        self.smtp_server = (
            getattr(settings, 'SMTP_SERVER', None) or
            getattr(settings, 'EMAIL_HOST', None) or
            'smtp.gmail.com'
        )
        self.smtp_port = (
            getattr(settings, 'SMTP_PORT', None) or
            getattr(settings, 'EMAIL_PORT', None) or
            587
        )
        self.smtp_username = (
            getattr(settings, 'SMTP_USERNAME', None) or
            getattr(settings, 'EMAIL_USER', None)
        )
        self.smtp_password = (
            getattr(settings, 'SMTP_PASSWORD', None) or
            getattr(settings, 'EMAIL_PASS', None)
        )
        self.from_email = (
            getattr(settings, 'FROM_EMAIL', None) or
            getattr(settings, 'EMAIL_USER', None) or
            self.smtp_username
        )

        self.smtplib = smtplib
        self.MIMEText = MIMEText
        self.MIMEMultipart = MIMEMultipart

    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = self.MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add text content
            if text_content:
                text_part = self.MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML content
            html_part = self.MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            server = self.smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"SMTP email failed for {to_email}: {str(e)}")
            return False

class SendGridEmailProvider(EmailProvider):
    """SendGrid email provider implementation"""

    def __init__(self):
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, To, From, Content

            self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            self.Mail = Mail
            self.To = To
            self.From = From
            self.Content = Content
        except ImportError:
            logger.error("SendGrid not installed. Run: pip install sendgrid")
            raise ImportError("SendGrid package not installed")

    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email using SendGrid"""
        try:
            from_email = getattr(settings, 'FROM_EMAIL', 'noreply@shawarmastop.com')

            message = self.Mail(
                from_email=self.From(from_email),
                to_emails=self.To(to_email),
                subject=subject,
                html_content=self.Content("text/html", html_content)
            )

            if text_content:
                message.add_content(self.Content("text/plain", text_content))

            response = self.sg.send(message)

            if response.status_code == 202:
                logger.info(f"SendGrid email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"SendGrid email failed for {to_email}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"SendGrid email error for {to_email}: {str(e)}")
            return False

class MockEmailProvider(EmailProvider):
    """Mock email provider for development/testing"""

    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Mock email - just log the details"""
        logger.info(f"MOCK EMAIL to {to_email}")
        logger.info(f"Subject: {subject}")
        if text_content:
            logger.info(f"Text: {text_content[:100]}...")
        logger.info(f"HTML: {html_content[:100]}...")

        print(f"📧 MOCK EMAIL to {to_email}")
        print(f"Subject: {subject}")
        print(f"Content: {text_content or html_content[:100]}...")
        return True

class EmailService:
    """Email service manager"""

    def __init__(self):
        self.provider: Optional[EmailProvider] = None
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize email provider based on settings"""
        if not getattr(settings, 'EMAIL_ENABLED', False):
            logger.warning("Email is disabled. Using mock provider for development.")
            self.provider = MockEmailProvider()
            return

        provider = getattr(settings, 'EMAIL_PROVIDER', 'smtp').lower()

        if provider == "sendgrid":
            if not hasattr(settings, 'SENDGRID_API_KEY'):
                logger.error("SendGrid API key not configured. Using mock provider.")
                self.provider = MockEmailProvider()
            else:
                try:
                    self.provider = SendGridEmailProvider()
                    logger.info("SendGrid email provider initialized successfully")
                except ImportError:
                    logger.error("SendGrid package not installed. Using mock provider.")
                    self.provider = MockEmailProvider()
        elif provider == "smtp":
            # Check for user-provided credentials or standard SMTP config
            has_user_config = all([
                getattr(settings, 'EMAIL_HOST', None) or getattr(settings, 'SMTP_SERVER', None),
                getattr(settings, 'EMAIL_USER', None) or getattr(settings, 'SMTP_USERNAME', None),
                getattr(settings, 'EMAIL_PASS', None) or getattr(settings, 'SMTP_PASSWORD', None)
            ])

            if not has_user_config:
                logger.error("SMTP credentials not configured (EMAIL_HOST/EMAIL_USER/EMAIL_PASS or SMTP_*). Using mock provider.")
                self.provider = MockEmailProvider()
            else:
                try:
                    self.provider = SMTPEmailProvider()
                    logger.info(f"SMTP email provider initialized successfully for {getattr(settings, 'EMAIL_USER', getattr(settings, 'SMTP_USERNAME', 'unknown'))}")
                except Exception as e:
                    logger.error(f"SMTP initialization failed: {e}. Using mock provider.")
                    self.provider = MockEmailProvider()
        else:
            logger.warning(f"Unknown email provider: {provider}. Using mock provider.")
            self.provider = MockEmailProvider()

    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send custom email"""
        if not self.provider:
            logger.error("No email provider configured")
            return False

        return await self.provider.send_email(to_email, subject, html_content, text_content)

    async def send_password_reset_email(self, to_email: str, reset_token: str, reset_link: str) -> bool:
        """Send password reset email"""
        subject = "Shawarma Stop - Password Reset"

        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your Shawarma Stop account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_link}" style="background-color: #F94F33; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>Shawarma Stop Team</p>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request

        You requested a password reset for your Shawarma Stop account.

        Reset your password here: {reset_link}

        This link will expire in 1 hour.

        If you didn't request this, please ignore this email.

        Best regards,
        Shawarma Stop Team
        """

        return await self.send_email(to_email, subject, html_content, text_content)

    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to Shawarma Stop!"

        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Shawarma Stop, {user_name}!</h2>
            <p>Thank you for joining Shawarma Stop. We're excited to serve you the best shawarma in town!</p>
            <p>Start ordering your favorite shawarma now.</p>
            <br>
            <p>Best regards,<br>Shawarma Stop Team</p>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to Shawarma Stop, {user_name}!

        Thank you for joining Shawarma Stop. We're excited to serve you the best shawarma in town!

        Start ordering your favorite shawarma now.

        Best regards,
        Shawarma Stop Team
        """

        return await self.send_email(to_email, subject, html_content, text_content)

# Global email service instance
email_service = EmailService()
