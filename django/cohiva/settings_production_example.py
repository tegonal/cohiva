"""
Django custom production settings for Cohiva.

NOTE: Settings are cascaded in the following order (settings in the later files override/extend
      settings in the earlier files):

  1. settings_defaults.py (default base settings)
  2. settings.py (custom base settings)
  3. settings_production_defaults.py (default production settings)
  4. settings_production.py (custom production settings)
"""

## Load test settings and extend/overwrite with default production settings
from .settings_production_defaults import *  # noqa: F403

# Put your custom production settings here:
###########################################
