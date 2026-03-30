import json
import os
import shutil
from collections import OrderedDict
from datetime import datetime, timedelta

from django.db.models import Q

from geno.models import Contract, RentalUnit
from geno.utils import JSONDecoderDatetime, nformat
from report.generator import ReportGenerator
from report.models import ReportOutput
from report.nk.bill import NkBill
from report.nk.contract import NkContract
from report.nk.cost.base import NkCostValueType
from report.nk.cost_config import get_costs_from_config
from report.nk.export_csv import ExportCSV
from report.nk.rental_unit import NkRentalUnit
from report.nk.section import NK_SECTIONS, get_section_by_id


class NkReportGenerator(ReportGenerator):
    default_config = {
        "Ausgabe:Plots": False,
        "Ausgabe:QR-Rechnungen": False,
        "Strom:Korrekturen": {},
        "Strom:Tarif:Korrekturen": {},
        "Liegenschaften": [],
    }

    def __init__(self, report, dry_run, output_root, *args, **kwargs):
        super().__init__(report, *args, **kwargs)
        self.start_year = int(self.config["Startjahr"])
        self.start_month = 7
        self.num_months = 12
        self.num_months_passed = 0
        self.period_start_index = 0
        self.dry_run = dry_run
        self.report = report

        self.dates = self.init_dates()

        self.costs = []
        self.rental_units = []
        self.contracts = []

        self.object_messung = {}
        self.object_weights = [
            "area",
            "messung_warmwasser",
            "area_warmwasser",
            "min_occupancy",
            "messung_heizung",
            "volume",
            "messung_wasser",
        ]
        self.totals = {}

        self.data_amount = {}
        self.previous_data = {}

        self.strom_total = {
            "solar_eigen": {"kwh": 12 * [0], "chf": 12 * [0]},
            "solar_speicher": {"kwh": 12 * [0], "chf": 12 * [0]},
            "solar_einkauf": {"kwh": 12 * [0], "chf": 12 * [0]},
            "ew_hoch": {"kwh": 12 * [0], "chf": 12 * [0]},
            "ew_nieder": {"kwh": 12 * [0], "chf": 12 * [0]},
            "korrektur": {"kwh": 12 * [0], "chf": 12 * [0]},
            "total": {"kwh": 12 * [0], "chf": 12 * [0]},
            "total_netz": {"kwh": 12 * [0], "chf": 12 * [0]},
            "total_sect": {},
        }

        self.monthly_weights = {
            # Jul  Aug  Sep  Oct  Nov  Dez  Jan  Feb  Mar  Apr  May  Jun
            "default": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        }

        self.admin_fee_factor = float(self.config["Verwaltungsaufwand:Faktor"]) / 100.0

        self.section_weights = {
            "default": {"Allgemein": 1.0, "Wohnen": 1.0, "Gewerbe": 1.0, "Lager": 1.0},
            #'ohne_lager': {'Allgemein': 1.0, 'Wohnen': 1.0, 'Gewerbe': 1.0, 'Lager': 0.0},
            "nur_wohnen": {"Allgemein": 0.0, "Wohnen": 1.0, "Gewerbe": 0.0, "Lager": 0.0},
            "radiatoren": {"Allgemein": 0.0, "Wohnen": 0.01, "Gewerbe": 1.0, "Lager": 0.0},
            "lueftung": {
                "Allgemein": 0.0,
                "Wohnen": 0.35,
                "Gewerbe": 0.55,
                "Lager": 0.1,
            },  ## Abschätzung aus Luftmenge, Betriebszeiten, Temperatur
            "wasser_allgemein": {"Allgemein": 0.0, "Wohnen": 1.0, "Gewerbe": 0.5, "Lager": 0.5},
            #'allgemeinstrom': {'Allgemein': 0.0, 'Wohnen': 1.0, 'Gewerbe': 1.0, 'Lager': 1.0},
            "reinigung": {"Allgemein": 0.0, "Wohnen": 0.7, "Gewerbe": 1.0, "Lager": 1.0},
        }

        self.virtual_contracts = {
            "-1": "Gästezimmer",
            "-2": "Sitzungszimmer",
            "-3": "Geschäftsstelle",
            "-4": "Holliger",
            "-5": "Allgemein",
            "-6": "Leerstand",
        }

        self.virtual_contracts_map = {
            "003": "-1",
            "410": "-1",
            "509": "-1",
            "9907": "-2",
            "9909": "-2",
            "9912": "-2",
            "9932": "-3",
            "9931": "-4",
            "9728": "-4",
            "9729": "-4",
            "604": "-5",  # Dachküche
            "9913": "-5",  # Teeküche
        }

        self.categories = OrderedDict()
        self.categories["hauswart"] = {"i": 0, "label": "Hauswart/Reinigung/Kehricht/Serviceabos"}
        self.categories["waerme_wasser_grund"] = {
            "i": 1,
            "label": "Heizung/Warmwasser/Wasser/Abwasser allg.",
        }
        self.categories["strom_allgemein"] = {"i": 2, "label": "Allgemeinstrom"}
        self.categories["waerme_wasser_verbrauch"] = {
            "i": 3,
            "label": "Heizung/Warmwasser/Wasser/Abwasser indiv. Verbrauch",
        }
        self.categories["strom"] = {"i": 4, "label": "Strom indiv. Verbrauch"}
        self.categories["internet"] = {"i": 5, "label": "Internet/WLAN"}
        self.categories["verwaltung"] = {"i": 6, "label": "Verwaltungsaufwand"}

        self.limit_bills_to_contract_ids = list(
            map(str, self.config.get("Ausgabe:LimitiereVertragsIDs"))
        )

        ## Logging
        self.log = []

        ## Options
        self.output_object_data = True  ## Save intermediate data and plots based on rental units?
        self.save_json_data = True  ## Save data to json file
        self.output_dir = "/tmp/nk_output"  ## Temporary files

        self.init_output(output_root)
        self.init_costs()

    def init_output(self, output_root):
        ## Output dir
        self.root = output_root + f"/report/{self.report.id}"
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        self._output_files = []

        ## Text outputs
        self._output_text = {}

        ## Temp. output
        self.output_dir = self.root + "/tmp"
        output_subdirs = ["/plots", "/bills/graphs", "/bills/parts"]
        for subdir in output_subdirs:
            odir = "%s/%s" % (self.output_dir, subdir)
            if not os.path.exists(odir):
                os.makedirs(odir)

    def init_costs(self):
        self.set_costs_defaults()
        self.set_costs_from_config()

    def generate(self):
        self.load_rental_units()
        self.load_contracts()
        self.load_costs()
        self.split_costs_by_objects()
        # self.add_admin_fee()

        if self.output_object_data:
            self.export_object_output()

        # if self.config["Ausgabe:Plots"]:
        #    generate_plots()

        # self.assign_costs_to_contracts()
        # self.export_contract_output()
        self.create_bills()
        self.finalize_output()

    def create_bills(self):
        total_building_costs = self.get_cost_sum()
        for contract in self.contracts:
            bill = NkBill(contract, self.period_end.date(), self.dry_run)
            bill.set_templates(
                self.config["Vorlage:Abrechnung"],
                self.config["Vorlage:EmpfehlungAkonto"],
            )
            filename = f"Nebenkosten-{contract.get_ru_list_string()}-{contract}.pdf"
            bill.set_output_filename(
                self.get_output_filename(
                    f"bills/{filename}",
                    filename,
                    "Abrechnungen",
                    regeneration_data=bill.get_regeneration_data(),
                )
            )
            try:
                bill.create(self.costs, total_building_costs, self.get_context())
                self.log.append(
                    "Did accounting on server and got QR-Bill: %s" % bill.output_pdf_filename
                )
            except Exception as e:
                self.log.append(
                    "Konnte Abrechnung für Vertrag %s nicht erstellen: %s: %s"
                    % (contract, e.__class__.__name__, e)
                )
                raise RuntimeError(
                    f"Konnte QR-Rechnung/Buchungen nicht erzeugen.\n\n{self.get_log_tail(5)}"
                )

    def get_context(self):
        billing_period = (
            f"{self.period_start.strftime('%d.%m.%Y')} – {self.period_end.strftime('%d.%m.%Y')}"
        )
        return {
            "betreff": f"Nebenkostenabrechnung {billing_period}",
            "billing_period": billing_period,
            "billing_period_start": self.period_start.strftime("%Y-%m-%d"),
            "billing_period_end": self.period_end.strftime("%Y-%m-%d"),
            "s_chft": nformat(self.get_cost_sum()),  # sum of total costs
            "num_months": self.num_months,
            "num_months_passed": self.num_months_passed,
        }

    def get_cost_sum(self, section=None, ru=None, value_type=NkCostValueType.COST):
        if section and ru:
            raise ValueError("section and ru cannot be specified at the same time")
        ret = 0
        for cost in self.costs:
            if ru:
                ret += cost.rental_unit_values[ru.id][value_type].amount
            elif section:
                ret += cost.section_values[section.id][value_type].amount
            else:
                ret += cost.total_values[value_type].amount
        return ret

    def finalize_output(self):
        self.text_output("Log", "Rohdaten", "\n".join(self.log))
        self.add_output_to_report()
        # self.delete_temp_files()

    def get_status_message(self):
        warnings = self.get_warnings()
        if warnings:
            return "Nebenkostenabrechung mit WARNUNGEN erstellt:\n\n" + "\n".join(warnings)
        else:
            return "Nebenkostenabrechnung erstellt"

    def load_rental_units(self):
        self._init_virtual_rental_units()
        units = RentalUnit.objects.filter(active=True).order_by("name")
        if self.config["Liegenschaften"]:
            building_ids = [
                int(x) for x in json.loads(self.config["Liegenschaften"].replace("'", '"'))
            ]
            units = units.filter(building__in=building_ids)
        for unit in units:
            try:
                self.rental_units.append(NkRentalUnit.from_rental_unit(unit, self))
            except ValueError as e:
                self.log.append(
                    f'WARNUNG: Ignoriere Objekt "{unit.name}" wegen fehlenden Daten: {e}'
                )
                self.add_warning(f"Ignoriere Objekt wegen fehlenden Daten: {e}", unit.name)
        self._update_virtual_rental_units()

    def _init_virtual_rental_units(self):
        self.rental_units.extend(
            [
                # "Virtual" rental unit to collect "Allgemeinkosten"
                NkRentalUnit(
                    id=-1, name="allg", is_virtual=True, section=get_section_by_id("allgemein")
                ),
                # "Virtual" rental unit to collect "Pauschale NK"
                NkRentalUnit(
                    id=-2, name="pauschal", is_virtual=True, section=get_section_by_id("lager")
                ),
                # "Virtual" rental unit to collect "Pauschale Strom"
                NkRentalUnit(
                    id=-3,
                    name="strom_pauschal",
                    is_virtual=True,
                    section=get_section_by_id("lager"),
                ),
            ]
        )

    def _update_virtual_rental_units(self):
        total_nk_pauschal = 0
        total_strom_pauschal = 0
        for ru in self.rental_units:
            if not ru.is_virtual and ru.nk_pauschal:
                total_nk_pauschal += ru.nk_pauschal
            if not ru.is_virtual and ru.strom_pauschal:
                total_strom_pauschal += ru.strom_pauschal
        # Add NK/Strom pauschal to corresponding virtual rental unit
        self.get_rental_unit_by_id(-2).nk_pauschal = total_nk_pauschal
        self.get_rental_unit_by_id(-3).strom_pauschal = total_strom_pauschal
        # self.get_rental_unit_by_id(-2).akonto = total_nk_pauschal
        # self.get_rental_unit_by_id(-3).akonto = total_strom_pauschal

    def load_contracts(self):
        date_overlap = Q(date__lte=self.period_end) & (
            Q(date_end__isnull=True) | Q(date_end__gte=self.period_start)
        )
        billing_date_overlap = Q(billing_date_start__lte=self.period_end) & (
            Q(billing_date_end__isnull=True) | Q(billing_date_end__gte=self.period_start)
        )
        contracts = (
            Contract.objects.filter(state__in=("unterzeichnet", "gekuendigt"))
            .filter(main_contract=None)
            .filter(date_overlap | billing_date_overlap)
        )
        for contract in contracts:
            try:
                obj = NkContract.from_contract(contract, self.period_start, self.period_end)
                self.contracts.append(obj)
                for ru in contract.rental_units.all():
                    if contract.billing_contract:
                        ## Contract is linked to a billing contract, so add the billing contract
                        ## to the rental unit
                        self.get_rental_unit_by_id(ru.id).add_contract_id(
                            contract.billing_contract.id
                        )
                    else:
                        self.get_rental_unit_by_id(ru.id).add_contract_id(contract.id)
            except ValueError as e:
                self.log.append(
                    f'WARNUNG: Ignoriere Vertrag "{contract.id}" wegen fehlenden Daten: {e}'
                )
                self.add_warning(f"Ignoriere Vertrag wegen fehlenden Daten: {e}", contract)
        # Also add rental units to contracts (for easier access when creating bills)
        for ru in self.rental_units:
            for contract_id in ru.get_contracts_ids():
                self.get_contract_by_id(contract_id).add_rental_unit(ru)
        self._load_virtual_contracts()

    def _load_virtual_contracts(self):
        for virtual_id, name in self.virtual_contracts.items():
            contract = NkContract(
                id=int(virtual_id),
                name=name,
                is_virtual=True,
                date_start=self.period_start,
                date_end=self.period_end,
            )
            self.contracts.append(contract)

    def assign_rental_unit_months_to_contracts(self):
        for ru in self.rental_units:
            if ru.is_virtual:
                continue
            for idx, date in enumerate(self.dates):
                active_contract = self._get_active_contract(date["start"])
                if not active_contract:
                    ## Assign to a virtual contract
                    active_contract = self._get_virtual_contract(ru)
                if not active_contract.period_start:
                    active_contract.period_start = date["start"]
                if not active_contract.period_end or date["end"] > active_contract.period_end:
                    active_contract.period_end = date["end"]
                active_contract.assign_month(idx, ru)

    def _get_active_contract(self, date: datetime):
        active_contract = None
        for contract in self.contracts:
            if not contract.is_virtual and contract.is_active_on(date):
                if active_contract:
                    raise ValueError(
                        f"Multiple active contracts on {date}: {active_contract} and {contract}"
                    )
                active_contract = contract
        return active_contract

    def _get_virtual_contract(self, ru):
        if ru.name in self.virtual_contracts_map:
            contract_id = self.virtual_contracts_map[ru.name]
        elif ru.is_allgemein:
            contract_id = -5  # Allgemein
        else:
            contract_id = -6  # Leerstand
        return self.get_contract_by_id(contract_id)

    def load_costs(self):
        ## Create cost objects from report config
        for cost_config in get_costs_from_config():
            cost_obj = cost_config.cost_class(self, cost_config.config)
            self.costs.append(cost_obj)
        ## Load cost data from report input data
        for cost in self.costs:
            cost.load_input_data()

    def split_costs_by_objects(self):
        for cost in self.costs:
            cost.split_costs()

    def export_object_output(self):
        exporter = ExportCSV(self)
        exporter.export()
        self.log.append("Output is in %s" % exporter.filename)

    def set_costs_defaults(self):
        defaults = {
            "category": "hauswart",
            "time_period": "yearly",
            "monthly_weights": "default",
            "amount": None,
            "section_weights": "default",
            "object_weights": "area",
        }
        for cost in self.costs:
            for name, value in defaults.items():
                if name not in cost:
                    cost[name] = value
            cost["cost_split"] = {"total": {}, "sections": {}, "objects": {}}

    def set_costs_from_config(self):
        remove_costs = []
        for i, cost in enumerate(self.costs):
            if (
                cost.get("amount_data")
                or cost.get("amount_meta")
                or cost.get("amount_from_objects")
            ):
                continue
            if cost["name"].endswith("_Grundkosten"):
                opt_name = cost["name"][:-12]
            elif cost["name"].endswith("_Verbrauch"):
                opt_name = cost["name"][:-10]
            else:
                opt_name = cost["name"]
            amount = self.config.get(f"Kosten:{opt_name}")
            if amount:
                cost["amount"] = amount
            else:
                self.add_warning("Ignoriere Kostenstelle, da keine Kosten definiert", opt_name)
                remove_costs.append(i)
            if cost["name"] == "Wasser_Abwasser_Verbrauch":
                cost["scale_to_total_usage"] = self.config["Messdaten:Wasserverbrauch"]
        for i in remove_costs:
            del self.costs[i]

    def delete_temp_files(self):
        try:
            shutil.rmtree(self.output_dir)
        except Exception:
            self.add_warning("Konnte temporäre Dateien nicht löschen", self.output_dir)

    def text_output(self, name, group, text):
        if name not in self._output_text:
            self._output_text[name] = {"group": group, "lines": [text]}
        else:
            self._output_text[name]["lines"].append(text)

    def get_output_filename(self, filename, name, group, regeneration_data=None):
        temp_out_file = f"{self.output_dir}/{filename}"
        self._output_files.append(
            {
                "temp_file": temp_out_file,
                "name": name,
                "group": group,
                "regeneration_data": regeneration_data,
            }
        )
        return temp_out_file

    @classmethod
    def get_group_name(cls, group):
        group_prefix = {
            "Übersicht": "A",
            "Manuelle Weiterverrechnung": "B",
            "Abrechnungen": "C",
            "Rohdaten": "D",
        }
        prefix = group_prefix.get(group)
        if prefix:
            return f"[{prefix}] {group}"
        return group

    def add_output_to_report(self):
        self.add_output_files_to_report()
        self.add_output_texts_to_report()

    def add_output_files_to_report(self, update=False):
        for outfile in self._output_files:
            filename = os.path.basename(outfile["temp_file"])
            ext = os.path.splitext(filename)[1][1:]
            if outfile["temp_file"].startswith(self.output_dir):
                ## Move temporary file
                os.replace(outfile["temp_file"], f"{self.root}/{filename}")
            else:
                raise ValueError(f"Output file with invalid path: {outfile['temp_file']}")
            output = None
            if update:
                self.log.append(f"Updating output file {filename}.")
                try:
                    output = ReportOutput.objects.get(name=outfile["name"], report=self.report)
                except ReportOutput.DoesNotExist:
                    self.log.append("No ReportOutput object to update found!.")
            if not output:
                output = ReportOutput(
                    name=outfile["name"],
                    group=self.get_group_name(outfile["group"]),
                    report=self.report,
                    output_type=ext,
                )
            output.value = filename
            if outfile["regeneration_data"]:
                output.regeneration_json = json.dumps(outfile["regeneration_data"])
            output.save()

    def add_output_texts_to_report(self):
        for name, text in self._output_text.items():
            output = ReportOutput(
                name=name,
                group=self.get_group_name(text["group"]),
                report=self.report,
                output_type="text",
                value="\n".join(text["lines"]),
            )
            output.save()

    def update_report_output(self):
        self.add_output_files_to_report(update=True)

    def init_dates(self):
        dates = []
        for m in range(self.num_months):
            month = self.start_month + m
            if month > 12:
                year = self.start_year + 1
                month -= 12
            else:
                year = self.start_year
            start_date = datetime(year, month, 1)
            if start_date < datetime.now():
                self.num_months_passed += 1

            next_month = month + 1
            if next_month > 12:
                next_month_year = year + 1
                next_month -= 12
            else:
                next_month_year = year
            end_date = datetime(next_month_year, next_month, 1) + timedelta(days=-1)

            dates.append({"start": start_date, "end": end_date})
        return dates

    @property
    def sections(self):
        return NK_SECTIONS

    @property
    def period_start(self):
        return self.dates[0]["start"]

    @property
    def period_end(self):
        return self.dates[-1]["end"]

    @property
    def period_name(self):
        first_year = self.period_start.year
        last_year = self.period_end.year
        if first_year == last_year:
            return f"{first_year}"
        return f"{first_year}-{last_year}"

    @property
    def period_string(self):
        return "%s-%s" % (
            self.period_start.strftime("%d.%m.%Y"),
            self.period_end.strftime("%d.%m.%Y"),
        )

    def get_contract_by_id(self, contract_id):
        for contract in self.contracts:
            if contract.id == contract_id:
                return contract
        raise ValueError(f"Rental unit with id {contract_id} not found")

    def get_rental_unit_by_id(self, ru_id):
        for unit in self.rental_units:
            if unit.id == ru_id:
                return unit
        raise ValueError(f"Rental unit with id {ru_id} not found")

    def get_rental_unit_by_name(self, name):
        for unit in self.rental_units:
            if unit.name == name:
                return unit
        raise ValueError(f"Rental unit with name {name} not found")

    # def get_costs(self):
    #    return self._costs.as_list()

    def load_saved_data(self):
        filename = f"{self.root}/Rohdaten.json"
        with open(filename) as f:
            data = json.load(f, cls=JSONDecoderDatetime)
        for dataset in data:
            setattr(self, dataset, data[dataset])
        if "cost_indices" not in data:
            for i in range(len(self.costs)):
                self.cost_indices[self.costs[i]["name"]] = i
        if not isinstance(self.active_contracts[0], str):
            self.active_contracts = list(map(str, self.active_contracts))

    def load_previous_data(self):
        period_name = self.config.get("Vorperiode:Bezeichnung", None)
        if period_name:
            with open(self.config["Vorperiode:Datei"]) as f:
                self.previous_data[period_name] = json.load(f, cls=JSONDecoderDatetime)
            if not isinstance(self.previous_data[period_name]["active_contracts"][0], str):
                self.previous_data[period_name]["active_contracts"] = list(
                    map(str, self.previous_data[period_name]["active_contracts"])
                )

    def get_log_tail(self, lines=5):
        log = f"== Letzte {lines} Zeilen des Logs: ==\n"
        log += "\n".join(self.log[-lines:])
        return log
