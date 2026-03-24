from types import SimpleNamespace
from unittest.mock import Mock, patch

import pycountry
from django.test import SimpleTestCase

from cohiva.utils import countries


class DummyTranslation:
    def __init__(self, mapping):
        self.mapping = mapping

    def gettext(self, text):
        return self.mapping.get(text, text)


class CountriesTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        countries.get_country_choices.cache_clear()
        countries._COUNTRY_CHOICES_CACHE.clear()

    def tearDown(self):
        countries.get_country_choices.cache_clear()
        countries._COUNTRY_CHOICES_CACHE.clear()
        super().tearDown()

    def test_get_country_choices_prioritizes_and_localizes(self):
        fake_countries = [
            SimpleNamespace(alpha_2="US", name="United States"),
            SimpleNamespace(alpha_2="DE", name="Germany"),
            SimpleNamespace(alpha_2="FR", name="France"),
            SimpleNamespace(alpha_2="CH", name="Switzerland"),
        ]
        translation = DummyTranslation(
            {
                "Germany": "Deutschland",
                "France": "Frankreich",
                "Switzerland": "Schweiz",
                "United States": "Vereinigte Staaten",
            }
        )
        with (
            patch("cohiva.utils.countries.pycountry.countries", fake_countries),
            patch("cohiva.utils.countries._current_language", return_value="de"),
            patch("cohiva.utils.countries.locale.strxfrm", side_effect=lambda value: value),
            patch(
                "cohiva.utils.countries.gettext.translation", return_value=translation
            ) as translation_mock,
        ):
            choices = countries.get_country_choices()

        self.assertEqual(
            choices,
            [
                ("CH", "Schweiz"),
                ("DE", "Deutschland"),
                ("FR", "Frankreich"),
                ("US", "Vereinigte Staaten"),
            ],
        )
        translation_mock.assert_called_once_with(
            "iso3166-1", pycountry.LOCALES_DIR, languages=["de"]
        )

    def test_get_country_choices_caches_per_language(self):
        fake_countries = [SimpleNamespace(alpha_2="DE", name="Germany")]
        translation_mock = Mock(return_value=DummyTranslation({"Germany": "Deutschland"}))
        with (
            patch("cohiva.utils.countries.pycountry.countries", fake_countries),
            patch("cohiva.utils.countries._current_language", return_value="de"),
            patch("cohiva.utils.countries.locale.strxfrm", side_effect=lambda value: value),
            patch("cohiva.utils.countries.gettext.translation", translation_mock),
        ):
            first = countries.get_country_choices()
            second = countries.get_country_choices()

        self.assertIs(first, second)
        translation_mock.assert_called_once()

        countries.get_country_choices.cache_clear()
        countries._COUNTRY_CHOICES_CACHE.clear()

        translation_fr = Mock(return_value=DummyTranslation({"Germany": "Allemagne"}))
        with (
            patch("cohiva.utils.countries.pycountry.countries", fake_countries),
            patch("cohiva.utils.countries._current_language", return_value="fr"),
            patch("cohiva.utils.countries.locale.strxfrm", side_effect=lambda value: value),
            patch("cohiva.utils.countries.gettext.translation", translation_fr),
        ):
            french = countries.get_country_choices()

        translation_fr.assert_called_once()
        self.assertIn(("DE", "Allemagne"), french)

    def test_country_name_from_code_returns_localized_name(self):
        translation = DummyTranslation({"Germany": "Deutschland"})
        with (
            patch("cohiva.utils.countries._current_language", return_value="de"),
            patch(
                "cohiva.utils.countries.gettext.translation", return_value=translation
            ) as translation_mock,
            patch(
                "cohiva.utils.countries.pycountry.countries.get",
                return_value=SimpleNamespace(name="Germany"),
            ),
        ):
            self.assertEqual(countries.country_name_from_code("de"), "Deutschland")
        translation_mock.assert_called_once()

    def test_country_name_from_code_handles_missing(self):
        with (
            patch("cohiva.utils.countries._current_language", return_value="de"),
            patch("cohiva.utils.countries.gettext.translation") as translation_mock,
            patch("cohiva.utils.countries.pycountry.countries.get", return_value=None),
        ):
            self.assertEqual(countries.country_name_from_code(""), "")
            self.assertEqual(countries.country_name_from_code("zz"), "")
        translation_mock.assert_not_called()

    def test_normalize_country_code_handles_iso_legacy_and_fuzzy(self):
        def fake_get(alpha_2=None):
            mapping = {"CH": SimpleNamespace(alpha_2="CH"), "DE": SimpleNamespace(alpha_2="DE")}
            return mapping.get((alpha_2 or "").upper())

        def fake_search_fuzzy(value):
            if value == "Brasil":
                return [SimpleNamespace(alpha_2="BR")]
            raise LookupError()

        with (
            patch("cohiva.utils.countries.pycountry.countries.get", side_effect=fake_get),
            patch(
                "cohiva.utils.countries.pycountry.countries.search_fuzzy",
                side_effect=fake_search_fuzzy,
            ),
        ):
            self.assertEqual(countries.normalize_country_code(""), "")
            self.assertEqual(countries.normalize_country_code("   "), "")
            self.assertEqual(countries.normalize_country_code("ch"), "CH")
            self.assertEqual(countries.normalize_country_code("Schweiz"), "CH")
            self.assertEqual(countries.normalize_country_code("Brasil"), "BR")
            self.assertEqual(countries.normalize_country_code("zz"), "")

    def test_get_default_country_code(self):
        self.assertEqual(countries.get_default_country_code(), countries.DEFAULT_COUNTRY_CODE)
