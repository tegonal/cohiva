import logging

logger = logging.getLogger(__name__)


class RequestDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.error(f"REQUEST: {request.method} {request.path}")
        logger.error(f"HOST: {request.META.get('HTTP_HOST', 'NO_HOST')}")
        logger.error(f"USER_AGENT: {request.META.get('HTTP_USER_AGENT', 'NO_UA')}")
        logger.error(f"REMOTE_ADDR: {request.META.get('REMOTE_ADDR', 'NO_ADDR')}")

        response = self.get_response(request)

        logger.error(f"RESPONSE: {response.status_code}")
        return response
