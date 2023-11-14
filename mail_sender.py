from threading import Thread
from flask import render_template, copy_current_request_context
from flask_mail import Message
from app import mail
from smtplib import SMTPException


import asyncio

async def send_mail(subject: str, body: str, users: list[str]) -> tuple[bool, str | None]:
    """
        Отправляет письмо на адреса электронной почты пользователей

        :param: subject: заголовок письма, body: текст письма, users: список адресов эл. почты
        :return: кортеж с информацией о статусе отправки письма (true/false и описание ошибки(при наличии))
        """
    try:
        async def send_email(user):
            with mail.connect() as conn:
                msg = Message(recipients=[user],
                              body=body,
                              subject=subject)

                await conn.send(msg)

        tasks = []
        for user in users:
            tasks.append(asyncio.create_task(send_email(user)))

        await asyncio.gather(*tasks)

        app.logger.info(f'Письмо с темой "{subject}" отправлено пользователям {users}')
        return (True, )
    except SMTPException as err:
        return (False, str(err))