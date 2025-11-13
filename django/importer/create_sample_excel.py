"""
Example script to create a sample Excel file for testing the importer.
"""

import openpyxl

# Create a new workbook
workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.title = "Sample Data"

# Add headers
headers = ["Name", "Email", "Phone", "City", "Age"]
worksheet.append(headers)

# Add sample data
sample_data = [
    ["John Doe", "john.doe@example.com", "+41 79 123 45 67", "Bern", 30],
    ["Jane Smith", "jane.smith@example.com", "+41 79 234 56 78", "Zurich", 25],
    ["Bob Wilson", "bob.wilson@example.com", "+41 79 345 67 89", "Basel", 35],
    ["Alice Brown", "alice.brown@example.com", "+41 79 456 78 90", "Geneva", 28],
    ["Charlie Davis", "charlie.davis@example.com", "+41 79 567 89 01", "Lausanne", 32],
]

for row in sample_data:
    worksheet.append(row)

# Save the workbook
workbook.save("sample_import.xlsx")
print("Sample Excel file created: sample_import.xlsx")

