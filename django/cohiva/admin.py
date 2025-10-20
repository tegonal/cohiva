from django.conf import settings
from unfold.sites import UnfoldAdminSite

from cohiva.ui import Navigation


class CohivaAdminSite(UnfoldAdminSite):
    # site_header = "Cohiva Administration"
    # site_title = "Cohiva Administration"
    # index_title = "Cohiva Administration"

    def __init__(self, name: str = "admin") -> None:
        super().__init__(name)
        self.navigation = Navigation()

    def get_environment(self):
        if settings.DEBUG:
            return ("TEST",)
        if settings.DEMO:
            return ("DEMO",)
        return None

    def get_environment_title(self):
        if settings.DEBUG:
            return "[TEST]"
        if settings.DEMO:
            return "[DEMO]"
        return None
