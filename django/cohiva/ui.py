from django.apps import apps
from django.conf import settings
from django.urls import NoReverseMatch, Resolver404, resolve, reverse


class Navigation:
    def __init__(self):
        self._nav_groups = []
        for item in settings.COHIVA_ADMIN_NAVIGATION:
            self.add_nav_group(item)

    def add_nav_group(self, obj):
        group = NavGroup(obj.get("name", "Group"), icon=obj.get("icon", None))
        for item in obj.get("items", []):
            if item.get("type", None) == "subgroup":
                group.add_subgroup(item)
            elif item.get("type", None) == "tabgroup":
                group.add_subgroup(item, tabs=True)
            else:
                group.add_item(item)
        self._nav_groups.append(group)

    def generate_unfold_navigation(self, request):
        nav = [
            {
                # "title": "Quicklinks",
                "items": [
                    {
                        "title": "Startseite",
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse("admin:index"),
                        "items": [],
                        # "badge": "sample_app.badge_callback",
                        # "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
        ]
        nav.extend([g.generate_unfold_navigation(request) for g in self._nav_groups])
        return nav

    def generate_unfold_tabs(self, request):
        ret = []
        for group in self._nav_groups:
            ret.extend(group.generate_unfold_tabs(request))
        return ret


class NavGroup:
    def __init__(self, name, depth=0, icon=None, tabs=False):
        self._name = name
        self._icon = icon
        self._items = []
        self._tabs = tabs
        if depth > 1:
            raise ValueError(f"Depth level {depth} is not supported.")
        self._depth = depth

    def add_item(self, obj):
        item = MenuItem(obj)
        self._items.append(item)

    def add_subgroup(self, obj, tabs=False):
        subgroup = NavGroup(
            obj.get("name", None),
            depth=self._depth + 1,
            icon=obj.get("icon", None),
            tabs=tabs,
        )
        for item in obj.get("items", []):
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
        if self._tabs and len(self._items):
            ## For tab groups we take the first tab as default for the menu item
            ret = self._items[0].generate_unfold_menuitem(request)
            if self._name:
                ret["title"] = self._name
            if self._icon:
                ret["icon"] = self._icon
            return ret
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

    def generate_unfold_tabs(self, request):
        if self._tabs:
            tabs = {"models": [], "items": []}
            for item in self._items:
                tabs["models"].append(item.get_tab_model())
                tabs["items"].append(item.generate_unfold_menuitem(request))
            return [tabs]
        ret = []
        for group in self._items:
            if isinstance(group, NavGroup):
                tabs = group.generate_unfold_tabs(request)
                if tabs:
                    ret.extend(tabs)
        return ret


class MenuItem:
    def __init__(self, obj):
        self._type = obj.get("type")
        self._value = obj.get("value")
        self._app_label = obj.get("app", None)
        self._title = obj.get("name", None)
        self._icon = obj.get("icon", None)
        self._permission = obj.get("permission", None)
        self._cls = None

    def determine_missing_values(self):
        if self._type == "model":
            if not self._cls:
                try:
                    if self._app_label:
                        self._cls = apps.get_model(self._app_label, self._value)
                    else:
                        self._cls = apps.get_model(self._value)
                except LookupError:
                    return
            if not self._permission:
                self._permission = f"{self._cls._meta.app_label}.view_{self._cls._meta.model_name}"
            if not self._title:
                self._title = self._cls._meta.verbose_name_plural
        elif self._type == "view":
            if not self._cls:
                try:
                    view = resolve(reverse(self._value)).func
                except (NoReverseMatch, Resolver404):
                    view = None
                if hasattr(view, "view_class"):
                    self._cls = view.view_class
            if self._cls:
                if not self._permission and hasattr(self._cls, "permission_required"):
                    self._permission = self._cls.permission_required
                if not self._title and hasattr(self._cls, "title"):
                    self._title = self._cls.title

    def get_title(self):
        if not self._title:
            return "UNKNOWN"
        return self._title

    def get_link(self):
        if self._type == "model":
            if self._cls:
                link = reverse(
                    f"admin:{self._cls._meta.app_label}_{self._cls._meta.model_name}_changelist"
                )
            else:
                return None
        elif self._type == "view":
            try:
                link = reverse(self._value)
            except NoReverseMatch:
                link = ""
        elif self._type == "link":
            link = self._value
        else:
            raise ValueError(f"Unknown type: {self._type}")
        return link

    def get_permission(self, request):
        if self._permission:
            if isinstance(self._permission, (list, tuple)):
                return request.user.has_perms(self._permission)
            return request.user.has_perm(self._permission)
        return False

    def generate_unfold_menuitem(self, request):
        self.determine_missing_values()
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

    def get_tab_model(self):
        self.determine_missing_values()
        if self._cls:
            if self._type == "model":
                return f"{self._cls._meta.app_label}.{self._cls._meta.model_name}"
            else:
                return f"{self._cls.__module__}.{self._cls.__name__}"
        return None
