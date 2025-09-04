from django.conf import settings
from django.shortcuts import redirect


class SecondaryPortalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.get_host() == settings.PORTAL_SECONDARY_HOST:
            ## Restrict URIs to /portal
            if not (
                request.path.startswith("/portal")
                or request.path.startswith("/o/")
                or request.path.startswith("//o/")
            ):
                return redirect("/portal/")

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
