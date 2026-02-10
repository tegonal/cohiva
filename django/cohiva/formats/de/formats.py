"""
This module kept the Swiss German formats under the "de" path for historical
reasons. It now delegates to the canonical `de_ch` module so both
`cohiva.formats.de` and `cohiva.formats.de_ch` work.
"""

# Import everything from the new de_ch module to preserve behavior.
from cohiva.formats.de_ch.formats import *  # noqa: F401,F403
