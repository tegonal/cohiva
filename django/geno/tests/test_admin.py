import datetime
from unittest.mock import patch

from django.contrib import admin as django_admin
from django.db.models import Q
from django.test import RequestFactory

import geno.admin
import geno.tests.data as geno_testdata
from geno import admin
from geno.admin import BooleanFieldDefaultTrueListFilter

# from django.conf import settings
from geno.models import Address, Child, ContentTemplate, Contract, GenericAttribute, Member
from geno.tests.base import MockDate

from .base import GenoAdminTestCase


class GenoAdminTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        geno_testdata.create_contracts(cls)
        inactive_adr = Address.objects.create(name="Inactive Address", active=False)
        Child.objects.create(name=inactive_adr, presence=1)

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

    @patch("geno.admin.datetime.date", MockDate)
    def test_admin_contract_actions(self):
        self.contracts.append(
            Contract.objects.create(date=datetime.date(2000, 6, 6), state="test1")
        )
        self.contracts.append(
            Contract.objects.create(date=datetime.date(2000, 6, 7), state="test2")
        )
        queryset = Contract.objects.filter(
            Q(pk=self.contracts[0].pk) | Q(pk=self.contracts[-1].pk)
        )
        admin.contract_mark_invalid(None, None, queryset)
        self.contracts[0].refresh_from_db()
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[0].state, "ungueltig")
        self.assertEqual(self.contracts[-1].state, "ungueltig")
        self.assertEqual(self.contracts[1].state, "test1")

        admin.contract_set_startdate_lastmonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].date, datetime.date(2024, 12, 1))
        admin.contract_set_startdate_thismonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].date, datetime.date(2025, 1, 1))
        admin.contract_set_startdate_nextmonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].date, datetime.date(2025, 2, 1))

        admin.contract_set_enddate_lastmonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].date_end, datetime.date(2024, 12, 31))
        admin.contract_set_enddate_thismonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].date_end, datetime.date(2025, 1, 31))
        admin.contract_set_enddate_nextmonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].date_end, datetime.date(2025, 2, 28))

        admin.contract_set_billingstart_lastmonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].billing_date_start, datetime.date(2024, 12, 1))
        admin.contract_set_billingstart_thismonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].billing_date_start, datetime.date(2025, 1, 1))
        admin.contract_set_billingstart_nextmonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].billing_date_start, datetime.date(2025, 2, 1))

        admin.contract_set_billingend_lastmonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].billing_date_end, datetime.date(2024, 12, 31))
        admin.contract_set_billingend_thismonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].billing_date_end, datetime.date(2025, 1, 31))
        admin.contract_set_billingend_nextmonth(None, None, queryset)
        self.contracts[-1].refresh_from_db()
        self.assertEqual(self.contracts[-1].billing_date_end, datetime.date(2025, 2, 28))

    def create_BooleanFieldDefaultTrueListFilter(
        self,
        model_name="address",
        query_params=None,
    ):
        if model_name == "address":
            model = Address
            field_path = "active"
            model_admin = geno.admin.AddressAdmin
        elif model_name == "child":
            model = Child
            field_path = "name__active"
            model_admin = geno.admin.ChildAdmin
        else:
            raise ValueError("Unknown model_name")
        factory = RequestFactory()
        request = factory.get(f"/admin/geno/{model_name}/", query_params=query_params)
        admin_instance = model_admin(model, django_admin.site)
        _filter = BooleanFieldDefaultTrueListFilter(
            field=Address._meta.get_field("active"),
            request=request,
            params=query_params or {},
            model=model,
            model_admin=admin_instance,
            field_path=field_path,
        )
        qs = _filter.queryset(request, model.objects.all())
        request.user = self.su
        changelist = admin_instance.get_changelist_instance(request)
        return _filter, qs, changelist

    def test_BooleanFieldDefaultTrueListFilter_title(self):
        _filter, _, _ = self.create_BooleanFieldDefaultTrueListFilter()
        self.assertEqual(_filter.title, "Aktiv")

        _filter, _, _ = self.create_BooleanFieldDefaultTrueListFilter("child")
        self.assertEqual(_filter.title, "Aktiv (Adresse)")

    def test_BooleanFieldDefaultTrueListFilter_default(self):
        _, qs, _ = self.create_BooleanFieldDefaultTrueListFilter()
        self.assertEqual(qs.count(), 8)

    def test_BooleanFieldDefaultTrueListFilter_active(self):
        _, qs, _ = self.create_BooleanFieldDefaultTrueListFilter(
            query_params={"active__exact": "1"}
        )
        self.assertEqual(qs.count(), 8)

    def test_BooleanFieldDefaultTrueListFilter_inactive(self):
        _, qs, _ = self.create_BooleanFieldDefaultTrueListFilter(
            query_params={"active__exact": "0"}
        )
        self.assertEqual(qs.count(), 1)

    def test_BooleanFieldDefaultTrueListFilter_all(self):
        _, qs, _ = self.create_BooleanFieldDefaultTrueListFilter(
            query_params={"active__exact": "all"}
        )
        self.assertEqual(qs.count(), 9)

    def test_BooleanFieldDefaultTrueListFilter_related_default(self):
        _, qs, _ = self.create_BooleanFieldDefaultTrueListFilter(model_name="child")
        self.assertEqual(qs.count(), 2)

    def test_BooleanFieldDefaultTrueListFilter_related_active(self):
        _, qs, _ = self.create_BooleanFieldDefaultTrueListFilter(
            model_name="child", query_params={"name__active__exact": "1"}
        )
        self.assertEqual(qs.count(), 2)

    def test_BooleanFieldDefaultTrueListFilter_related_inactive(self):
        _, qs, _ = self.create_BooleanFieldDefaultTrueListFilter(
            model_name="child", query_params={"name__active__exact": "0"}
        )
        self.assertEqual(qs.count(), 1)

    def test_BooleanFieldDefaultTrueListFilter_related_all(self):
        _, qs, _ = self.create_BooleanFieldDefaultTrueListFilter(
            model_name="child", query_params={"name__active__exact": "all"}
        )
        self.assertEqual(qs.count(), 3)

    def test_BooleanFieldDefaultTrueListFilter_choices(self):
        _filter, _, changelist = self.create_BooleanFieldDefaultTrueListFilter()
        choices = list(_filter.choices(changelist))
        self.assertEqual(choices[0]["query_string"], "?active__exact=all")
        self.assertEqual(choices[1]["query_string"], "?active__exact=1")
        self.assertEqual(choices[2]["query_string"], "?active__exact=0")
        self.assertEqual(choices[0]["selected"], False)
        self.assertEqual(choices[1]["selected"], True)
        self.assertEqual(choices[2]["selected"], False)
        _filter, _, changelist = self.create_BooleanFieldDefaultTrueListFilter(
            query_params={"active__exact": "all"}
        )
        choices = list(_filter.choices(changelist))
        self.assertEqual(choices[0]["selected"], True)
        self.assertEqual(choices[1]["selected"], False)
        self.assertEqual(choices[2]["selected"], False)
        _filter, _, changelist = self.create_BooleanFieldDefaultTrueListFilter(
            query_params={"active__exact": "0"}
        )
        choices = list(_filter.choices(changelist))
        self.assertEqual(choices[0]["selected"], False)
        self.assertEqual(choices[1]["selected"], False)
        self.assertEqual(choices[2]["selected"], True)
        _filter, _, changelist = self.create_BooleanFieldDefaultTrueListFilter(
            query_params={"active__exact": "1"}
        )
        choices = list(_filter.choices(changelist))
        self.assertEqual(choices[0]["selected"], False)
        self.assertEqual(choices[1]["selected"], True)
        self.assertEqual(choices[2]["selected"], False)

    def test_COHIV133_dont_overwrite_model_field_name(self):
        self.client.login(username="superuser", password="secret")
        # Setup  model field name to name__active by
        self.client.get("/admin/geno/child/")
        # Bug COHIV-133 will result in a HTTP Error 500 here:
        response = self.client.get("/admin/geno/address/add/")
        self.assertEqual(response.status_code, 200)
