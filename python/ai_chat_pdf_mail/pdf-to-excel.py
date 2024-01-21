# Convert the modified CSV data to a DataFrame
df_modified = pd.read_csv(StringIO(modified_csv_data))

# Create a Pandas Excel writer using XlsxWriter as the engine
excel_file_path = '/mnt/data/modified_invoices.xlsx'
writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')

# Write the DataFrame to the Excel file
df_modified.to_excel(writer, sheet_name='Sheet1', index=False)

# Access the XlsxWriter workbook and worksheet objects
workbook  = writer.book
worksheet = writer.sheets['Sheet1']

# Set the column widths
worksheet.set_column('A:A', 30)  # Sender Name
worksheet.set_column('B:B', 20)  # Invoice Number
worksheet.set_column('C:C', 15)  # Invoice Amount
worksheet.set_column('D:D', 10)  # VAT

# Add a header format
header_format = workbook.add_format({'bold': True})

# Write the column headers with the format
for col_num, value in enumerate(df_modified.columns.values):
    worksheet.write(0, col_num, value, header_format)

# Close the Pandas Excel writer and output the Excel file
writer.save()

excel_file_path

