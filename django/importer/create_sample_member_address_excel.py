"""
Script to create a sample Excel file for member/address imports.

This creates an Excel file with the expected column structure for importing
members and addresses from legacy systems.
"""

import openpyxl
from datetime import date

# Create a new workbook
workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.title = "Member Address Import"

# Define all columns as per the specification
headers = [
    "email",
    "____Person",
    "X_heute",
    "P_nr",
    "____Adressangaben",
    "P_ansprechperson",
    "P_co",
    "P_strasse",
    "P_postfach",
    "P_plzort",
    "P_geschlecht",
    "P_anrede",
    "P_land",
    "P_titel",
    "P_briefanrede",
    "____Kontakt",
    "P_nachname",
    "P_vorname",
    "P_telp",
    "P_telg",
    "P_faxp",
    "P_faxg",
    "P_mobilep",
    "P_mobileg",
    "P_emailp",
    "P_emailg",
    "P_homepagep",
    "P_homepageg",
    "____Persönliches",
    "P_beruf",
    "P_arbeitgeber",
    "P_heimatort",
    "P_geburtsort",
    "P_geburtsdatum",
    "P_portalregcode",
    "P_portalurllogin",
    "____Zahlstellen",
    "ZS_dd",
    "ZS_kontoinhaberdd",
    "ZS_lsv",
    "ZS_kontoinhaberlsv",
    "ZS_auszahlungnk",
    "ZS_kontoinhaberauszahlungnk",
    "ZS_auszahlungverzinsung",
    "ZS_kontoinhaberauszahlungverzinsung",
    "ZS_auszahlungmanuell",
    "ZS_kontoinhaberauszahlungmanuell",
]

worksheet.append(headers)

# Add sample data rows
sample_data = [
    [
        "max.mueller@example.com",  # email
        "",  # ____Person (section header)
        "2024-01-15",  # X_heute (join date)
        "1001",  # P_nr (person number)
        "",  # ____Adressangaben (section header)
        "",  # P_ansprechperson (organization name, empty for individuals)
        "",  # P_co (c/o)
        "Bahnhofstrasse 42",  # P_strasse
        "",  # P_postfach (PO box number)
        "3011 Bern",  # P_plzort
        "Herr",  # P_geschlecht
        "Herr",  # P_anrede
        "Schweiz",  # P_land
        "",  # P_titel
        "",  # P_briefanrede
        "",  # ____Kontakt (section header)
        "Müller",  # P_nachname
        "Max",  # P_vorname
        "+41 31 123 45 67",  # P_telp (private phone)
        "+41 31 234 56 78",  # P_telg (business phone)
        "",  # P_faxp
        "",  # P_faxg
        "+41 79 123 45 67",  # P_mobilep (private mobile)
        "",  # P_mobileg (business mobile)
        "max.mueller@example.com",  # P_emailp
        "",  # P_emailg
        "",  # P_homepagep
        "",  # P_homepageg
        "",  # ____Persönliches (section header)
        "Informatiker",  # P_beruf (will be combined with P_arbeitgeber)
        "Tech AG",  # P_arbeitgeber (combined: "Informatiker, Tech AG")
        "Bern",  # P_heimatort
        "Bern",  # P_geburtsort
        "1990-05-15",  # P_geburtsdatum
        "",  # P_portalregcode
        "",  # P_portalurllogin
        "",  # ____Zahlstellen (section header)
        "CH93 0076 2011 6238 5295 7",  # ZS_dd (direct debit IBAN)
        "Max Müller",  # ZS_kontoinhaberdd
        "",  # ZS_lsv
        "",  # ZS_kontoinhaberlsv
        "",  # ZS_auszahlungnk
        "",  # ZS_kontoinhaberauszahlungnk
        "",  # ZS_auszahlungverzinsung
        "",  # ZS_kontoinhaberauszahlungverzinsung
        "",  # ZS_auszahlungmanuell
        "",  # ZS_kontoinhaberauszahlungmanuell
    ],
    [
        "anna.schmidt@example.com",
        "",
        "2024-02-01",
        "1002",
        "",
        "",
        "",
        "Musterweg 15",
        "",
        "8001 Zürich",
        "Frau",
        "Frau",
        "Schweiz",
        "Dr.",
        "",
        "",
        "Schmidt",
        "Anna",
        "+41 44 123 45 67",
        "",
        "",
        "",
        "+41 79 234 56 78",
        "",
        "anna.schmidt@example.com",
        "",
        "www.anna-schmidt.ch",
        "",
        "",
        "Ärztin",
        "Spital Zürich",
        "Zürich",
        "Basel",
        "1985-08-20",
        "",
        "",
        "",
        "CH14 0070 0110 0023 8599 1",
        "Anna Schmidt",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ],
    [
        "kontakt@example-gmbh.ch",
        "",
        "2024-03-10",
        "1003",
        "",
        "Example GmbH",  # Organization name
        "",
        "Hauptstrasse 100",
        "Postfach 1234",  # PO Box (will be split to: po_box=True, po_box_number="1234")
        "4000 Basel",
        "Firma",
        "Firma",
        "Schweiz",
        "",
        "",
        "",
        "Weber",  # Contact person last name
        "Thomas",  # Contact person first name
        "+41 61 123 45 67",
        "+41 61 234 56 78",
        "",
        "",
        "",
        "+41 79 345 67 89",
        "kontakt@example-gmbh.ch",
        "thomas.weber@example-gmbh.ch",
        "www.example-gmbh.ch",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "CH36 0070 0115 2008 8125 9",
        "Example GmbH",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ],
]

for row in sample_data:
    worksheet.append(row)

# Auto-size columns for better readability
for column in worksheet.columns:
    max_length = 0
    column_letter = column[0].column_letter
    for cell in column:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass
    adjusted_width = min(max_length + 2, 50)
    worksheet.column_dimensions[column_letter].width = adjusted_width

# Save the workbook
filename = "sample_member_address_import.xlsx"
workbook.save(filename)
print(f"Sample Excel file created: {filename}")
print(f"Contains {len(sample_data)} sample records with all required columns.")

