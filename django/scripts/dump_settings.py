#!/usr/bin/env python3

import os
from datetime import datetime
from pprint import pprint

output_dir = "./dump/settings"


def dump_variables(label, timestamp):
    if label == "test":
        from cohiva import settings as data
    elif label == "production":
        from cohiva import settings_production as data
    dump = {}
    if hasattr(data, "__all__"):
        for name in data.__all__:
            dump[name] = getattr(data, name)
    else:
        for name in dir(data):
            if not name.startswith("_"):
                dump[name] = getattr(data, name)

    dumpfile = f"{output_dir}/settings-{label}{timestamp}.dump"
    with open(dumpfile, "w") as output_file:
        pprint(dump, output_file)
        print(f"Wrote current {label} settings to {dumpfile}.")


timestamp = datetime.now().strftime("_%Y%m%d-%H%M%S")
os.makedirs(output_dir, mode=0o700, exist_ok=True)
dump_variables("test", timestamp)
dump_variables("production", timestamp)
