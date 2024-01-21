import pandas as pd
import hashlib
import datetime
import openpyxl

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

    date_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_for_filename = datetime.datetime.now().strftime("%H%M")
    checksum_row = pd.DataFrame([{'Sender Name': f'Date: {date_stamp}', 'Invoice Number': f'Checksum: {checksum}'}])

    df = pd.concat([checksum_row, df, pd.DataFrame([{}]), totals_row], ignore_index=True)

    excel_file_name = f'invoices-{time_for_filename}-{checksum[:8]}.xlsx'
    df.to_excel(excel_file_name, index=False)

    workbook = openpyxl.load_workbook(excel_file_name)
    sheet = workbook.active
    for column in sheet.columns:
        sheet.column_dimensions[openpyxl.utils.get_column_letter(column[0].column)].width = 15

    workbook.save(excel_file_name)

    return excel_file_name, f'Date: {date_stamp}, Checksum: {checksum}'

excel_file_name, email_subject = create_excel_from_csv('export-pdf.csv')

