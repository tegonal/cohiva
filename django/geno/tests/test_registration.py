from django.conf import settings

import geno.tests.data as testdata
from geno.models import Registration

from .base import BaseTestCase


class TestRegistrationForm(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        testdata.create_registrationevents(cls)
        cls.form_url = f"/anmeldung/{cls.registrationevents[0].id}/"

    def test_form_submission(self):
        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertInHTML("Public Test-Registration, 10 places", content)
        self.assertInHTML("<h3>Ich melde mich für folgenden Termin an:</h3>", content)
        self.assertInHTML('<input type="submit" value="Anmeldung abschicken">', content)
        datestr = self.registrationslots[0].get_slot_text()
        self.assertIn(datestr + " (noch 10 Plätze frei)", content)

        post_data = {
            "reg_id": f"{self.registrationevents[0].id}",
            "slot": f"{self.registrationslots[0].id}",
            "first_name": "Hans",
            "name": "Muster",
            "email": "hans.muster@example.com",
        }

        prev_geno_formal = settings.GENO_FORMAL
        settings.GENO_FORMAL = False
        response = self.client.post(self.form_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Eine Bestätigung wurde an hans.muster@example.com geschickt.",
            response.content.decode(),
        )

        ## Don't allow two registraionts
        response = self.client.post(self.form_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "Eine Bestätigung wurde an hans.muster@example.com geschickt.",
            response.content.decode(),
        )
        self.assertIn(
            "Es gibt bereits eine Anmeldung mit dieser Email-Adresse!", response.content.decode()
        )

        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(datestr + " (noch 9 Plätze frei)", response.content.decode())

        settings.GENO_FORMAL = True
        post_data["first_name"] = "Rosa"
        post_data["email"] = "rosa.muster@example.com"
        response = self.client.post(self.form_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Eine Bestätigung wurde an rosa.muster@example.com geschickt.",
            response.content.decode(),
        )

        expected_msg = (
            "Hallo Hans\n\nDu hast dich für den Anlass «Public Test",
            "Hallo Rosa Muster\n\nSie haben sich für den Anlass «Public Test",
        )
        self.assertEmailSent(
            2, 2 * ("Anmeldung Public Test-Registration, 10 places",), expected_msg
        )

        reg = Registration.objects.all()
        self.assertEqual(2, reg.count())
        self.assertEqual("Hans", reg[0].first_name)
        self.assertEqual("Muster", reg[0].name)
        self.assertEqual("hans.muster@example.com", reg[0].email)
        self.assertEqual("rosa.muster@example.com", reg[1].email)

        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(datestr + " (noch 8 Plätze frei)", response.content.decode())

        settings.GENO_FORMAL = prev_geno_formal
