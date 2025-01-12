import asyncio
import aiosmtplib
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from config.settings import settings


connection_config = ConnectionConfig(
                                        MAIL_USERNAME = settings.MAIL_USERNAME,
                                        MAIL_PASSWORD = settings.MAIL_PASSWORD,
                                        MAIL_FROM = settings.MAIL_FROM,
                                        MAIL_PORT = settings.MAIL_PORT,
                                        MAIL_SERVER = settings.MAIL_SERVER,
                                        MAIL_FROM_NAME = settings.MAIL_FROM_NAME,
                                        MAIL_STARTTLS = settings.MAIL_STARTTLS,
                                        MAIL_SSL_TLS = settings.MAIL_SSL_TLS,
                                        USE_CREDENTIALS = settings.USE_CREDENTIALS,
                                        VALIDATE_CERTS = settings.VALIDATE_CERTS,
                                        TEMPLATE_FOLDER = settings.TEMPLATE_FOLDER)


def send_sync(message: MessageSchema, template_name: str, background_task: BackgroundTasks):

    async def try_to_send(message=message, template_name=template_name):
        try:
            mail_service = FastMail(connection_config)
            await mail_service.send_message(message=message, template_name=template_name)
        except aiosmtplib.SMTPException:
            pass

    background_task.add_task(try_to_send, message=message, template_name=template_name)


async def send_email(message: MessageSchema, template_name: str, background_task: BackgroundTasks):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, send_sync, message, template_name, background_task)
