"""
Django system checks for the geno app.

Validates configuration and setup requirements, particularly middleware ordering.
"""

from django.conf import settings
from django.core.checks import Error, Warning, register


@register()
def check_middleware_ordering(app_configs, **kwargs):
    """
    Validate that custom middleware is positioned correctly in MIDDLEWARE.

    Checks:
    - LoginRedirectMiddleware must come after AuthenticationMiddleware
    - SessionExpiryMiddleware should come before CommonMiddleware
    - LocaleMiddleware must be between SessionMiddleware and CommonMiddleware
    """
    errors = []
    middleware = getattr(settings, "MIDDLEWARE", [])

    # Convert to list of class paths for easier checking
    middleware_list = list(middleware)

    # Check 1: LoginRedirectMiddleware ordering
    login_redirect = "geno.middleware.LoginRedirectMiddleware"
    auth_middleware = "django.contrib.auth.middleware.AuthenticationMiddleware"

    if login_redirect in middleware_list:
        try:
            login_redirect_idx = middleware_list.index(login_redirect)
            auth_middleware_idx = middleware_list.index(auth_middleware)

            if login_redirect_idx <= auth_middleware_idx:
                errors.append(
                    Error(
                        "LoginRedirectMiddleware is positioned incorrectly",
                        hint=(
                            f"LoginRedirectMiddleware (position {login_redirect_idx}) must come "
                            f"AFTER AuthenticationMiddleware (position {auth_middleware_idx}). "
                            "LoginRedirectMiddleware processes responses from authentication "
                            "checks and needs to run after authentication is complete."
                        ),
                        id="geno.E001",
                    )
                )
        except ValueError:
            # One of the middleware is not in the list
            if auth_middleware not in middleware_list:
                errors.append(
                    Warning(
                        "AuthenticationMiddleware not found",
                        hint=(
                            "LoginRedirectMiddleware is present but AuthenticationMiddleware "
                            "is not in MIDDLEWARE. LoginRedirectMiddleware requires "
                            "AuthenticationMiddleware to function correctly."
                        ),
                        id="geno.W001",
                    )
                )

    # Check 2: SessionExpiryMiddleware ordering
    session_expiry = "geno.middleware.SessionExpiryMiddleware"
    common_middleware = "django.middleware.common.CommonMiddleware"

    if session_expiry in middleware_list and common_middleware in middleware_list:
        try:
            session_expiry_idx = middleware_list.index(session_expiry)
            common_middleware_idx = middleware_list.index(common_middleware)

            if session_expiry_idx >= common_middleware_idx:
                errors.append(
                    Warning(
                        "SessionExpiryMiddleware positioned after CommonMiddleware",
                        hint=(
                            f"SessionExpiryMiddleware (position {session_expiry_idx}) should "
                            f"come BEFORE CommonMiddleware (position {common_middleware_idx}) "
                            "to ensure session expiry is set before common request processing."
                        ),
                        id="geno.W002",
                    )
                )
        except ValueError:
            pass

    # Check 3: LocaleMiddleware ordering
    locale_middleware = "django.middleware.locale.LocaleMiddleware"
    session_middleware = "django.contrib.sessions.middleware.SessionMiddleware"

    if locale_middleware in middleware_list:
        try:
            locale_idx = middleware_list.index(locale_middleware)
            session_idx = middleware_list.index(session_middleware)
            common_idx = middleware_list.index(common_middleware)

            if locale_idx <= session_idx:
                errors.append(
                    Error(
                        "LocaleMiddleware positioned before SessionMiddleware",
                        hint=(
                            f"LocaleMiddleware (position {locale_idx}) must come AFTER "
                            f"SessionMiddleware (position {session_idx}). LocaleMiddleware "
                            "needs access to session data to determine user language preferences."
                        ),
                        id="geno.E002",
                    )
                )

            if locale_idx >= common_idx:
                errors.append(
                    Error(
                        "LocaleMiddleware positioned after CommonMiddleware",
                        hint=(
                            f"LocaleMiddleware (position {locale_idx}) must come BEFORE "
                            f"CommonMiddleware (position {common_idx}). LocaleMiddleware "
                            "needs to process language preferences before URL resolution."
                        ),
                        id="geno.E003",
                    )
                )
        except ValueError:
            pass

    return errors
