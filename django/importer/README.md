# Importer App

Django app for importing data from Excel documents.

## Features

- Upload Excel files (.xlsx, .xls)
- Track import jobs with status (pending, processing, completed, failed)
- Record-level tracking with success/error status
- Admin interface for monitoring imports
- Web interface for uploading files
- Extensible architecture for custom import logic

## Installation

The app is already included in the Cohiva project. To enable it:

1. Add `'importer'` to `INSTALLED_APPS` in `cohiva/settings_defaults.py`
2. Add URL patterns to `cohiva/urls.py`
3. Run migrations: `./manage.py makemigrations importer && ./manage.py migrate`

## Usage

### Basic Upload

Navigate to `/importer/upload/` to upload an Excel file. The system will:

1. Validate the file (format, size)
2. Create an ImportJob record
3. Process the file row by row
4. Track success/failure for each row
5. Display results

### Admin Interface

The admin interface provides:

- List view of all import jobs
- Detail view showing import records
- Status badges and file download links
- Error message display

Access it at `/admin/importer/`

### Customizing Import Logic

To implement custom import logic, subclass `ExcelImporter` and override `_process_single_row`:

```python
from importer.services import ExcelImporter
from myapp.models import MyModel

class MyImporter(ExcelImporter):
    def _process_single_row(self, row_data):
        # Your custom logic
        MyModel.objects.create(
            name=row_data.get('Name'),
            email=row_data.get('Email'),
            # ... more fields
        )
```

Then use your custom importer in views or tasks:

```python
from myapp.importers import MyImporter

importer = MyImporter(import_job)
results = importer.process()
```

### Async Processing with Celery

For large files, process imports asynchronously:

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

# In your view after creating the job:
process_import_async.delay(import_job.id)
```

## Models

### ImportJob

Tracks overall import jobs.

**Fields:**
- `created_at` - When the job was created
- `updated_at` - When the job was last updated
- `created_by` - User who created the job
- `file` - The uploaded Excel file
- `status` - Job status (pending, processing, completed, failed)
- `records_imported` - Number of successfully imported records
- `error_message` - Error message if job failed
- `result_data` - JSON field with processing results

### ImportRecord

Tracks individual records from an import.

**Fields:**
- `job` - Related ImportJob
- `row_number` - Row number in the Excel file
- `data` - JSON field with row data
- `created_at` - When the record was created
- `error_message` - Error message if row failed
- `success` - Whether the row was processed successfully

## Excel File Format

The importer expects:

- First row contains column headers
- Subsequent rows contain data
- Empty rows are skipped
- Headers are used as dictionary keys for row data

Example:

```
| Name      | Email           | Age |
|-----------|-----------------|-----|
| John Doe  | john@email.com  | 30  |
| Jane Smith| jane@email.com  | 25  |
```

## Testing

Run tests:

```bash
./manage.py test importer
```

Or run specific test modules:

```bash
./manage.py test importer.tests.test_models
./manage.py test importer.tests.test_services
./manage.py test importer.tests.test_views
```

## Development

### Project Structure

```
importer/
├── __init__.py
├── admin.py              # Admin interface
├── apps.py              # App configuration
├── forms.py             # Form definitions
├── models.py            # Database models
├── services.py          # Business logic
├── urls.py              # URL routing
├── views.py             # View functions
├── migrations/          # Database migrations
├── templates/           # HTML templates
│   └── importer/
│       ├── upload.html
│       └── detail.html
├── static/              # Static files (CSS, JS)
│   └── importer/
└── tests/               # Test suite
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    └── test_views.py
```

### Adding New Features

1. Update models in `models.py`
2. Create/update migrations
3. Update admin interface in `admin.py`
4. Add business logic in `services.py`
5. Create views in `views.py`
6. Add URL patterns in `urls.py`
7. Create templates
8. Write tests

## License

Part of the Cohiva project.

