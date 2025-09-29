from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod


class CohivaAdminViewMixin:
    title = "Cohiva Administration"
    template_name = "geno/messages_unfold.html"

    def get_context_data(self, **kwargs):
        self.request.current_app = "geno"
        return super().get_context_data(
            **kwargs, **admin.site.each_context(self.request), title=self.title, model_admon=None
        )

    @classonlymethod
    def as_view(cls, **initkwargs):
        return login_required(admin.site.admin_view(super().as_view(**initkwargs)))
