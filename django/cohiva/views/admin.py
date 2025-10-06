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
            actions_list=self.actions,
            cohiva_view_name=f"{self.__class__.__module__}.{self.__class__.__name__}",
        )
        return context

    @classonlymethod
    def as_view(cls, **initkwargs):
        return login_required(admin.site.admin_view(super().as_view(**initkwargs)))
