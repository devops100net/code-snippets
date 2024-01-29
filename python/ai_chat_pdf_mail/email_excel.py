import smtplib
import os
import glob
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def find_latest_file(pattern):
    list_of_files = glob.glob(pattern)
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file

def send_email_with_attachment(send_from, subject, message):
    send_to = os.getenv('EMAIL_RECIPIENT')
    if not send_to:
        print("Recipient email not set in environment variable.")
        return

    file_path = find_latest_file('invoices-*.xlsx')
    if not file_path:
        print("No invoice file found.")
        return

    subject = f"{subject}, File: {os.path.basename(file_path)}"

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")
    msg.attach(part)

    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(smtp_username, smtp_password)
    text = msg.as_string()
    server.sendmail(send_from, send_to, text)
    server.quit()
    print(f"Email sent with attachment: {os.path.basename(file_path)}")

send_email_with_attachment('bert.achterkamp@devops100.net', email_subject, 'Please find the attached invoice report.')

