from unfold.sites import UnfoldAdminSite

from cohiva.ui import Navigation


class CohivaAdminSite(UnfoldAdminSite):
    # site_header = "Cohiva Administration"
    # site_title = "Cohiva Administration"
    # index_title = "Cohiva Administration"

    def __init__(self, name: str = "admin") -> None:
        super().__init__(name)
        self.navigation = Navigation()
