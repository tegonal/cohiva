import pprint
import importlib

from django.apps import apps
from django.contrib.admin import ModelAdmin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

#from geno.admin import AddressAdmin, ChildAdmin

class Navigation:
    def __init__(self):
        self._nav_groups = []

        # Define Navigation Structure
        g = self.add_nav_group(_("Stammdaten"))
        g.add_item("geno.Address", title=_("Adressen/Personen"))
        g.add_item("geno.Child", title=_("Kinder"))
        sg = g.add_subgroup(_("Erweiterte Konfiguration"))

    def add_nav_group(self, name):
        group = NavGroup(name)
        self._nav_groups.append(group)
        return group

    def generate_unfold_navigation(self, request):
        return [ g.generate_unfold_navigation(request) for g in self._nav_groups ]

class NavGroup:
    def __init__(self, name, depth=0):
        self._name = name
        self._items = []
        if depth > 1:
            raise ValueError(f"Depth level {depth} is not supported.")
        self._depth = depth

    def add_item(self, obj, title=None):
        item = MenuItem(obj, title=title)
        self._items.append(item)
        return item

    def add_subgroup(self, name):
        subgroup = NavGroup(name, depth=self._depth+1)
        self._items.append(subgroup)
        return subgroup

    def generate_unfold_navigation(self, request):
        ret = {
            "title": self._name,
            "separator": True,  # Top border
            "collapsible": True,  # Collapsible group of links
            "items": [ i.generate_unfold_menuitem(request) for i in self._items ]
        }
        return ret

    def generate_unfold_menuitem(self, request):
        # Subgroup
        ret = {
            "title": self._name,
            "icon": "construction",  # Supported icon set: https://fonts.google.com/icons
            "link": None,
        }
        return ret

class MenuItem:
    def __init__(self, obj, title=None, link=None, permission=None):
        self._obj = obj
        self._title = title
        self._link = link
        self._permission = permission

    def get_mytitle(self, request):
        if not self._title:
            self._title = "TEST"
            #cls = apps.get_model(self._obj)
            #self._title = str(cls)
        print("Title")
        return self._title

    def get_link(self, request):
        print("get link")
        if not self._link:
            cls = apps.get_model(self._obj)
            self._link = reverse_lazy(
                f"admin:{cls._meta.app_label}_{cls._meta.model_name}_changelist"
            )
        return self._link

    def get_permission(self, request):
        if not self._permission:
            cls = apps.get_model(self._obj)
            self._permission = request.user.has_perm(
                f"{cls._meta.app_label}.view_{cls._meta.model_name}"
            )
        return self._permission

    def generate_unfold_menuitem(self, request):
        ret = {
            "title": self._title,
            "icon": "contact_page",  # Supported icon set: https://fonts.google.com/icons
            "link": lambda request: self.get_link(request),
            "permission": lambda request: self.get_permission(request),
            # "badge": "sample_app.badge_callback",
        }
        return ret

def generate_unfold_navigation(request):
    nav = Navigation()
    return nav.generate_unfold_navigation(request)
