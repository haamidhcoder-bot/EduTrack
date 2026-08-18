import smtplib
from email.message import EmailMessage


def email(from_address, to_address, subject, message, app_password):
    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address

    msg.set_content(message)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()

        server.login(
            from_address,
            app_password
        )

        server.send_message(msg)

def email_file(from_address,to_address,subject,message,file_name,app_password):
    msg = EmailMessage()

    msg["Subject"] =subject
    msg["From"] = from_address
    msg["To"] = to_address

    with open(file_name, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="text",
            subtype="plain",
            filename=file_name
        )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()

        server.login(
            from_address,
            app_password
        )

        server.send_message(msg)
