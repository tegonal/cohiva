from django.conf import settings


def featurelist(request):
    features = []
    if "portal" in settings.INSTALLED_APPS:
        features.append("portal")
    return {"FEATURES": features, "DEMO": settings.DEMO}
