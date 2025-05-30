from fastapi_mail import FastMail, MessageSchema


class MailService:
    def __init__(self, mail: FastMail):
        self.mail = mail

    async def send_email(self, message: MessageSchema):
        await self.mail.send_message(message)
