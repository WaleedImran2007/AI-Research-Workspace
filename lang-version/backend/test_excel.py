# from openpyxl import load_workbook

# def find_column(sheet, column_name):
#     for cell in sheet[1]:  # Assuming the first row contains headers
#         if cell.value == column_name:
#             return cell.column

#     return None  # Column not found

# def find_row(sheet, column_name, value):
#     column = find_column(sheet, column_name)

#     if column is None:
#         print(f"Column '{column_name}' not found.")
#         return None

#     print(f"Searching column: {column_name}")
#     print(f"Looking for value: '{value}'")

#     for row in range(2, sheet.max_row + 1):
#         cell_value = sheet.cell(
#             row = row,
#             column = column
#         ).value

#         print(
#             f"Row {row}: '{cell_value}' | "
#             f"Type: {type(cell_value)}"
#         )

#         if cell_value == value:
#             return row

#     return None  # Row not found

# def add_marks(input_file, output_file, amount):
#     workbook = load_workbook(input_file)
#     sheet = workbook["Sheet1"]

#     marks_column = find_column(sheet, "Marks")
#     if marks_column is None:
#         print("Marks column not found.")
#         return

#     print(f"Marks column found at index: {marks_column}")

#     for row in range(2, sheet.max_row + 1):
#         cell = sheet.cell(
#             row = row,
#             column = marks_column
#         )

#         if cell.value is not None:
#             cell.value += amount
#             cell.value = min(cell.value, 100)  # Ensure marks do not exceed 100

#             print(f"Row {row}: Updated Marks = {cell.value}")

#     workbook.save(output_file)
#     print("Marks updated successfully!")

# def add_result_column(input_file, output_file):
#     workbook = load_workbook(input_file)
#     sheet = workbook["Sheet1"]

#     # Add a new column
#     marks_column = find_column(sheet, "Marks")
#     print(f"Marks column found at index: {marks_column}")
    
#     sheet.insert_cols(marks_column + 1)  # Insert a new column after the "Marks" column
#     print(f"New column inserted at index: {marks_column + 1}")

#     # Add header for the new column
#     sheet.cell(
#         row = 1,
#         column = marks_column + 1,
#         value = "Result"
#     )

#     for row in range(2, sheet.max_row + 1):
#         marks = sheet.cell(
#             row = row,
#             column = marks_column
#         ).value

#         print(f"Row {row}: Marks = {marks}")

#         if marks >= 50:
#             sheet.cell(
#                 row = row,
#                 column = marks_column + 1,
#             ).value = "Pass"
#         else:
#             sheet.cell(
#                 row = row,
#                 column = marks_column + 1,
#             ).value = "Fail"

#     # Save the modified workbook
#     workbook.save(output_file)
#     print("Excel file modified successfully!")

# def rename_column(input_file, output_file, old_name, new_name):
#     workbook = load_workbook(input_file)
#     sheet = workbook["Sheet1"]

#     column = find_column(sheet, old_name)

#     if column is None:
#         print(f"Column '{old_name}' not found.")
#         return

#     # Rename the column header
#     sheet.cell(
#         row = 1,
#         column = column,
#         value = new_name
#     )

#     # Save the modified workbook
#     workbook.save(output_file)
#     print(f"Column '{old_name}' renamed to '{new_name}' successfully!")

# def delete_column(input_file, output_file, column_name):
#     workbook = load_workbook(input_file)
#     sheet = workbook["Sheet1"]

#     # Find the column index based on the column name
#     column_index = find_column(sheet, column_name)

#     if column_index is None:
#         print(f"Column '{column_name}' not found.")
#         return

#     # Delete the column
#     sheet.delete_cols(column_index)

#     # Save the modified workbook
#     workbook.save(output_file)
#     print(f"Column '{column_name}' deleted successfully!")

# def add_student(input_file, output_file, data:dict):
#     workbook = load_workbook(input_file)
#     sheet = workbook["Sheet1"]

#     new_row = sheet.max_row + 1

#     for column in range(1, sheet.max_column + 1):
#         header = sheet.cell(
#             row = 1,
#             column = column
#         ).value

#         sheet.cell(
#             row = new_row,
#             column = column,
#             value=data.get(header, "")
#         )

#     # Save the modified workbook
#     workbook.save(output_file)
#     print("New student added successfully!")

# def delete_student(input_file, output_file, column_name, value):
#     workbook = load_workbook(input_file)
#     sheet = workbook["Sheet1"]

#     row_to_delete = find_row(sheet, column_name, value)

#     if row_to_delete is None:
#         print(f"Student with {column_name} '{value}' not found.")
#         return

#     print(f"Deleting row {row_to_delete} for student with {column_name} '{value}'.")

#     # Delete the row
#     sheet.delete_rows(row_to_delete)

#     # Save the modified workbook
#     workbook.save(output_file)
#     print(f"Student with {column_name} '{value}' deleted successfully!")



# # add_result_column("students.xlsx", "students_modified.xlsx")
# # add_marks("students.xlsx", "students_modified.xlsx", 10)
# # rename_column("students.xlsx", "students_modified.xlsx", "Marks", "Final Marks")

# # new_student = {
# #     "Name": "John Doe",
# #     "Age": 20,
# #     "Marks": 85,
# #     "City": "Karachi"
# # }

# # add_student("students.xlsx", "students_modified.xlsx", new_student)

# delete_student("students.xlsx", "students_modified.xlsx", "Name", "John Doe")