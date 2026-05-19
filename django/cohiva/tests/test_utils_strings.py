from django.test import TestCase

from cohiva.utils.strings import sanitize_log_message


class UtilsStringsTestCase(TestCase):
    def test_sanitize_log_message_no_uri(self):
        text = "Normal text without URI"
        safe_text = sanitize_log_message(text)
        self.assertEqual(safe_text, text)

    def test_sanitize_log_message_uri_without_password(self):
        text = "Normal text without URI but no password https://user@host/path?bla=1 more text"
        safe_text = sanitize_log_message(text)
        self.assertEqual(safe_text, text)

    def test_sanitize_log_message_uri_https(self):
        safe_text = sanitize_log_message("https://user:_SECRET_@host")
        self.assertEqual(safe_text, "https://user:******@host")

    def test_sanitize_log_message_uri_https_with_text(self):
        safe_text = sanitize_log_message("Text https://user:_SECRET_@host more text")
        self.assertEqual(safe_text, "Text https://user:******@host more text")

    def test_sanitize_log_message_uri_mysql(self):
        safe_text = sanitize_log_message("Text mysql://user:_SECRET_@host more text")
        self.assertEqual(safe_text, "Text mysql://user:******@host more text")

    def test_sanitize_log_message_multiple_uris(self):
        text = (
            "Text https://user:_SECRET_@host more text "
            "mysql://user:_SECRET_@host/path/to/?query=1 more text"
        )
        safe_text = sanitize_log_message(text)
        self.assertEqual(
            safe_text,
            (
                "Text https://user:******@host more text "
                "mysql://user:******@host/path/to/?query=1 more text"
            ),
        )
