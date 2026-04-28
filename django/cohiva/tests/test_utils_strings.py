from django.test import TestCase

from cohiva.utils.strings import remove_secrets_from_uri


class UtilsStringsTestCase(TestCase):
    def test_remove_secrets_from_uri_no_uri(self):
        text = "Normal text without URI"
        safe_text = remove_secrets_from_uri(text)
        self.assertEqual(safe_text, text)

    def test_remove_secrets_from_uri_no_password(self):
        text = "Normal text without URI but no password https://user@host/path?bla=1 more text"
        safe_text = remove_secrets_from_uri(text)
        self.assertEqual(safe_text, text)

    def test_remove_secrets_from_uri_https(self):
        safe_text = remove_secrets_from_uri("https://user:_SECRET_@host")
        self.assertEqual(safe_text, "https://user:******@host")

    def test_remove_secrets_from_uri_https_with_text(self):
        safe_text = remove_secrets_from_uri("Text https://user:_SECRET_@host more text")
        self.assertEqual(safe_text, "Text https://user:******@host more text")

    def test_remove_secrets_from_uri_mysql(self):
        safe_text = remove_secrets_from_uri("Text mysql://user:_SECRET_@host more text")
        self.assertEqual(safe_text, "Text mysql://user:******@host more text")

    def test_remove_secrets_from_uri_multiple(self):
        text = (
            "Text https://user:_SECRET_@host more text "
            "mysql://user:_SECRET_@host/path/to/?query=1 more text"
        )
        safe_text = remove_secrets_from_uri(text)
        self.assertEqual(
            safe_text,
            (
                "Text https://user:******@host more text "
                "mysql://user:******@host/path/to/?query=1 more text"
            ),
        )
