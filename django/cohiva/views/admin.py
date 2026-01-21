import copy
from enum import Enum

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod


class ResponseVariant(str, Enum):
    """Display variants for response items in templates.

    These control how response items are styled in the UI:
    - DEFAULT: Regular heading (gray/default styling)
    - INFO: Blue informational box
    - SUCCESS: Green success box
    - WARNING: Yellow warning box
    - ERROR: Red error box
    """

    DEFAULT = "default"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class CohivaAdminViewMixin:
    title = "Cohiva Administration"
    template_name = "geno/default.html"
    model_admin = None
    actions = []  # title, path, items (for dropdown), method_name (for dropdown?), icon, variant, permission_required
    action = None
    # Set this for "sub-views" that should have the same navigation (active tabs etc.)
    # as the as the "main" navigation view
    navigation_view_name = None

    def get_context_data(self, **kwargs):
        self.request.current_app = "geno"
        context = super().get_context_data(
            **kwargs,
            **admin.site.each_context(self.request),
            title=self.title,
            model_admin=self.model_admin,
            actions_list=self.get_actions(),
            navigation_view_name=self.get_navigation_view_name(),
        )
        return context

    def get_actions(self):
        if not self.actions or not isinstance(self.actions, (list, tuple)):
            return []
        actions = self.get_permitted_actions(copy.deepcopy(self.actions))
        return self.resolve_paths(actions)

    def resolve_paths(self, actions):
        for action in actions:
            if "path" in action and isinstance(action["path"], (list, tuple)):
                action["path"] = "".join([str(part) for part in action["path"]])
            if "items" in action:
                action["items"] = self.resolve_paths(action["items"])
        return actions

    def get_permitted_actions(self, actions):
        permitted_actions = []
        for action in actions:
            if "items" in action:
                action["items"] = self.get_permitted_actions(action["items"])
                if not action["items"]:
                    continue
            if "permission_required" in action:
                if isinstance(action["permission_required"], (list, tuple)):
                    if self.request.user.has_perms(action["permission_required"]):
                        permitted_actions.append(action)
                else:
                    if self.request.user.has_perm(action["permission_required"]):
                        permitted_actions.append(action)
            else:
                permitted_actions.append(action)
        return permitted_actions

    def get_navigation_view_name(self):
        if self.navigation_view_name:
            return self.navigation_view_name
        return f"{self.__class__.__module__}.{self.__class__.__name__}"

    @staticmethod
    def make_response_item(info, objects=None, variant=None):
        """Helper to create standardized response items.

        Args:
            info: Main message text (required)
            objects: List of sub-items to display (optional)
            variant: ResponseVariant enum for styling (optional, defaults to DEFAULT)

        Returns:
            dict: Response item with keys 'info', 'objects', and 'variant'

        Example:
            response = [
                make_response_item(
                    "Successfully saved",
                    objects=["Item 1", "Item 2"],
                    variant=ResponseVariant.SUCCESS
                )
            ]
        """
        return {
            "info": info,
            "objects": objects or [],
            "variant": variant.value if variant else ResponseVariant.DEFAULT.value,
        }

    @classonlymethod
    def as_view(cls, **initkwargs):
        return login_required(admin.site.admin_view(super().as_view(**initkwargs)))
