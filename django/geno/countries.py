"""Country utilities backed by pycountry.

This centralizes ISO alpha-2 codes and helps translate between
legacy free-text values and normalized codes.
"""
from functools import lru_cache
from typing import Iterable, List, Tuple

import pycountry

DEFAULT_COUNTRY_CODE = "CH"

# Map common legacy spellings to ISO alpha-2 codes.
LEGACY_COUNTRY_MAP = {
    "schweiz": "CH",
    "suisse": "CH",
    "svizzera": "CH",
    "svizra": "CH",
    "switzerland": "CH",
    "fürstentum liechtenstein": "LI",
    "fuerstentum liechtenstein": "LI",
    "liechtenstein": "LI",
    "deutschland": "DE",
    "germany": "DE",
    "österreich": "AT",
    "oesterreich": "AT",
    "austria": "AT",
    "frankreich": "FR",
    "france": "FR",
    "italien": "IT",
    "italia": "IT",
    "italy": "IT",
    "spanien": "ES",
    "españa": "ES",
    "espana": "ES",
    "spain": "ES",
    "brasilien": "BR",
    "brazil": "BR",
}


def _sorted_countries() -> Iterable:
    return sorted(pycountry.countries, key=lambda c: c.name)


@lru_cache(maxsize=1)
def get_country_choices() -> List[Tuple[str, str]]:
    """Return country choices as (ISO alpha-2 code, name)."""
    return [(country.alpha_2, country.name) for country in _sorted_countries()]


def get_default_country_code() -> str:
    return DEFAULT_COUNTRY_CODE


def country_name_from_code(code: str) -> str:
    if not code:
        return ""
    match = pycountry.countries.get(alpha_2=code.upper())
    return match.name if match else ""


def normalize_country_code(value: str) -> str:
    """Normalize free-text or ISO value to a valid ISO alpha-2 code.

    Returns an empty string if no suitable code can be found.
    """
    if not value:
        return ""

    candidate = value.strip()
    if not candidate:
        return ""

    upper_candidate = candidate.upper()
    if len(upper_candidate) == 2 and pycountry.countries.get(alpha_2=upper_candidate):
        return upper_candidate

    legacy = LEGACY_COUNTRY_MAP.get(candidate.lower())
    if legacy:
        return legacy

    try:
        match = pycountry.countries.search_fuzzy(candidate)[0]
    except LookupError:
        return ""
    return match.alpha_2

