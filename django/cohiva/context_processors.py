from django.conf import settings

from cohiva.version import git_commit, git_tag


def baseconfig(request):
    return {
        "COHIVA_VERSION": settings.COHIVA_VERSION,
        "COHIVA_GIT_TAG": git_tag,
        "COHIVA_GIT_COMMIT": git_commit,
        "COHIVA_GENO_ID": settings.GENO_ID,
        "COHIVA_BASE_URL": settings.BASE_URL,
        "COHIVA_DEBUG": settings.DEBUG,
    }
