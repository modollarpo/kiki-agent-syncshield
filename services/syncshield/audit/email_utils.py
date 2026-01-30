import smtplib
from email.message import EmailMessage
import os

def send_pdf_report(smtp_server, smtp_port, smtp_user, smtp_pass, to_email, subject, body, pdf_path):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(body)
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    print(f"[Email] Sent PDF report to {to_email}")
