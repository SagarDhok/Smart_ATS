# core/utils/email.py

import resend
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


def send_resend_email(to_email: str, subject: str, html_content: str) -> bool:
    try:
        resend.Emails.send({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": to_email,
            "subject": subject,
            "html": html_content,
        })
        return True
    except Exception as e:
        logger.error(f"Resend email failed to {to_email}: {e}")
        return False
