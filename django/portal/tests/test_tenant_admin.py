from django.conf import settings
from django.core import mail

from .base import PortalTestCase


class PortalTenantAdminTest(PortalTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # cls.UserModel = get_user_model()

    def test_unauthorized(self):
        self.client.login(username="user.tenant", password="secret")
        response = self.get_secondary("/portal/tenant-admin/")
        self.assertInHTMLResponse("FEHLER: Keine Berechtigung für diese Aktion.", response)

    def test_add_tenant(self):
        self.client.login(username="Tenantadmin1", password="secret")
        response = self.get_secondary("/portal/tenant-admin/")
        self.assertInHTMLResponse("tenant1@example.com", response)
        self.assertInHTMLResponse("tenant2@example.com", response)
        self.assertInHTMLResponse('<a href="/portal/tenant-admin/add/"', response, raw=True)

        response = self.get_secondary("/portal/tenant-admin/add/")
        # self.assertInHTMLResponse('<input type="email" name="email" required id="id_email">', response)
        self.assertInHTMLResponse(
            '<input type="email" name="email" maxlength="320" required id="id_email">', response
        )

        response = self.post_secondary(
            "/portal/tenant-admin/add/",
            {"first_name": "First3", "name": "Tenant3", "email": "tenant3@example.com"},
        )
        self.assertInHTMLResponse("tenant1@example.com", response)
        self.assertInHTMLResponse("tenant2@example.com", response)
        self.assertInHTMLResponse("tenant3@example.com", response)

    def test_send_invite_mail(self):
        self.client.login(username="Tenantadmin1", password="secret")
        response = self.post_secondary(
            "/portal/tenant-admin/",
            {
                "action": "invite",
                "submit_action": "Ausführen",
                "selection": [self.tenants[0].id, self.tenants[1].id],
            },
        )
        self.assertInHTMLResponse("Es wurden 2 Einladungs-Mails verschickt.", response)
        self.assertIn("INFO: Created new user: tenant1", mail.outbox[0].subject)
        self.assertIn(
            f"Einladungsmail: {settings.PORTAL_SECONDARY_NAME}-Konto aktivieren",
            mail.outbox[1].subject,
        )
        self.assertIn("INFO: Created new user: tenant2", mail.outbox[2].subject)
        self.assertIn(
            f"Einladungsmail: {settings.PORTAL_SECONDARY_NAME}-Konto aktivieren",
            mail.outbox[3].subject,
        )
