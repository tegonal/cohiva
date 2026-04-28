import json

import report.tests.data as testdata
from geno.utils import nformat
from report.models import ReportInputData, ReportInputField
from report.nk.cost import NkCostValueType, NkCostZEVStromallmend
from report.nk.generator import NkReportGenerator
from report.nk.measurement_data import NkMeasurementDataBase
from report.nk.rental_unit import NkVirtualRentalUnitId

from .base import NkReportTestCase


class NkMeasurementTestDataBuilding(NkMeasurementDataBase):
    def __init__(self, report_generator, measurements_config):
        super().__init__(report_generator, measurements_config)
        self.num_months = report_generator.num_months

    def load(self):
        # Building-level data: 230 kWh consumed from grid per month, 69 kWh returned to grid
        # => einspeisefaktor = 69/230 = 0.3 per month
        self.data = {
            "strom_bezug_zev": self.num_months * [230.0],
            "strom_ruecklieferung_ew": self.num_months * [69.0],
        }


class NkMeasurementTestDataRentalUnits(NkMeasurementDataBase):
    def __init__(self, report_generator, measurements_config):
        super().__init__(report_generator, measurements_config)
        self.num_months = report_generator.num_months

    def load(self):
        # Per-unit measurement data keyed by ru.name
        # 001a (area=100): solar=50, ew_hoch=30, ew_nieder=20 kWh/month
        # 001b (area=20):  solar=10, ew_hoch=6,  ew_nieder=4  kWh/month
        # Others: no measurement data (skip ZEV)
        num_months = self.num_months
        self.data = {
            "001a": {
                "strom_solar": num_months * [50.0],
                "strom_ew_hoch": num_months * [30.0],
                "strom_ew_nieder": num_months * [20.0],
                "chf_netz_hoch": num_months * [9.0],  # 30 kWh * 0.30 CHF/kWh
                "chf_netz_nieder": num_months * [5.6],  # 20 kWh * 0.28 CHF/kWh
            },
            "001b": {
                "strom_solar": num_months * [10.0],
                "strom_ew_hoch": num_months * [6.0],
                "strom_ew_nieder": num_months * [4.0],
                "chf_netz_hoch": num_months * [1.8],  # 6 kWh * 0.30 CHF/kWh
                "chf_netz_nieder": num_months * [1.12],  # 4 kWh * 0.28 CHF/kWh
            },
            "allg": {
                "strom_solar": num_months * [100.0],
                "strom_ew_hoch": num_months * [70.0],
                "strom_ew_nieder": num_months * [90.0],
                "chf_netz_hoch": num_months * [70 * 0.30],  # 0.30 CHF/kWh
                "chf_netz_nieder": num_months * [90 * 0.28],  # 0.28 CHF/kWh
            },
            "strom_pauschal": {
                "strom_solar": num_months * [1.0],
                "strom_ew_hoch": num_months * [2.0],
                "strom_ew_nieder": num_months * [3.0],
                "chf_netz_hoch": num_months * [2 * 0.30],  # 0.30 CHF/kWh
                "chf_netz_nieder": num_months * [3 * 0.28],  # 0.28 CHF/kWh
            },
        }


class NKCostZEVStromallmendTest(NkReportTestCase):
    zev_cost_config = {
        "class": NkCostZEVStromallmend,
        "name": "Stromkosten",
        "tarif_eigenstrom_key": "Strom:Tarif:Eigenstrom",
        "tarif_einspeiseverguetung_key": "Strom:Tarif:Einspeisevergütung",
        "tarif_hkn_key": "Strom:Tarif:HKN",
        "tarif_korrektur_key": "Strom:Tarif:Korrekturen",
        "korrekturen_key": "Strom:Korrekturen",
        "measurement_data": {
            "building": {"class": NkMeasurementTestDataBuilding},
            "rental_units": {"class": NkMeasurementTestDataRentalUnits},
        },
    }
    tarif_hoch = 0.3  # 0.30 CHF/kWh
    tarif_nieder = 0.28  # 0.28 CHF/kWh
    tarif_eigenstrom = 0.1453
    tarif_hkn = 0.07
    tarif_korrektur = 0.28
    tarif_einspeiseverguetung = [
        0.176,
        0.176,
        0.176,
        0.176,
        0.176,
        0.176,
        0.136,
        0.136,
        0.136,
        0.136,
        0.136,
        0.136,
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        testdata.create_nk_data(cls)

    def _setup_report_with_strom_data(self):
        """Configure a minimal report and populate measurement data for ZEV strom."""
        self.configure_test_report_minimal()
        report_generator = NkReportGenerator(self.report, True, output_root="/tmp/")
        report_generator.load_rental_units()
        report_generator.load_contracts()
        return report_generator

    def test_zev_cost_calculation(self):
        """Test NkCostZEVStromallmend per-unit cost calculation."""
        rg = self._setup_report_with_strom_data()
        num_months = rg.num_months

        cost = NkCostZEVStromallmend(rg, self.zev_cost_config)
        cost.load_input_data()
        cost.split_costs()

        # Recalculate expected values for 001a
        ru_001a = rg.get_rental_unit_by_name("001a")
        expected_chf_001a, expected_kwh_001a = self._calc_expected(50.0, 30.0, 20.0, num_months)
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001a.id][NkCostValueType.COST].amount,
            expected_chf_001a,
            places=4,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001a.id][NkCostValueType.USAGE].amount,
            expected_kwh_001a,
            places=4,
        )

        # Recalculate expected values for 001b
        ru_001b = rg.get_rental_unit_by_name("001b")
        expected_chf_001b, expected_kwh_001b = self._calc_expected(10.0, 6.0, 4.0, num_months, -1)
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001b.id][NkCostValueType.COST].amount,
            expected_chf_001b,
            places=4,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001b.id][NkCostValueType.USAGE].amount,
            expected_kwh_001b,
            places=4,
        )

        # Virtual rental units (Allgemeinstrom and Pauschal)
        expected_chf_allg, expected_kwh_allg = self._calc_expected(
            100, 70, 90, num_months, correction=-2 + 1
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[NkVirtualRentalUnitId.COMMON][NkCostValueType.COST].amount,
            expected_chf_allg,
            places=4,
        )
        ru_pauschal_id = -3
        expected_chf_pauschal, expected_kwh_pauschal = self._calc_expected(1, 2, 3, num_months)
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_pauschal_id][NkCostValueType.COST].amount,
            expected_chf_pauschal,
            places=4,
        )

        # Units without measurement data → 0
        ru_g001 = rg.get_rental_unit_by_name("G001")
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_g001.id][NkCostValueType.COST].amount,
            0.0,
        )

        # Grand total = sum of all units
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.COST].amount,
            expected_chf_001a + expected_chf_001b + expected_chf_allg + expected_chf_pauschal,
            places=4,
        )
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.USAGE].amount,
            expected_kwh_001a + expected_kwh_001b + expected_kwh_allg + expected_kwh_pauschal,
        )

    def _calc_expected(self, solar, hoch, nieder, num_months, correction=0.0):
        """Calculate expected cost and usage values for a single unit.

        For 001a per month:
          chf_eigen = 50 kWh * 0.1453 = 7.265 CHF
          kwh_netz = 30 + 20 = 50 kWh
          kwh_speicher = 0.3 * 50 = 15 kWh
          kwh_einkauf = 50 - 15 = 35 kWh
          chf_speicher = 15 * (0.1453 - 0.176) = 15 * (-0.0307) = -0.4605 CHF
            (negative because einspeisung tariff > eigenstrom tariff in summer months)
          chf_hkn = 35 * 0.07 = 2.45 CHF
          chf_total = 7.265 + (-0.4605) + 2.45 + 9.0 + 5.6 = 23.8545 CHF/month
        """
        expected_chf = 0
        expected_kwh = 0
        for m in range(num_months):
            kwh_netz = hoch + nieder
            kwh_speicher = 0.3 * kwh_netz
            kwh_einkauf = kwh_netz - kwh_speicher
            chf_korrektur = correction * self.tarif_korrektur
            chf_eigen = solar * self.tarif_eigenstrom
            chf_speicher = kwh_speicher * (
                self.tarif_eigenstrom - self.tarif_einspeiseverguetung[m]
            )
            chf_hkn = kwh_einkauf * self.tarif_hkn
            chf_total_month = (
                chf_eigen
                + chf_speicher
                + chf_hkn
                + hoch * self.tarif_hoch
                + nieder * self.tarif_nieder
                + chf_korrektur
            )
            expected_chf += chf_total_month
            expected_kwh += solar + hoch + nieder + correction
        return expected_chf, expected_kwh

    def test_zev_extra_context(self):
        """Test that get_extra_context() returns the correct Stromkosten variables."""
        rg = self._setup_report_with_strom_data()

        cost = NkCostZEVStromallmend(rg, self.zev_cost_config)
        cost.load_input_data()
        cost.split_costs()
        rg.assign_rental_unit_months_to_contracts()

        ru_001a = rg.get_rental_unit_by_name("001a")
        ctx = cost.get_extra_context(ru_001a, rg.get_contract_by_id(self.contracts[0].id))

        num_months = rg.num_months
        # ssd: Eigenverbrauch Solar direkt
        expected_ssd_kwh = 50.0 * num_months  # 50 kWh/month
        expected_ssd_chf = expected_ssd_kwh * 0.1453
        self.assertEqual(ctx["ssd"], nformat(expected_ssd_kwh, 0))
        self.assertEqual(ctx["ssd_chf"], f"{expected_ssd_chf:,.2f}".replace(",", "'"))

        # snh/snt: Netzstrom hoch/tief
        expected_snh_kwh = 30.0 * num_months  # 30 kWh/month
        expected_snh_chf = expected_snh_kwh * self.tarif_hoch
        expected_snt_kwh = 20.0 * num_months  # 20 kWh/month
        expected_snt_chf = expected_snt_kwh * self.tarif_nieder
        self.assertEqual(ctx["snh"], nformat(expected_snh_kwh, 0))
        self.assertEqual(ctx["snt"], nformat(expected_snt_kwh, 0))
        self.assertEqual(ctx["snh_chf"], nformat(expected_snh_chf))
        self.assertEqual(ctx["snt_chf"], nformat(expected_snt_chf))

        # sss: Eigenverbrauch Solar via Speicher
        # kwh_netz = 50/month, kwh_speicher = 0.3 * 50 = 15/month
        expected_sss_kwh = 15.0 * num_months
        self.assertEqual(ctx["sss"], nformat(expected_sss_kwh, 0))

        # Building totals
        expected_ssdt = num_months * (50 + 10 + 100 + 1)
        expected_snht = num_months * (30 + 6 + 70 + 2)
        self.assertEqual(ctx["ssdt"], nformat(expected_ssdt, 0))
        self.assertEqual(ctx["ssd_chft"], nformat(expected_ssdt * self.tarif_eigenstrom))
        self.assertEqual(ctx["snht"], nformat(expected_snht, 0))
        self.assertEqual(ctx["snh_chft"], nformat(expected_snht * self.tarif_hoch))
        self.assertIsInstance(ctx["stot_chft"], str)

        # Units without data get zeros in context
        ru_g001 = rg.get_rental_unit_by_name("G001")
        ctx_g001 = cost.get_extra_context(ru_g001, rg.get_contract_by_id(self.contracts[2].id))
        self.assertEqual(ctx_g001["ssd"], "0")
        self.assertEqual(ctx_g001["sss"], "0")
        self.assertEqual(ctx_g001["st_chf"], "0.00")

    def test_zev_no_measurement_data(self):
        """When no measurement data is present, all costs are zero."""
        self.configure_test_report_minimal()
        rg = NkReportGenerator(self.report, True, output_root="/tmp/")
        rg.load_rental_units()

        cost = NkCostZEVStromallmend(rg, self.zev_cost_config)
        # Remove measurement data
        cost.measurements = {
            "building": NkMeasurementDataBase(rg, {}),
            "rental_units": NkMeasurementDataBase(rg, {}),
        }
        cost.load_input_data()
        cost.split_costs()

        self.assertAlmostEqual(cost.total_values[NkCostValueType.COST].amount, 0.0)
        for ru in rg.rental_units:
            self.assertAlmostEqual(
                cost.rental_unit_values[ru.id][NkCostValueType.COST].amount, 0.0
            )

    def test_zev_invalid_correction_rental_unit(self):
        self.configure_test_report_minimal()
        inputdata = ReportInputData.objects.get(
            name=ReportInputField.objects.get(name="Strom:Korrekturen"), report=self.report
        )
        inputdata.value = json.dumps(
            {
                "_INVALID_RU_": [
                    {
                        "desc": "Test",
                        "tarif": "mittel",
                        "kwh": 12 * [-1],
                    }
                ]
            }
        )
        inputdata.save()
        rg = NkReportGenerator(self.report, True, output_root="/tmp/")
        rg.load_rental_units()

        with self.assertRaises(ValueError):
            NkCostZEVStromallmend(rg, self.zev_cost_config)

    def test_zev_invalid_correction_tarif(self):
        self.configure_test_report_minimal()
        inputdata = ReportInputData.objects.get(
            name=ReportInputField.objects.get(name="Strom:Korrekturen"), report=self.report
        )
        inputdata.value = json.dumps(
            {
                "allg": [
                    {
                        "desc": "Test",
                        "tarif": "_INVALID_TARIF_",
                        "kwh": 12 * [-1],
                    }
                ]
            }
        )
        inputdata.save()
        rg = NkReportGenerator(self.report, True, output_root="/tmp/")
        rg.load_rental_units()

        with self.assertRaises(ValueError):
            NkCostZEVStromallmend(rg, self.zev_cost_config)
