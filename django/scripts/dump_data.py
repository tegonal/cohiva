#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime

output_dir = "./dump/data"

apps = [
    {
        "name": "geno",
        "models": [
            # {'name': 'Address' },
            # {'name': 'Child' },
            # {'name': 'Building' },
            # {'name': 'Tenant' },
            # {'name': 'Member' },
            # {'name': 'MemberAttributeType' },
            # {'name': 'MemberAttribute' },
            # {'name': 'ShareType' },
            # {'name': 'Share' },
            # {'name': 'DocumentType' },
            # {'name': 'Document' },
            # {'name': 'RegistrationEvent' },
            # {'name': 'RegistrationSlot' },
            # {'name': 'Registration' },
            # {'name': 'RentalUnit' },
            # {'name': 'Contract' },
            # {'name': 'InvoiceCategory' },
            # {'name': 'Invoice' },
            # {'name': 'LookupTable' },
            # {'name': 'GenericAttribute' },
            # {'name': 'ContentTemplateOption' },
            # {'name': 'ContentTemplate' },
        ],
    },
    {
        "name": "report",
        "models": [
            # {'name': 'Report' },
            # {'name': 'ReportType' },
            # {'name': 'ReportInputField' },
            # {'name': 'ReportInputData' },
        ],
    },
    {
        "name": "reservation",
        "models": [
            # {"name": "ReportType"},
            # {"name": "ReportCategory"}
        ],
    },
]


def dump_model(app, model, timestamp):
    label = f"{app}_{model}"
    dumpfile = f"{output_dir}/{label}{timestamp}.json"
    subprocess.run(["./manage.py", "dumpdata", f"{app}.{model}", "-o", dumpfile, "--indent", "2"])
    print(f"Wrote {label} data to {dumpfile}.")


timestamp = datetime.now().strftime("_%Y%m%d-%H%M%S")
os.makedirs(output_dir, mode=0o700, exist_ok=True)
for app in apps:
    for model in app["models"]:
        dump_model(app["name"], model["name"], timestamp)
