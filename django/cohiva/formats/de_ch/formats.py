"""
Custom date/time format overrides for Swiss German (de-ch).

This file provides Swiss German formats for Django when
`LANGUAGE_CODE` is set to 'de-ch'. It mirrors the previous
`cohiva/formats/de/formats.py` behavior but uses the
module name expected for regional code: `de_ch`.
"""

# Import Django's de_CH formats as base
from django.conf.locale.de_CH.formats import *  # noqa: F403

# Override DATE_FORMAT to use shorter format (d.m.Y instead of j. F Y)
DATE_FORMAT = "d.m.Y"
DATETIME_FORMAT = "d.m.Y H:i"

# Add ISO format as additional input option
DATE_INPUT_FORMATS = [
    "%d.%m.%Y",  # Swiss format: 25.12.2024
    "%d.%m.%y",  # Swiss short: 25.12.24
    "%Y-%m-%d",  # ISO format: 2024-12-25 (added)
]

DATETIME_INPUT_FORMATS = [
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y %H:%M:%S.%f",
    "%d.%m.%Y %H:%M",
    "%Y-%m-%d %H:%M:%S",  # ISO format (added)
    "%Y-%m-%d %H:%M",  # ISO format (added)
]
THOUSAND_SEPARATOR = "'"
DECIMAL_SEPARATOR = "."
NUMBER_GROUPING = 3

