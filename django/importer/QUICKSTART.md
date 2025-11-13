# Quick Start Guide - Importer App

This guide will help you get started with the importer app in just a few minutes.

## 1. Enable the App

Add `"importer"` to the `FEATURES` list in your `cohiva/base_config.py`:

```python
FEATURES = [
    "api",
    "portal",
    "reservation",
    "report",
    "credit_accounting",
    "website",
    "cms",
    "importer",  # Add this line
]
```

## 2. Run Migrations

Create and apply the database migrations:

```bash
./manage.py makemigrations importer
./manage.py migrate
```

## 3. Access the Importer

### Web Interface

Navigate to: `http://your-domain/importer/upload/`

You can:
- Upload Excel files
- View recent import jobs
- Check import results

### Admin Interface

Navigate to: `http://your-domain/admin/importer/`

You can:
- View all import jobs
- See detailed import records
- Download uploaded files
- Check error messages

## 4. Try It Out

### Create a Sample Excel File

Run the provided script to create a sample Excel file:

```bash
cd importer
python create_sample_excel.py
```

This creates `sample_import.xlsx` with sample data.

### Upload and Process

1. Go to `/importer/upload/`
2. Click "Choose File" and select `sample_import.xlsx`
3. Click "Upload and Process"
4. View the results

## 5. Customize for Your Needs

### Option A: Simple Customization

Edit `importer/services.py` and modify the `_process_single_row` method:

```python
def _process_single_row(self, row_data: Dict):
    # Add your custom logic here
    from myapp.models import MyModel
    
    MyModel.objects.create(
        name=row_data.get('Name'),
        email=row_data.get('Email'),
        # ... more fields
    )
```

### Option B: Create a Custom Importer

Create a new file `importer/custom_importers.py`:

```python
from importer.services import ExcelImporter
from myapp.models import MyModel

class MyCustomImporter(ExcelImporter):
    def _process_single_row(self, row_data):
        # Validate data
        if not row_data.get('Email'):
            raise ValidationError("Email is required")
        
        # Create or update records
        MyModel.objects.update_or_create(
            email=row_data.get('Email'),
            defaults={
                'name': row_data.get('Name'),
                'phone': row_data.get('Phone'),
            }
        )
```

Then use it in your views:

```python
from importer.custom_importers import MyCustomImporter

def my_import_view(request):
    # ... create import_job ...
    importer = MyCustomImporter(import_job)
    results = importer.process()
```

## 6. Excel File Format

The importer expects:

```
| Column1  | Column2  | Column3  |
|----------|----------|----------|
| value1   | value2   | value3   |
| value4   | value5   | value6   |
```

- **First row**: Column headers (used as dictionary keys)
- **Subsequent rows**: Data
- **Empty rows**: Automatically skipped
- **Empty columns**: Skip columns without headers

## 7. Common Use Cases

### Import Members/Users

```python
class MemberImporter(ExcelImporter):
    def _process_single_row(self, row_data):
        Member.objects.create(
            first_name=row_data.get('First Name'),
            last_name=row_data.get('Last Name'),
            email=row_data.get('Email'),
            joined_date=row_data.get('Join Date'),
        )
```

### Import Financial Transactions

```python
class TransactionImporter(ExcelImporter):
    def _process_single_row(self, row_data):
        Transaction.objects.create(
            date=row_data.get('Date'),
            amount=Decimal(row_data.get('Amount', 0)),
            description=row_data.get('Description'),
            category=row_data.get('Category'),
        )
```

### Update Existing Records

```python
class UpdateImporter(ExcelImporter):
    def _process_single_row(self, row_data):
        member_id = row_data.get('Member ID')
        Member.objects.filter(id=member_id).update(
            phone=row_data.get('Phone'),
            address=row_data.get('Address'),
        )
```

## 8. Async Processing (Optional)

For large files, use Celery:

```python
# tasks.py
from celery import shared_task
from importer.services import process_import_job

@shared_task
def process_import_async(import_job_id):
    return process_import_job(import_job_id)
```

```python
# views.py
from myapp.tasks import process_import_async

# After creating the job:
process_import_async.delay(import_job.id)
messages.success(request, "Import started in background")
```

## 9. Troubleshooting

### Import fails with "File not found"

Make sure your `MEDIA_ROOT` is configured in settings:

```python
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

### Can't access the upload page

Make sure you're logged in. The importer requires authentication.

### Excel file won't upload

Check:
- File size (max 10MB by default)
- File extension (.xlsx or .xls)
- File permissions in upload directory

### Import succeeds but no records created

Check `_process_single_row` method - the default implementation just validates data but doesn't create records. You need to add your custom logic.

## 10. Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check the [tests](tests/) for examples
- Customize the templates in `templates/importer/`
- Add API endpoints if needed
- Implement email notifications on import completion

## Support

For issues or questions, check the Cohiva documentation or contact your system administrator.

