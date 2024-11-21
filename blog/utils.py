import random
import pyotp
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

def generate_otp(length=6):
    """Generate a numeric OTP of specified length"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp_email(email, otp):
    """Send OTP via email"""
    subject = 'Your OTP for Email Verification'
    message = f'''
    Dear User,

    Your One-Time Password (OTP) for email verification is:

    {otp}

    This OTP will expire in 10 minutes. Please do not share this with anyone.

    Best regards,
    Your Blog Application Team
    '''
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        send_mail(
            subject, 
            message, 
            from_email, 
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False