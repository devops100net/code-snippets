import pandas as pd
import hashlib
import datetime
import openpyxl
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def calculate_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

def create_excel_from_csv(input_csv):
    checksum = calculate_checksum(input_csv)
    df = pd.read_csv(input_csv)

    total_amount = df['Invoice Amount'].sum()
    total_vat = df['VAT'].sum()
    totals_row = pd.DataFrame([{'Sender Name': 'Totals', 'Invoice Number': '', 'Invoice Amount': total_amount, 'VAT': total_vat}])

    time_for_filename = datetime.datetime.now().strftime("%H%M")
    date_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    checksum_row = pd.DataFrame([{'Sender Name': f'Date: {date_stamp}', 'Invoice Number': f'Checksum: {checksum[:8]}'}])

    df = pd.concat([checksum_row, df, pd.DataFrame([{}]), totals_row], ignore_index=True)

    excel_file_name = f'invoices-{time_for_filename}-{checksum[:8]}.xlsx'
    df.to_excel(excel_file_name, index=False)

    workbook = openpyxl.load_workbook(excel_file_name)
    sheet = workbook.active
    for column in sheet.columns:
        sheet.column_dimensions[openpyxl.utils.get_column_letter(column[0].column)].width = 15
    workbook.save(excel_file_name)

    return excel_file_name, f'Date: {date_stamp}, Checksum: {checksum[:8]}'

def send_email_with_attachment(subject, message, file_path):
    send_from = os.getenv('SMTP_USERNAME')
    send_to = os.getenv('EMAIL_RECIPIENT')

    if not send_to:
        print("Recipient email not set in environment variable.")
        return

    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

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

    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(smtp_username, smtp_password)
    text = msg.as_string()
    server.sendmail(send_from, send_to, text)
    server.quit()
    print(f"Email sent with attachment: {os.path.basename(file_path)}")

# Run the processes
excel_file_name, email_subject = create_excel_from_csv('export-pdf.csv')
send_email_with_attachment(email_subject, 'Please find the attached invoice report.', excel_file_name)

