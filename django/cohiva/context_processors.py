from django.conf import settings


def baseconfig(request):
    return {
        "COHIVA_VERSION": settings.COHIVA_VERSION,
        "COHIVA_GENO_ID": settings.GENO_ID,
        "COHIVA_BASE_URL": settings.BASE_URL,
        "COHIVA_DEBUG": settings.DEBUG,
    }
