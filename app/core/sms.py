from abc import ABC, abstractmethod
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SMSProvider(ABC):
    """Abstract base class for SMS providers"""

    @abstractmethod
    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS message to phone number"""
        pass

class TwilioSMSProvider(SMSProvider):
    """Twilio SMS provider implementation"""

    def __init__(self):
        try:
            from twilio.rest import Client
            from twilio.base.exceptions import TwilioException

            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.from_number = settings.TWILIO_PHONE_NUMBER
            self.twilio_exception = TwilioException
        except ImportError:
            logger.error("Twilio not installed. Run: pip install twilio")
            raise ImportError("Twilio package not installed")

    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS using Twilio"""
        try:
            # Send SMS
            message_response = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number
            )

            logger.info(f"SMS sent successfully to {phone_number}. SID: {message_response.sid}")
            return True

        except self.twilio_exception as e:
            logger.error(f"Twilio SMS failed for {phone_number}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected SMS error for {phone_number}: {str(e)}")
            return False

class MockSMSProvider(SMSProvider):
    """Mock SMS provider for development/testing"""

    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Mock SMS - just log the message"""
        logger.info(f"MOCK SMS to {phone_number}: {message}")
        print(f"📱 MOCK SMS to {phone_number}: {message}")
        return True

class SMSService:
    """SMS service manager"""

    def __init__(self):
        self.provider: Optional[SMSProvider] = None
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize SMS provider based on settings"""
        if not settings.SMS_ENABLED:
            logger.warning("SMS is disabled. Using mock provider for development.")
            self.provider = MockSMSProvider()
            return

        if settings.SMS_PROVIDER.lower() == "twilio":
            if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
                logger.error("Twilio credentials not configured. Using mock provider.")
                self.provider = MockSMSProvider()
            else:
                try:
                    self.provider = TwilioSMSProvider()
                    logger.info("Twilio SMS provider initialized successfully")
                except ImportError:
                    logger.error("Twilio package not installed. Using mock provider.")
                    self.provider = MockSMSProvider()
        else:
            logger.warning(f"Unknown SMS provider: {settings.SMS_PROVIDER}. Using mock provider.")
            self.provider = MockSMSProvider()

    async def send_otp(self, phone_number: str, otp_code: str) -> bool:
        """Send OTP via SMS"""
        message = f"Your Shawarma Stop verification code is: {otp_code}. Valid for 10 minutes."
        return await self.send_sms(phone_number, message)

    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send custom SMS message"""
        if not self.provider:
            logger.error("No SMS provider configured")
            return False

        return await self.provider.send_sms(phone_number, message)

# Global SMS service instance
sms_service = SMSService()
