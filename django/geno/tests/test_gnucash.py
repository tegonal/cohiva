from geno.billing import get_book

from .base import BaseTestCase


class TestGnucash(BaseTestCase):
    def test_open_book(self):
        msg = []
        book = get_book(msg)
        self.assertIsNotNone(book, " ".join(msg))

    ## TODO: Test create_qrbill after moving send-mail code to separate util class

    ## TODO: Test send mail with recipients that include commas, parentheses and utf8 chars
    # https://github.com/anymail/django-anymail/issues/369
