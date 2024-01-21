``
Make sure to set these variables
export SMTP_SERVER="smtp.yourserver.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your_username"
export SMTP_PASSWORD="your_password"
``

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def send_email_with_attachment(send_from, send_to, subject, message, file_path):
    # Retrieve environment variables for SMTP settings
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    # Attach the file
    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")
    msg.attach(part)

    # SMTP server setup
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    text = msg.as_string()
    server.sendmail(send_from, send_to, text)
    server.quit()

# Example usage
send_email_with_attachment('sender@example.com', 'recipient@example.com',
                           'Invoice Report', 'Please find the attached invoice report.', '/path/to/your/file.xls')

