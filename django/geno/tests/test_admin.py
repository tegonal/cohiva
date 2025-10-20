import datetime

import geno.tests.data as geno_testdata

# from django.conf import settings
from geno.models import Address, ContentTemplate, Contract, GenericAttribute, Member

from .base import GenoAdminTestCase


class GenoAdminTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        geno_testdata.create_contracts(cls)

    def test_admin_views_status200(self):
        logged_in = self.client.login(username="superuser", password="secret")
        self.assertTrue(logged_in)
        paths = [
            "geno/address/",
            f"geno/address/{self.addresses[0].id}/change/",
            "geno/member/",
            f"geno/member/{self.members[0].id}/change/",
            "geno/child/",
            f"geno/child/{self.children[0].id}/change/",
            "geno/share/",
            f"geno/share/{self.shares[0].id}/change/",
            "geno/building/",
            f"geno/building/{self.buildings[0].id}/change/",
            "geno/rentalunit/",
            f"geno/rentalunit/{self.rentalunits[0].id}/change/",
            "geno/contract/",
            f"geno/contract/{self.contracts[0].id}/change/",
            "geno/invoicecategory/",
            f"geno/invoicecategory/{self.invoicecategories[0].id}/change/",
            "geno/contenttemplate/",
            f"geno/contenttemplate/{self.contenttemplates[0].id}/change/",
            "geno/contenttemplateoption/",
            f"geno/contenttemplateoption/{self.contenttemplateoptions['billing'][0].id}/change/",
            "geno/documenttype/",
            f"geno/documenttype/{self.documenttypes[0].id}/change/",
        ]
        for path in paths:
            try:
                response = self.client.get(f"/admin/{path}")
            except Exception as e:
                print(f"FAILED PATH: /admin/{path} [Exception: {e}]")
                raise e
            if response.status_code != 200:
                print(f"FAILED PATH: /admin/{path} [{response.status_code}]")
            self.assertEqual(response.status_code, 200)

    def test_admin_links(self):
        logged_in = self.client.login(username="superuser", password="secret")
        self.assertTrue(logged_in)

        dummydate = datetime.date(2025, 1, 1)

        adr1 = Address.objects.create(name="LinkTest", first_name="One")
        adr2 = Address.objects.create(name="LinkTest", first_name="Two")
        adr3 = Address.objects.create(name="LinkTest", first_name="Three")
        adr4 = Address.objects.create(name="LinkTest", first_name="Four")

        member = Member.objects.create(name=adr1, date_join=dummydate)

        contract = Contract.objects.create(main_contact=adr3, date=dummydate)
        contract.contractors.set([adr1, adr2])
        contract.save()

        generic1 = GenericAttribute.objects.create(
            name="Generic1", value="Test", content_object=adr4
        )
        generic2 = GenericAttribute.objects.create(
            name="Generic2", value="Test", content_object=adr4
        )

        ## Links (foreign key and m2m)
        response = self.client.get(f"/admin/geno/contract/{contract.id}/change/")
        for adr in [adr1, adr2, adr3]:
            expected = f'<a href="/admin/geno/address/{adr.id}">{adr}</a>'
            self.assertContains(response, expected, html=True)

        ## Links 1:1 key
        response = self.client.get(f"/admin/geno/member/{member.id}/change/")
        expected = f'<li>Adresse: <a href="/admin/geno/address/{adr1.id}">LinkTest, One</a></li>'
        self.assertContains(response, expected, html=True)

        ## Links generic relation (ContentType)
        response = self.client.get(f"/admin/geno/genericattribute/{generic1.id}/change/")
        expected = f'<li>Adresse: <a href="/admin/geno/address/{adr4.id}">LinkTest, Four</a></li>'
        self.assertContains(response, expected, html=True)

        ## Backlinks
        response = self.client.get(f"/admin/geno/address/{adr1.id}/change/")
        expected = f'<li>Mitglied: <ul><li><a href="/admin/geno/member/{member.id}">LinkTest, One</a></li></ul></li>'
        self.assertContains(response, expected, html=True)
        expected = f'<li>Vertrag: <ul><li><a href="/admin/geno/contract/{contract.id}"> [One LinkTest/Two LinkTest]</a></li></ul></li>'
        self.assertContains(response, expected, html=True)

        response = self.client.get(f"/admin/geno/address/{adr2.id}/change/")
        expected = f'<li>Vertrag: <ul><li><a href="/admin/geno/contract/{contract.id}"> [One LinkTest/Two LinkTest]</a></li></ul></li>'
        self.assertContains(response, expected, html=True)

        response = self.client.get(f"/admin/geno/address/{adr3.id}/change/")
        expected = f'<li>Vertrag: <ul><li><a href="/admin/geno/contract/{contract.id}"> [One LinkTest/Two LinkTest]</a></li></ul></li>'
        self.assertContains(response, expected, html=True)

        response = self.client.get(f"/admin/geno/address/{adr4.id}/change/")
        expected = f"""<li>Attribut: <ul>
                                <li><a href="/admin/geno/genericattribute/{generic2.id}">LinkTest, Four [Generic2 - Test]</a></li>
                                <li><a href="/admin/geno/genericattribute/{generic1.id}">LinkTest, Four [Generic1 - Test]</a></li>
                            </ul></li>"""
        self.assertContains(response, expected, html=True)

    def test_copy_objects(self):
        adr = Address.objects.create(name="Copytest", first_name="First")
        adr.save_as_copy()
        copy = Address.objects.get(name="Copytest [KOPIE]")
        self.assertEqual(copy.first_name, "First")

        contract = Contract.objects.create(date=datetime.date(2025, 1, 1))
        contract.rental_units.set(self.rentalunits[0:2])
        contract.contractors.set(self.addresses[0:2])
        contract.children.set(self.children[0:2])
        contract.save()
        old_contract_id = contract.id

        contract.save_as_copy()
        new_contract_id = contract.id

        self.assertNotEqual(old_contract_id, new_contract_id)
        old_contract = Contract.objects.get(id=old_contract_id)
        new_contract = Contract.objects.get(id=new_contract_id)
        self.assertNotEqual(old_contract, new_contract)
        self.assertEqual(old_contract.date, new_contract.date)
        self.assertListEqual(
            list(old_contract.contractors.all()), list(new_contract.contractors.all())
        )
        self.assertListEqual(
            list(old_contract.rental_units.all()), list(new_contract.rental_units.all())
        )
        self.assertListEqual(list(old_contract.children.all()), list(new_contract.children.all()))

        ct = self.contenttemplates[0]
        old_ct_id = ct.id
        ct.save_as_copy()
        new_ct_id = ct.id
        self.assertNotEqual(old_ct_id, new_ct_id)
        old_ct = ContentTemplate.objects.get(id=old_ct_id)
        new_ct = ContentTemplate.objects.get(id=new_ct_id)
        self.assertNotEqual(old_ct, new_ct)
        self.assertEqual(old_ct.template_type, new_ct.template_type)
        self.assertListEqual(
            list(old_ct.template_context.all()), list(new_ct.template_context.all())
        )
