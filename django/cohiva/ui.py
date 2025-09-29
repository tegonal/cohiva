from django.apps import apps
from django.conf import settings
from django.urls import reverse_lazy

# from geno.admin import AddressAdmin, ChildAdmin


class Navigation:
    def __init__(self):
        self._nav_groups = []
        for item in settings.COHIVA_ADMIN_NAVIGATION:
            self.add_nav_group(item)

    def add_nav_group(self, obj):
        group = NavGroup(obj["name"], icon=obj.get("icon", None))
        for item in obj["items"]:
            if item["type"] == "subgroup":
                group.add_subgroup(item)
            else:
                group.add_item(item)
        self._nav_groups.append(group)

    def generate_unfold_navigation(self, request):
        return [g.generate_unfold_navigation(request) for g in self._nav_groups]


class NavGroup:
    def __init__(self, name, depth=0, icon=None):
        self._name = name
        self._icon = icon
        self._items = []
        if depth > 1:
            raise ValueError(f"Depth level {depth} is not supported.")
        self._depth = depth

    def add_item(self, obj):
        item = MenuItem(obj)
        self._items.append(item)

    def add_subgroup(self, obj):
        subgroup = NavGroup(obj["name"], depth=self._depth + 1, icon=obj.get("icon", None))
        for item in obj["items"]:
            subgroup.add_item(item)
        self._items.append(subgroup)

    def generate_unfold_navigation(self, request):
        ret = {
            "title": self._name,
            "separator": True,  # Top border
            "collapsible": True,  # Collapsible group of links
            "items": [i.generate_unfold_menuitem(request) for i in self._items],
        }
        return ret

    def generate_unfold_menuitem(self, request):  # Subgroup
        ret = {
            "title": self._name,
            "link": None,
            "collapsible": True,
            "is_subgroup": True,
            "items": [i.generate_unfold_menuitem(request) for i in self._items],
        }
        if self._icon:
            ret["icon"] = self._icon
        return ret


class MenuItem:
    def __init__(self, obj):
        self._type = obj.get("type")
        self._value = obj.get("value")
        self._title = obj.get("name", None)
        self._icon = obj.get("icon", None)
        self._permission = obj.get("permission", None)

    def get_title(self):
        if not self._title:
            return "UNKNOWN"
        return self._title

    def get_link(self):
        if self._type == "model":
            cls = apps.get_model(self._value)
            link = reverse_lazy(f"admin:{cls._meta.app_label}_{cls._meta.model_name}_changelist")
        elif self._type == "custom":
            link = reverse_lazy(self._value)
        else:
            raise ValueError(f"Unknown type: {self._type}")
        return link

    def get_permission(self, request):
        if self._permission:
            return request.user.has_perm(self._permission)
        if self._type == "model":
            cls = apps.get_model(self._value)
            return request.user.has_perm(f"{cls._meta.app_label}.view_{cls._meta.model_name}")
        return False

    def generate_unfold_menuitem(self, request):
        ret = {
            "title": self._title,
            "link": self.get_link(),
            # "link_callback",
            "permission": lambda req: self.get_permission(req),
            # "badge": "sample_app.badge_callback",
            # "active:"  ## can be value or callable / callback-str
            #            ## if not set it's derived from request URL/query.
        }
        if self._icon:
            ret["icon"] = self._icon  # Supported icon set: https://fonts.google.com/icons
        return ret
