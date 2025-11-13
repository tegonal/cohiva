# Importer Quick Start

## Member/Address Import

### 1. Generate Sample File
```bash
cd /path/to/django
python importer/create_sample_member_address_excel.py
```

### 2. Upload
- Web: Navigate to `/importer/upload/member-address/`
- CLI: `python manage.py process_member_imports --job-id <ID>`

### 3. Verify
- Check results summary
- View imported data at `/admin/geno/address/` and `/admin/geno/member/`

**See [MEMBER_ADDRESS_IMPORT.md](MEMBER_ADDRESS_IMPORT.md) for complete column reference.**

---

## General Setup

### 1. Enable App
Add to `cohiva/base_config.py`:
```python
FEATURES = [
    # ...existing features...
    "importer",
]
```

### 2. Run Migrations
```bash
./manage.py makemigrations importer
./manage.py migrate
```

### 3. Access
- Web: `/importer/upload/`
- Admin: `/admin/importer/`

---

## Custom Importer Example

```python
# importer/custom_importers.py
from importer.services import ExcelImporter
from myapp.models import MyModel

class MyImporter(ExcelImporter):
    def _process_single_row(self, row_data):
        MyModel.objects.update_or_create(
            email=row_data.get('Email'),
            defaults={
                'name': row_data.get('Name'),
                'phone': row_data.get('Phone'),
            }
        )
```

```python
# views.py
from importer.custom_importers import MyImporter

def my_view(request):
    # ... create import_job ...
    importer = MyImporter(import_job)
    results = importer.process()
```

---

## Excel Format

```
| Column1  | Column2  | Column3  |
|----------|----------|----------|
| value1   | value2   | value3   |
```

- First row = headers (becomes dict keys)
- Empty rows/columns skipped
- Supported: .xlsx, .xls (max 10MB)

---

## Troubleshooting

**Can't upload**: Check logged in, file size <10MB, .xlsx format

**No records created**: Implement custom `_process_single_row()` logic

**Import failed**: Check `/admin/importer/importjob/` for error details
