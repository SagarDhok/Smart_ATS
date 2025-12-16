# core/utils/email.py

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def send_brevo_email(to_email: str, subject: str, html_content: str) -> bool:
    payload = {
        "sender": {
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": "Smart ATS"
        },
        "to": [
            {"email": to_email}
        ],
        "subject": subject,
        "htmlContent": html_content
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }

    try:
        response = requests.post(
            BREVO_URL,
            json=payload,
            headers=headers,
            timeout=10  # IMPORTANT: prevents hanging
        )

        if response.status_code in (200, 201, 202):
            return True

        logger.error(f"Brevo error {response.status_code}: {response.text}")
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Brevo request failed: {e}")
        return False
