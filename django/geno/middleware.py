import logging
import re
from http import HTTPStatus
from urllib.parse import urlparse, urlunparse

import geno.settings

logger = logging.getLogger(__name__)


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


class LoginRedirectMiddleware:
    """
    Middleware to redirect login requests to the appropriate login page
    based on the URL path that triggered the login requirement.

    - /admin/* and /geno/* URLs redirect to /admin/login/
    - /portal/* URLs redirect to /portal/login/
    - All other URLs use the default LOGIN_URL setting

    IMPORTANT: This middleware must be placed AFTER AuthenticationMiddleware
    in the MIDDLEWARE setting, as it needs to process responses from
    authentication checks.
    """

    # Login URL paths (without domain/protocol)
    ADMIN_LOGIN_PATH = '/admin/login/'
    PORTAL_LOGIN_PATH = '/portal/login/'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only process 302 Found redirects (login redirects)
        if response.status_code != HTTPStatus.FOUND:
            return response

        location = response.get('Location', '')
        if not location:
            return response

        # Parse the redirect URL
        try:
            parsed_location = urlparse(location)
        except ValueError:
            # Malformed URL, leave it alone
            logger.warning(f"LoginRedirectMiddleware: Malformed redirect URL: {location}")
            return response

        # Check if this is a redirect to a login page
        redirect_path = parsed_location.path

        # Determine the correct login path based on original request path
        correct_login_path = None

        if request.path.startswith('/admin/') or request.path.startswith('/geno/'):
            # Admin/geno paths should go to admin login
            if redirect_path == self.PORTAL_LOGIN_PATH:
                correct_login_path = self.ADMIN_LOGIN_PATH
        elif request.path.startswith('/portal/'):
            # Portal paths should go to portal login
            if redirect_path == self.ADMIN_LOGIN_PATH:
                correct_login_path = self.PORTAL_LOGIN_PATH

        # If we need to change the login path, reconstruct the URL
        if correct_login_path:
            new_parsed = parsed_location._replace(path=correct_login_path)
            new_location = urlunparse(new_parsed)
            response['Location'] = new_location

            logger.debug(
                f"LoginRedirectMiddleware: Redirected {request.path} from "
                f"{redirect_path} to {correct_login_path}"
            )

        return response
