# Importer App

Import data from Excel files into Cohiva.

## Quick Links

- **[QUICKSTART.md](QUICKSTART.md)** - Setup and basic usage
- **[MEMBER_ADDRESS_IMPORT.md](MEMBER_ADDRESS_IMPORT.md)** - Member/address import guide

## Features

- Upload Excel files (.xlsx, .xls, max 10MB)
- Track import jobs (pending → processing → completed/failed)
- Row-level error tracking
- Admin interface for monitoring
- Extensible for custom import logic

## Usage

### Member/Address Import
Navigate to `/importer/upload/member-address/`

Import members and addresses from 47-column Excel files.

### General Import
Navigate to `/importer/upload/`

Basic Excel import (requires custom importer implementation).

### Admin
Navigate to `/admin/importer/`

View all import jobs, records, and error messages.

## Testing

```bash
./manage.py test importer
```


## License

Part of the Cohiva project.

