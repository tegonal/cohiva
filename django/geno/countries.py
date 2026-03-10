"""Country utilities backed by pycountry.

This centralizes ISO alpha-2 codes and helps translate between
legacy free-text values and normalized codes.
"""
from functools import lru_cache
from typing import Iterable, List, Tuple

import pycountry
import gettext
import locale

DEFAULT_COUNTRY_CODE = "CH"
PRIORITY_CODES = ["CH", "DE", "AT", "FR", "IT"]
_COUNTRY_CHOICES_CACHE = {}

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

def _current_language() -> str:
    try:
        from django.utils.translation import get_language

        lang = get_language() or ""
    except Exception:
        lang = ""
    return lang.split("-")[0].lower()


@lru_cache(maxsize=1)
def get_country_choices() -> List[Tuple[str, str]]:
    """Return country choices as (ISO alpha-2 code, localized name)."""
    lang = _current_language()
    if lang in _COUNTRY_CHOICES_CACHE:
        return _COUNTRY_CHOICES_CACHE[lang]

    # Keep the five most-used countries at the top, others stay alphabetically sorted
    priority = []
    remaining = []
    countries_trans = gettext.translation('iso3166-1', pycountry.LOCALES_DIR, languages = [lang])
    for country in pycountry.countries:
        entry = (country.alpha_2, countries_trans.gettext(country.name))
        if country.alpha_2 in PRIORITY_CODES:
            priority.append(entry)
        else:
            remaining.append(entry)
    # Preserve PRIORITY_CODES order explicitly
    priority_sorted = sorted(priority, key=lambda c: PRIORITY_CODES.index(c[0]))
    # sort remaining alphabetically by localized name (respecting german umlauts etc.)
    remaining.sort(key=lambda c: locale.strxfrm(c[1]))
    result = priority_sorted + remaining
    _COUNTRY_CHOICES_CACHE[lang] = result
    return result


def get_default_country_code() -> str:
    return DEFAULT_COUNTRY_CODE


def country_name_from_code(code: str) -> str:
    if not code:
        return ""
    match = pycountry.countries.get(alpha_2=code.upper())
    if not match:
        return ""
    lang = _current_language()
    countries_trans = gettext.translation('iso3166-1', pycountry.LOCALES_DIR, languages=[lang])
    return countries_trans.gettext(match.name)


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

