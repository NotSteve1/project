from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

email_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM_ADDRESS,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(email_config)


async def send_otp_email(to_email: str, otp: str) -> None:
    message = MessageSchema(
        subject="Verify your email",
        recipients=[to_email],
        body=f"Your verification code is: {otp}\nThis code expires in 10 minutes.",
        subtype=MessageType.plain,
    )
    await fm.send_message(message)