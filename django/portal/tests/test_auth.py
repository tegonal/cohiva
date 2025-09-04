import re
from urllib.parse import quote

from django.conf import settings
from django.core import mail
from oauth2_provider.models import get_application_model
from requests_oauthlib import OAuth2Session

from geno.models import Address

from .base import PortalTestCase


class PortalAuthTest(PortalTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # cls.UserModel = get_user_model()

    def signup_user(self):
        response = self.client.get("/portal/")
        self.assertInHTMLResponse("Aktivieren", response)

        response = self.client.post("/portal/login/", {"register": ""})
        self.assertInHTMLResponse("E-Mail Adresse", response)

        response = self.client.post("/portal/password_reset/", {"email": self.addresses[0].email})
        self.assertInHTMLResponse(
            "Falls die angegebene Email-Adresse bei uns registriert ist", response, raw=True
        )

        self.assertIn("INFO: Created new user: hans.muster", mail.outbox[0].subject)
        self.assertIn(
            f"{settings.COHIVA_SITE_NICKNAME}-Konto aktivieren / Passwort zurücksetzen",
            mail.outbox[1].subject,
        )

        match = re.search(
            r"neues Passwort für dein Konto zu setzen: https://\S+(/portal/reset/\S+/)\s",
            mail.outbox[1].body,
        )
        self.assertTrue(bool(match))
        reset_url = match.group(1)
        response = self.client.get(reset_url)
        (response, content, last_redirect) = self.assertInHTMLResponse(
            "Bitte wähle ein neues Passwort", response, raw=True
        )

        self.userpass = "newdummy"
        response = self.client.post(
            last_redirect, {"new_password1": self.userpass, "new_password2": self.userpass}
        )
        self.assertInHTMLResponse("Dein neues Passwort wurde aktiviert.", response, raw=True)

        self.user = self.UserModel.objects.get(email=self.addresses[0].email)
        adr = Address.objects.get(email=self.addresses[0].email)
        self.assertEqual(self.user, adr.user)
        self.addresses[0].user = self.user

    def portal_oauth(self):
        ## Setup OAuth provider
        dummy_redirect_uri = "https://localhost/oauth2/callback"
        application = get_application_model()
        provider_app = application(
            name="Test",
            authorization_grant_type=application.GRANT_AUTHORIZATION_CODE,
            client_type=application.CLIENT_CONFIDENTIAL,
            redirect_uris=dummy_redirect_uri,
            user=self.user,
        )
        client_secret = provider_app.client_secret
        provider_app.save()

        ## Start Authorization
        oauth = OAuth2Session(provider_app.client_id, redirect_uri=dummy_redirect_uri)
        authorization_url, state = oauth.authorization_url("https://localhost/o/authorize/")
        self.assertIn(
            f"https://localhost/o/authorize/?response_type=code&client_id={provider_app.client_id}",
            authorization_url,
        )
        # print(authorization_url)
        # request.session['test_oauth_state'] = state
        # request.session['test_oauth_origin_url'] = request.get_full_path()
        # print("Redirecting to authorization URL: %s" % authorization_url)
        auth_url = authorization_url[len("https://localhost") :]
        response = self.client.get(auth_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/portal/login/?next=" + quote(auth_url), response.url)

        ## Do login
        response = self.client.get(response.url)
        self.assertInHTMLResponse("E-Mail oder Benutzername", response)
        logged_in = self.client.login(username=self.user.username, password=self.userpass)
        self.assertTrue(logged_in)

        ## Finish Authorization
        response = self.client.get(auth_url)
        self.assertInHTMLResponse("Berechtigung für Test?", response)
        scope = " ".join(settings.OAUTH2_PROVIDER["SCOPES"].keys())
        post_data = {
            "allow": "Zustimmen",
            "client_id": provider_app.client_id,
            "state": state,
            "redirect_uri": dummy_redirect_uri,
            "scope": scope,
            "response_type": "code",
        }
        response = self.client.post(auth_url, post_data)
        self.assertEqual(response.status_code, 302)
        match = re.search(f"{dummy_redirect_uri}\\?code=(\\S+)&state={state}", response.url)
        self.assertTrue(bool(match))
        auth_code = match.group(1)

        ## Logout and get access token
        self.client.logout()
        post_data = {
            "client_id": provider_app.client_id,
            "client_secret": client_secret,  # provicer_app.client_secret can't be used because it is encrypted on save()
            "state": state,
            "redirect_uri": dummy_redirect_uri,
            "scope": scope,
            "grant_type": "authorization_code",
            "code": auth_code,
        }
        response = self.client.post("/o/token/", post_data)
        self.assertEqual(response.status_code, 200)
        token = response.json()
        self.assertEqual(token["token_type"], "Bearer")
        self.assertTrue("refresh_token" in token)

        ## Forbidden without token
        response = self.client.get("/portal/me/")
        self.assertEqual(response.status_code, 403)

        ## Use token and check profile information
        response = self.client.get(
            "/portal/me/", HTTP_AUTHORIZATION=f"Bearer {token['access_token']}"
        )
        self.assertEqual(response.status_code, 200)
        profile = response.json()
        self.assertEqual(profile["email"], self.addresses[0].email)
        self.assertEqual(profile["username"], self.user.username)
        self.assertEqual(
            profile["name"], f"{self.addresses[0].first_name} {self.addresses[0].name}"
        )
        self.assertEqual(profile["id"], f"{settings.GENO_ID}_{self.user.id}")

    def test_portal_auth(self):
        self.signup_user()
        self.portal_oauth()

    def test_login_with_next(self):
        response = self.client.post(
            "/portal/login/",
            {"next": "###TEST_NEXT_URL###", "username": "test", "password": "test"},
        )
        self.assertInHTMLResponse(
            '<input type="hidden" name="next" value="###TEST_NEXT_URL###">', response
        )

    def test_login_fail(self):
        response = self.client.post(
            "/portal/login/",
            {"next": "/portal/password_change/", "username": "invalid", "password": "invalid"},
        )
        self.assertInHTMLResponse(
            "Das eingegebene Passwort oder der Benutzername ist ungültig. Bitte versuche es nochmals.",
            response,
        )

    def test_login(self):
        response = self.client.post(
            "/portal/login/",
            {"next": "/portal/password_change/", "username": "user.renter", "password": "secret"},
        )
        self.assertInHTMLResponse("Altes Passwort:", response)

    def test_login_with_email(self):
        response = self.client.post(
            "/portal/login/",
            {
                "next": "/portal/password_change/",
                "username": "renter@example.com",
                "password": "secret",
            },
        )
        self.assertInHTMLResponse("Altes Passwort:", response)

    def test_portal_redirect_primary_to_secondary(self):
        response = self.client.post(
            "/portal/password_reset/", {"email": self.tenants[0].name.email}
        )
        self.assertEqual(response.status_code, 302)
        match = re.search(
            rf"{settings.PORTAL_SECONDARY_HOST}(/portal/password_reset/\?email=\S+&autosubmit=1)$",
            response.url,
        )
        self.assertTrue(bool(match))
        redirect_url = match.group(1)

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(
            "ERROR: Unauthorized account activation - testserver", mail.outbox[0].subject
        )
        self.assertIn(
            f"INFO: Password reset for unknown user: {self.tenants[0].name.email} - testserver",
            mail.outbox[1].subject,
        )

        response = self.get_secondary(redirect_url)
        self.assertInHTMLResponse(
            "Falls die angegebene Email-Adresse bei uns registriert ist", response, raw=True
        )

        self.assertIn("INFO: Created new user: tenant1", mail.outbox[2].subject)
        self.assertIn(
            f"{settings.PORTAL_SECONDARY_NAME}-Konto aktivieren / Passwort zurücksetzen",
            mail.outbox[3].subject,
        )

    def test_portal_redirect_secondary_to_primary(self):
        response = self.post_secondary(
            "/portal/password_reset/", {"email": self.addresses[0].email}
        )
        self.assertEqual(response.status_code, 302)
        match = re.search(r"(/portal/password_reset/\?email=\S+&autosubmit=1)$", response.url)
        self.assertTrue(bool(match))
        redirect_url = match.group(1)

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(
            f"ERROR: Unauthorized account activation - {settings.PORTAL_SECONDARY_HOST}",
            mail.outbox[0].subject,
        )
        self.assertIn(
            f"INFO: Password reset for unknown user: {self.addresses[0].email} - {settings.PORTAL_SECONDARY_HOST}",
            mail.outbox[1].subject,
        )

        response = self.client.get(redirect_url)
        self.assertInHTMLResponse(
            "Falls die angegebene Email-Adresse bei uns registriert ist", response, raw=True
        )

        self.assertIn("INFO: Created new user: hans.muster", mail.outbox[2].subject)
        self.assertIn(
            f"{settings.COHIVA_SITE_NICKNAME}-Konto aktivieren / Passwort zurücksetzen",
            mail.outbox[3].subject,
        )
