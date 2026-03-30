import datetime
import os
from collections import OrderedDict

import requests

from cohiva import settings
from cohiva.utils.pdf import PdfGenerator
from geno.utils import fill_template_pod, nformat, odt2pdf
from report.nk.contract import NkContract
from report.nk.cost import NkCost, NkCostValueType
from report.nk.graph import NkGraph


class NkBill:
    def __init__(
        self, contract: NkContract, billing_date: datetime.date, output_dir: str, dry_run=True
    ):
        self.contract = contract
        self.billing_date = billing_date
        self.dry_run = dry_run
        self.output_dir = output_dir
        self.rental_unit_files = []
        self.has_previous_data = False
        self.odt_bill_template = None
        self.odt_akonto_recommendation_template = None
        self.output_pdf_filename = None
        self.akonto_recommendation_pdf_filename = None
        self.akonto_recommendation_qr_filename = None
        self.regenerate_invoice_id = None

    def set_templates(self, bill_template, akonto_recommendation_template=None):
        self.odt_bill_template = bill_template
        self.odt_akonto_recommendation_template = akonto_recommendation_template

    def set_output_filename(self, filename):
        self.output_pdf_filename = filename

    def create(self, costs: list[NkCost], total_building_costs, context: dict = None):
        contract_context = context or {}
        self.contract.update_context(contract_context, costs)
        contract_context["bill_lines"] = []
        for ru in self.contract.rental_units:
            ru_context = contract_context | ru.get_context()
            total_ru_costs = self.contract.get_total_costs(costs, ru)
            ru_context["costs"] = []
            for name, group in self._get_billing_groups(costs).items():
                cost_context = self._get_billing_group_context(
                    name, group, ru, total_building_costs, total_ru_costs
                )
                if cost_context:
                    ru_context["costs"].append(cost_context)
            self.rental_unit_files.append(self._create_rental_unit_files(ru_context, ru))
            contract_context["bill_lines"].append(self._get_bill_line(ru_context))
        if context["total_akonto"]:
            context["bill_lines"].append(
                {
                    "date": self.billing_date.strftime("%d.%m.%Y"),
                    "text": "Abzüglich Akontozahlungen",
                    "total": nformat(context["total_akonto"] * -1),
                }
            )
        self._create_akonto_recommendation(contract_context)
        self._create_final_pdf(contract_context)

    def get_regeneration_data(self):
        if self.dry_run:
            return None
        return {
            "type": "nk_bills",
            "contract_id": self.contract.id,
            "invoice_id": self.regenerate_invoice_id,
        }

    def _create_rental_unit_files(self, context, ru):
        tmp_filename = fill_template_pod(self.odt_bill_template, context, output_format="odt")
        odt_file = "%s/bills/parts/%s_object_%s.odt" % (self.output_dir, self.contract, ru.id)
        os.rename(tmp_filename, odt_file)
        # nk.log.append("Created %s" % filename)

        graph_files = self._create_rental_unit_graphs(context, ru)

        return {"odt_file": odt_file, "graph_files": graph_files}

    def _create_rental_unit_graphs(self, context, ru):
        file_prefix = "%s/bills/graphs/%s_object_%s" % (self.output_dir, self.contract, ru.id)
        graph_files = {}
        graph = NkGraph(file_prefix)
        if self.has_previous_data:
            self._create_timeseries(
                self.contract,
                ru,
                context,
                file_prefix,
            )
        if ru.section == "Wohnen":
            output_filename = graph.create_energy_consumption_graph(context)
            graph_files["energy_consumption_graph"] = output_filename
        return graph_files

    def _create_timeseries(self, contract, ru, context, file_prefix):
        print("TODO: Create timeseries graphs")
        return None

    @classmethod
    def _get_billing_groups(cls, costs: list[NkCost]):
        billing_groups = OrderedDict()
        for cost in costs:
            if cost.billing_group not in billing_groups:
                billing_groups[cost.billing_group] = []
            billing_groups[cost.billing_group].append(cost)
        return billing_groups

    def _get_billing_group_context(
        self, name, group, rental_unit, total_building_cost, total_ru_cost
    ):
        object_cost = 0
        building_cost = 0
        for cost in group:
            object_cost += cost.get_assigned_amount(
                NkCostValueType.COST, self.contract, rental_unit
            )
            building_cost += cost.get_building_amount(NkCostValueType.COST)
        if object_cost == 0 and building_cost == 0:
            return None
        if building_cost:
            share = "%s%%" % nformat(object_cost / building_cost * 100.0, 2)
        else:
            share = "-"
        return {
            "name": name,
            "chft": nformat(building_cost),
            "chf": nformat(object_cost),
            "pctt": nformat(
                building_cost / total_building_cost * 100.0,
                1,
            ),
            "pct": nformat(object_cost / total_ru_cost * 100, 1),
            "share": share,
        }

    def _get_bill_line(self, context):
        return {
            "date": self.billing_date.strftime("%d.%m.%Y"),
            "text": f"Nebenkosten {context['ru_label']}",
            "total": context["s_chf"],
        }

    def _create_akonto_recommendation(self, context):
        if (
            context["total_amount"] <= 0
            or context["total_akonto"] <= 0
            and context["total_amount"] / context["total_akonto"]
            <= context["akonto_threshold"] / 100
        ):
            # No recommendation needed.
            return

        tmp_filename = fill_template_pod(
            self.odt_akonto_recommendation_template, context, output_format="odt"
        )
        filename = "%s/bills/parts/%s_EmpfehlungAkonto.odt" % (self.output_dir, self.contract)
        os.rename(tmp_filename, filename)
        self.akonto_recommendation_pdf_filename = odt2pdf(filename)

        qr_pdf_akonto = self._get_akonto_qrbill(context)
        if not qr_pdf_akonto:
            raise RuntimeError("Konnte QR-Rechnung für Akonto-Empfehlung nicht erstellen")
        self.akonto_recommendation_qr_filename = "%s/bills/parts/%s_QR-Zusatzzahlung.pdf" % (
            self.output_dir,
            self.contract,
        )
        with open(self.akonto_recommendation_qr_filename, "wb") as outfile:
            outfile.write(qr_pdf_akonto)

    def _create_final_pdf(self, context):
        # Put everything together.
        # 1. Bill with QR-Code
        # 2. Detail pages per object, including plots
        # 3. Additional payment info (if applicable)

        pdfgen = PdfGenerator()
        pdfgen.append_pdf_file(self._create_qr_bill(context))

        for ru_files in self.rental_unit_files:
            pdfgen.append_pdf_file(
                odt2pdf(ru_files["odt_file"]),
                merge_pdfs_on_last_page=ru_files.get("graph_files", []),
                transform={"tx": 60, "ty": 560, "dy": -250, "scale": 0.7},
            )

        if self.akonto_recommendation_pdf_filename:
            pdfgen.append_pdf_file(
                self.akonto_recommendation_pdf_filename, self.akonto_recommendation_qr_filename
            )

        pdfgen.write_file(self.output_pdf_filename)

    def _create_qr_bill(self, context):
        qr_pdf = self._get_qrbill(context)
        qr_pdf_filename = "%s/bills/parts/%s_QR-Rechnung.pdf" % (self.output_dir, self.contract)
        with open(qr_pdf_filename, "wb") as outfile:
            outfile.write(qr_pdf)
        return qr_pdf_filename

    def _get_akonto_qrbill(self, context):
        return self._get_qrbill(context, True)

    def _get_qrbill(self, context, get_akonto_qrbill=False):
        # TODO?: Create QRBill directly instead of going through the REST API
        headers = {"Authorization": "Token " + settings.COHIVA_REPORT_API_TOKEN}
        request_data = context.copy()
        if get_akonto_qrbill:
            request_data["get_akonto_qrbill"] = True
        if not self.dry_run:
            request_data["dry_run"] = False
        response = requests.post(
            settings.BASE_URL + "/api/v1/geno/qrbill/", json=request_data, headers=headers
        )
        if response.status_code != 200:  # not response.ok:
            raise RuntimeError(
                f"qrbill API returned: {response.status_code} {response.reason} / {response.text}"
            )
        if response.headers["Content-Type"] != "application/pdf":
            raise RuntimeError(
                f"qrbill API returned {response.headers['Content-Type']} "
                "instead of application/pdf data."
            )
        return response.content
