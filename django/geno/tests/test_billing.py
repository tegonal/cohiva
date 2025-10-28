from .base import BaseTestCase


class TestBilling(BaseTestCase):
    pass
    ## TODO: Add tests ;)

    ## TODO: Test create_qrbill after moving send-mail code to separate util class

    ## TODO: Test send mail with recipients that include commas, parentheses and utf8 chars
    # https://github.com/anymail/django-anymail/issues/369
