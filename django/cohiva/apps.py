from django.contrib import admin
from django.contrib.admin import sites
from filer.apps import FilerConfig
from unfold.apps import BasicAppConfig as UnfoldAppConfig

from cohiva.admin import CohivaAdminSite


class CohivaFilerConfig(FilerConfig):
    verbose_name = "Tools - Dateiverwaltung"


class CohivaUnfoldConfig(UnfoldAppConfig):
    def ready(self):
        site = CohivaAdminSite()

        admin.site = site
        sites.site = site
