import re

import geno.settings


class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.restricted_urls = (
            re.compile(r"/admin/(.*)$"),
            re.compile(r"/geno/(.*)$"),
        )

    def __call__(self, request):
        for url in self.restricted_urls:
            if url.match(request.path):
                request.session.set_expiry(geno.settings.ADMIN_SESSION_COOKIE_AGE)
                break
        response = self.get_response(request)
        return response
