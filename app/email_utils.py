import smtplib
from email.message import EmailMessage

from flask import current_app


def send_email(to_email, subject, body):
    host = current_app.config["SMTP_HOST"]
    port = current_app.config["SMTP_PORT"]
    user = current_app.config["SMTP_USER"]
    password = current_app.config["SMTP_PASSWORD"]
    use_tls = current_app.config["SMTP_USE_TLS"]

    if not host or not port or not user or not password:
        raise ValueError("SMTP configuration is incomplete.")

    message = EmailMessage()
    message["From"] = user
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    if use_tls:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP_SSL(host, port) as smtp:
            smtp.login(user, password)
            smtp.send_message(message)
