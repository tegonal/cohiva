import copy

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod


class CohivaAdminViewMixin:
    title = "Cohiva Administration"
    template_name = "geno/messages.html"
    model_admin = None
    actions = []

    def get_context_data(self, **kwargs):
        self.request.current_app = "geno"
        context = super().get_context_data(
            **kwargs,
            **admin.site.each_context(self.request),
            title=self.title,
            model_admin=self.model_admin,
            actions_list=self.get_actions(),
            cohiva_view_name=f"{self.__class__.__module__}.{self.__class__.__name__}",
        )
        return context

    def get_actions(self):
        if not self.actions or not isinstance(self.actions, (list, tuple)):
            return []
        return self.get_permitted_actions(copy.deepcopy(self.actions))

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

    @classonlymethod
    def as_view(cls, **initkwargs):
        return login_required(admin.site.admin_view(super().as_view(**initkwargs)))
