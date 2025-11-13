# Member/Address Import - Quick Guide

## Step 1: Create Sample File (First Time)

```bash
cd /path/to/django
python importer/create_sample_member_address_excel.py
```

This creates `sample_member_address_import.xlsx` with example data.

## Step 2: Upload File

### Option A: Web Interface
1. Navigate to `/importer/upload/member-address/`
2. Click "Choose File" and select your Excel file
3. Click "Upload and Process"
4. View results

### Option B: Command Line
```bash
# Process specific import by ID
python manage.py process_member_imports --job-id 123

# Process all pending imports
python manage.py process_member_imports --all
```

## Step 3: Verify Import

1. Check results summary (success count, error count)
2. Go to `/admin/geno/address/` to see imported addresses
3. Go to `/admin/geno/member/` to see imported members
4. Check `/admin/importer/importjob/` for detailed error logs

---

## Excel File Requirements

### Required Columns (47 total)

Your Excel file must have these columns in the first row (exact names):

```
email, ____Person, X_heute, P_nr, ____Adressangaben, P_ansprechperson, 
P_co, P_strasse, P_postfach, P_plzort, P_geschlecht, P_anrede, P_land, 
P_titel, P_briefanrede, ____Kontakt, P_nachname, P_vorname, P_telp, 
P_telg, P_faxp, P_faxg, P_mobilep, P_mobileg, P_emailp, P_emailg, 
P_homepagep, P_homepageg, ____Persönliches, P_beruf, P_arbeitgeber, 
P_heimatort, P_geburtsort, P_geburtsdatum, P_portalregcode, 
P_portalurllogin, ____Zahlstellen, ZS_dd, ZS_kontoinhaberdd, ZS_lsv, 
ZS_kontoinhaberlsv, ZS_auszahlungnk, ZS_kontoinhaberauszahlungnk, 
ZS_auszahlungverzinsung, ZS_kontoinhaberauszahlungverzinsung, 
ZS_auszahlungmanuell, ZS_kontoinhaberauszahlungmanuell
```

### Minimum Required Data

Each row must have:
- **P_nachname** (last name) OR **P_vorname** (first name)
- **X_heute** (join date) - only if creating a member

### Important Columns

| Column | Purpose | Example |
|--------|---------|---------|
| P_nr | Unique ID for updates | 1001 |
| P_nachname | Last name | Müller |
| P_vorname | First name | Max |
| P_strasse | Street & number | Bahnhofstrasse 42 |
| P_plzort | ZIP & city | 3011 Bern |
| P_emailp | Primary email | max@example.com |
| X_heute | Join date → creates Member | 2024-01-15 |
| ZS_dd | Bank IBAN | CH93 0076 2011 6238 5295 7 |
| P_ansprechperson | Organization name | Example GmbH |

**Note:** Columns starting with `____` are section headers and can be empty.

---

## Data Formatting Tips

### Dates
Use one of these formats:
- `2024-01-15` (YYYY-MM-DD)
- `15.01.2024` (DD.MM.YYYY)
- `15/01/2024` (DD/MM/YYYY)

### Street Address
Will be auto-split:
- Input: `Bahnhofstrasse 42`
- Result: street_name: "Bahnhofstrasse", house_number: "42"

### ZIP/City
Will be auto-split:
- Input: `3011 Bern`
- Result: city_zipcode: "3011", city_name: "Bern"

### Organizations
Fill **P_ansprechperson** with company name → treated as organization

---

## Updating Existing Records

The importer automatically detects duplicates:

1. **By P_nr**: If record with same `P_nr` exists → updates it
2. **By email**: If no P_nr match, tries email → updates it
3. **Otherwise**: Creates new record

You can safely re-import files to update records.

---

## Troubleshooting

### Import Failed
- Check admin: `/admin/importer/importjob/`
- Look at `error_message` field
- Review individual row errors in ImportRecord

### Row Skipped
- Check ImportRecord for specific error message
- Common issues:
  - Missing required fields (P_nachname/P_vorname)
  - Invalid date format
  - Empty row

### No Member Created
- Member requires `X_heute` (join date) field
- Check date format is valid

