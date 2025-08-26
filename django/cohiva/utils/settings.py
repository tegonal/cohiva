from django.conf import settings


def get_default_email():
    return settings.SERVER_EMAIL


def get_default_formal_choice():
    if settings.GENO_FORMAL:
        return "Sie"
    else:
        return "Du"


def get_default_mail_footer():
    if settings.GENO_FORMAL:
        footer = "Freundliche Grüsse"
    else:
        footer = "Herzliche Grüsse"
    footer += f"\n{settings.GENO_NAME}\n\n-- \n{settings.SERVER_EMAIL}\n{settings.GENO_WEBSITE}\n"
    return footer


def get_default_app_sender():
    return f'"{settings.COHIVA_SITE_NICKNAME}-App" <{settings.GENO_DEFAULT_EMAIL}>'
