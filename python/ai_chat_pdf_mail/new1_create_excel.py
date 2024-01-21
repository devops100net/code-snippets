import pandas as pd
import hashlib
import datetime
import openpyxl
import os
from openpyxl.styles import Font

def calculate_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

def create_excel_from_csv(input_csv):
    df = pd.read_csv(input_csv)

    total_amount = df['Invoice Amount'].sum()
    total_vat = df['VAT'].sum()
    totals_row = pd.DataFrame([{'Sender Name': 'Totals', 'Invoice Number': '', 'Invoice Amount': total_amount, 'VAT': total_vat}])

    time_for_filename = datetime.datetime.now().strftime("%H%M")
    checksum = calculate_checksum(input_csv)
    description_row = pd.DataFrame([{'Sender Name': os.getenv('sheet_description'), 'Invoice Number': '', 'Invoice Amount': '', 'VAT': ''}])

    df = pd.concat([description_row, pd.DataFrame([{}]), df, totals_row], ignore_index=True)

    excel_file_name = f'invoices-{time_for_filename}-{checksum[:8]}.xlsx'
    df.to_excel(excel_file_name, index=False)

    workbook = openpyxl.load_workbook(excel_file_name)
    sheet = workbook.active

    # Set column widths and make the header row bold
    for column in sheet.columns:
        sheet.column_dimensions[openpyxl.utils.get_column_letter(column[0].column)].width = 15
    for cell in sheet["3:3"]:
        cell.font = Font(bold=True)

    workbook.save(excel_file_name)

    return excel_file_name

# Run the process
excel_file_name = create_excel_from_csv('export-pdf.csv')

