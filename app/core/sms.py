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

    async def send_whatsapp(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp message using Twilio Sandbox"""
        try:
            # WhatsApp sandbox number
            whatsapp_from = 'whatsapp:+14155238886'

            # Format phone number for WhatsApp
            whatsapp_to = f'whatsapp:{phone_number}'

            message_response = self.client.messages.create(
                body=message,
                from_=whatsapp_from,
                to=whatsapp_to
            )

            logger.info(f"WhatsApp sent successfully to {phone_number}. SID: {message_response.sid}")
            return True

        except self.twilio_exception as e:
            logger.error(f"Twilio WhatsApp failed for {phone_number}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected WhatsApp error for {phone_number}: {str(e)}")
            return False

class MockSMSProvider(SMSProvider):
    """Mock SMS provider for development/testing"""

    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Mock SMS - just log the message"""
        print("=" * 60)
        print("MOCK SMS PROVIDER - DEVELOPMENT MODE")
        print("=" * 60)
        print(f"To: {phone_number}")
        print(f"Message: {message}")
        print("")
        print("✅ SMS sent successfully (mock mode)")
        print("📝 Use the OTP code shown above to complete registration")
        print("=" * 60)
        return True

class ConsoleSMSProvider(SMSProvider):
    """Console SMS provider that shows OTP clearly for testing"""

    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Console SMS - shows OTP in clear format for testing"""
        print("=" * 80)
        print("📱 SHAWARMA STOP - OTP VERIFICATION")
        print("=" * 80)
        print(f"📞 Phone Number: {phone_number}")
        print(f"💬 Message: {message}")
        print("")
        print("✅ OTP sent to console (development mode)")
        print("🔄 Copy the verification code above to complete registration")
        print("=" * 80)
        return True

class SMSService:
    """SMS service manager"""

    def __init__(self):
        self.provider: Optional[SMSProvider] = None
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize SMS provider based on settings"""
        print("Initializing SMS Service...")
        print(f"   SMS_ENABLED: {settings.SMS_ENABLED}")
        print(f"   SMS_PROVIDER: {settings.SMS_PROVIDER}")

        if not settings.SMS_ENABLED:
            print("   INFO: SMS is disabled. Using console provider for development.")
            self.provider = ConsoleSMSProvider()
            return

        if settings.SMS_PROVIDER.lower() == "twilio":
            if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
                print("   INFO: Twilio credentials not configured. Using console provider for development.")
                print("   SETUP: To enable real SMS:")
                print("      1. Sign up for Twilio account at https://www.twilio.com")
                print("      2. Get your Account SID, Auth Token, and phone number")
                print("      3. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in .env")
                print("      4. Install twilio package: pip install twilio")
                print("")
                self.provider = ConsoleSMSProvider()
            else:
                try:
                    self.provider = TwilioSMSProvider()
                    print("   SUCCESS: Twilio SMS provider initialized")
                    print(f"      From: {settings.TWILIO_PHONE_NUMBER}")
                except ImportError:
                    print("   WARNING: Twilio package not installed. Using console provider.")
                    print("      Install with: pip install twilio")
                    self.provider = ConsoleSMSProvider()
                except Exception as e:
                    print(f"   ERROR: Twilio initialization failed: {e}")
                    print("      Using console provider as fallback.")
                    self.provider = ConsoleSMSProvider()
        else:
            print(f"   WARNING: Unknown SMS provider: {settings.SMS_PROVIDER}. Using console provider.")
            self.provider = ConsoleSMSProvider()

        print(f"   Final provider: {type(self.provider).__name__}")
        print("=" * 70)

    async def send_otp(self, phone_number: str, otp_code: str) -> bool:
        """Send OTP via SMS (Primary) or WhatsApp (Fallback)"""
        message = f"Your Shawarma Stop verification code is: {otp_code}. Valid for 10 minutes."

        # For development providers, show clear OTP information
        if isinstance(self.provider, (MockSMSProvider, ConsoleSMSProvider)):
            print("=" * 80)
            print("SHAWARMA STOP - OTP VERIFICATION CODE")
            print("=" * 80)
            print(f"Phone: {phone_number}")
            print(f"OTP Code: {otp_code}")
            print(f"Valid for: 10 minutes")
            print("")
            print("DEVELOPMENT MODE:")
            print("   - This OTP appears in the console for testing")
            print("   - Copy this code to complete registration")
            print("   - In production, this will be sent via SMS")
            print("=" * 80)

        # Try SMS first (higher priority)
        sms_sent = await self.send_sms(phone_number, message)
        if sms_sent:
            logger.info(f"OTP sent via SMS to {phone_number}")
            return True

        # Fallback to WhatsApp if SMS fails and provider supports it
        if hasattr(self.provider, 'send_whatsapp'):
            logger.info(f"SMS failed, trying WhatsApp for {phone_number}")
            whatsapp_sent = await self.send_whatsapp(phone_number, message)
            if whatsapp_sent:
                logger.info(f"OTP sent via WhatsApp to {phone_number}")
                return True

        # If both SMS and WhatsApp fail, return False
        logger.error(f"Failed to send OTP to {phone_number} via SMS or WhatsApp")
        return False

    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send custom SMS message"""
        if not self.provider:
            logger.error("No SMS provider configured")
            return False

        return await self.provider.send_sms(phone_number, message)

    async def send_whatsapp(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp message"""
        if not self.provider:
            logger.error("No SMS provider configured")
            return False

        # Only Twilio provider supports WhatsApp
        if hasattr(self.provider, 'send_whatsapp'):
            return await self.provider.send_whatsapp(phone_number, message)
        else:
            logger.error("WhatsApp not supported by current provider")
            return False

# Global SMS service instance
sms_service = SMSService()
