from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from ..config.logger import logger
from ..config.settings import setting

conf = ConnectionConfig(
    MAIL_USERNAME=setting.MAIL_USERNAME,
    MAIL_PASSWORD=setting.MAIL_PASSWORD,
    MAIL_FROM=setting.MAIL_FROM,
    MAIL_PORT=setting.MAIL_PORT,
    MAIL_SERVER=setting.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_verification_otp_email(email: str, otp: str) -> None:
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; padding: 24px; border: 1px solid #e5e7eb; border-radius: 10px;">
        <h2 style="color: #111827; margin-bottom: 8px;">Verify Your Email</h2>
        <p style="color: #4b5563; font-size: 14px;">Use the 6-digit verification code below to verify your Py_Todo account:</p>
        <div style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563eb; background: #eff6ff; padding: 14px; text-align: center; border-radius: 8px; margin: 18px 0;">
            {otp}
        </div>
        <p style="color: #6b7280; font-size: 12px;">This code expires in <strong>5 minutes</strong>. If you didn't request this, please ignore this email.</p>
    </div>
    """

    message = MessageSchema(
        subject="Your Verification Code - Py_Todo",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        logger.error(f"Failed to send verification OTP email to {email}. Error: {e}")
        raise
