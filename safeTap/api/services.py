# Create a new file api/services.py
import random
import string
import importlib
try:
    _twilio_rest = importlib.import_module('twilio.rest')
    Client = getattr(_twilio_rest, 'Client', None)
except Exception:
    Client = None
from django.conf import settings

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_sms_verification(phone_number, code):
    # Using Twilio as an example - you'll need to configure your own SMS service
    try:
        if Client is None:
            print("Twilio client not available: install the 'twilio' package to enable SMS sending.")
            return False
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=f"Your verification code is: {code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False