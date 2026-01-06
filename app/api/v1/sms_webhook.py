from fastapi import APIRouter, Request, Response, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhook")
async def twilio_sms_webhook(request: Request):
    """Handle incoming SMS from Twilio"""
    try:
        # Get form data from Twilio
        data = await request.form()

        # Extract SMS details
        from_number = data.get('From')
        to_number = data.get('To')
        message_body = data.get('Body')
        message_sid = data.get('MessageSid')
        account_sid = data.get('AccountSid')

        logger.info(f"Incoming SMS - From: {from_number}, To: {to_number}, Body: {message_body}")

        # Here you can process incoming SMS
        # For example: handle OTP replies, customer support messages, etc.

        # For OTP verification, you might want to store replies or handle support
        if message_body and len(message_body.strip()) > 0:
            # Process the incoming message
            # You can add database operations here if needed
            pass

        # Return empty TwiML response (no auto-reply SMS)
        twiml_response = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'

        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
