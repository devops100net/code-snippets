import pandas as pd

def create_excel_from_csv(input_csv, output_excel):
    # Read the CSV file
    df = pd.read_csv(input_csv)

    # Ensure 'Invoice Amount' and 'VAT' are strings for replacement operation
    df['Invoice Amount'] = df['Invoice Amount'].astype(str)
    df['VAT'] = df['VAT'].astype(str)

    # Remove EUR and € signs and convert amounts to float
    df['Invoice Amount'] = df['Invoice Amount'].str.replace(' EUR', '').str.replace('€', '').astype(float)
    df['VAT'] = df['VAT'].str.replace(' EUR', '').str.replace('€', '').astype(float)

    # Calculate totals
    total_amount = df['Invoice Amount'].sum()
    total_vat = df['VAT'].sum()

    # Reorder columns
    df = df[['Sender Name', 'Invoice Number', 'Invoice Amount', 'VAT']]

    # Create rows for an empty row and the totals
    empty_row = pd.DataFrame([{}])
    totals_row = pd.DataFrame([{"Invoice Amount": total_amount, "VAT": total_vat}])

    # Concatenate the empty row and totals row to the dataframe
    df = pd.concat([df, empty_row, totals_row], ignore_index=True)

    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(output_excel, engine='xlsxwriter')

    # Write the DataFrame to the Excel file
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    # Access the XlsxWriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # Set all column widths to 15
    worksheet.set_column('A:D', 15)  # Set width of all columns to 15

    # Add a header format with right alignment
    header_format = workbook.add_format({'bold': True, 'align': 'right'})

    # Write the column headers with the format
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    # Close the Pandas Excel writer and output the Excel file
    writer.close()

# Example usage
create_excel_from_csv('export-pdf.csv', 'invoices-output.xls')

