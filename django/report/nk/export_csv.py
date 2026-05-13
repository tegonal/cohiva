import csv
from operator import add

from geno.utils import nformat


class ExportCSV:
    def __init__(self, nk_generator, filename=None):
        self.filename = None
        self.nk = nk_generator
        # output_filename = nk.get_output_filename(
        #    "Abrechnung.csv", "NK-Abrechnung Übersicht", "Übersicht"
        # )
        self.include_monthly = False
        self.include_percent = False
        self.cost_rows = []
        self.weight_rows = []
        self.footers = {}

    def export(self):
        if not self.filename:
            self.filename = self.nk.get_output_filename(
                "Abrechnung.csv", "NK-Abrechnung Übersicht", "Übersicht"
            )
        self.get_data()
        self.calc_footers()
        self.write()

    def write(self):
        with open(self.filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.get_header())
            for row in self.cost_rows:
                row[1:] = list(map(self.format_amount, row[1:]))
                writer.writerow(row)
            writer.writerow([])
            writer.writerow(self.footers["nominal_akonto"])
            writer.writerow(self.footers["nominal_nk_pauschal"])
            writer.writerow(self.footers["nominal_strom_pauschal"])
            writer.writerow(self.footers["nominal_total"])
            writer.writerow([])
            writer.writerow(self.footers["total_reduced"])
            writer.writerow(self.footers["nominal_diff_reduced"])
            writer.writerow([])
            writer.writerow(self.footers["total"])
            writer.writerow(self.footers["nominal_diff"])
            writer.writerow([])
            # writer.writerow(self.footers["nominal_diff_percent"])
            writer.writerow([])
            self.write_object_extra_info(writer)
            self.write_cost_extra_info(writer)

            ## Add weights
            writer.writerow([])
            writer.writerow(["GEWICHTE"])
            for row in self.weight_rows:
                writer.writerow(row)

    def get_data(self):
        for cost in self.nk.costs:
            cost_row = cost.get_export_cost_row(include_percent=self.include_percent)
            weight_row = cost.get_export_weight_row(include_percent=self.include_percent)
            self.cost_rows.append(cost_row)
            self.weight_rows.append(weight_row)

    def get_header(self):
        header = ["Kosten", "Total"]
        for s in self.nk.sections:
            header.append(s.name)
            if self.include_percent:
                header.append("%")
        for ru in self.nk.rental_units:
            header.append(ru.name)
            if self.include_percent:
                header.append("%")
        return header

    ## TODO: Refactor / simplify
    def calc_footers(self):
        footer_total = ["Total"]
        footer_total_reduced = ["Total ohne Spezialkosten"]
        footer_nominal = {}
        footer_nominal_items = {
            "akonto": "Akonto nominell",
            "nk_pauschal": "Pauschal nominell",
            "strom_pauschal": "Strom pauschal nominell",
            "total": "Total nominell",
        }
        for attr, name in footer_nominal_items.items():
            footer_nominal[attr] = [name]
        footer_nominal_diff = ["Differenz zu Total nominell"]
        footer_nominal_diff_reduced = ["Differenz zu Total nominell ohne Spezialkosten"]
        # footer_nominal_diff_percent = ['  in Prozent']

        for i, cost in enumerate(self.nk.costs):
            if cost.is_meta:
                ## Exclude meta from totals
                start_index = 2
            else:
                start_index = 1
            if len(footer_total) > 1:
                footer_total[start_index:] = list(
                    map(add, footer_total[start_index:], self.cost_rows[i][start_index:])
                )
                if not cost.is_special:  # not in ("Strom_Total", "Internet/WLAN"):
                    footer_total_reduced[start_index:] = list(
                        map(
                            add,
                            footer_total_reduced[start_index:],
                            self.cost_rows[i][start_index:],
                        )
                    )
            else:
                footer_total[start_index:] = self.cost_rows[i][start_index:]
                if not cost.is_special:  # not in ("Strom_Total", "Internet/WLAN"):
                    footer_total_reduced[start_index:] = self.cost_rows[i][start_index:]

        ## adjust percents
        if self.include_percent:
            for i in range(2, len(footer_total), 2):
                if footer_total[1]:
                    footer_total[i + 1] = footer_total[i] / footer_total[1] * 100.0
                if footer_total_reduced[1]:
                    footer_total_reduced[i + 1] = (
                        footer_total_reduced[i] / footer_total_reduced[1] * 100.0
                    )

        ## Remove allgemein
        for i, head in enumerate(self.get_header()):
            if head == "Allgemein" or head == "0000":
                footer_total[i] = ""
                footer_total_reduced[i] = ""
                if self.include_percent:
                    footer_total[i + 1] = ""
                    footer_total_reduced[i + 1] = ""

        ## Calc akonto etc.
        nominal_obj = {"total": {"sum": 0}}
        for attr in footer_nominal_items:
            if attr == "total":
                continue
            nominal_obj[attr] = {"sum": 0}
            for s in self.nk.sections:
                nominal_obj[attr][s.id] = 0
            for ru in self.nk.rental_units:
                if ru.id not in nominal_obj["total"]:
                    nominal_obj["total"][ru.id] = 0
                if ru.section.id not in nominal_obj["total"]:
                    nominal_obj["total"][ru.section.id] = 0
                nominal_obj[attr][ru.id] = getattr(ru, attr)
                nominal_obj["total"][ru.id] += getattr(ru, attr)
                if not ru.is_virtual:
                    # Don't include virtual units in section totals
                    # so that they are not counted twice
                    nominal_obj[attr][ru.section.id] += getattr(ru, attr)
                    nominal_obj[attr]["sum"] += getattr(ru, attr)
                    nominal_obj["total"][ru.section.id] += getattr(ru, attr)
                    nominal_obj["total"]["sum"] += getattr(ru, attr)

        for attr in footer_nominal_items:
            footer_nominal[attr].append(nominal_obj[attr]["sum"])
            for s in self.nk.sections:
                footer_nominal[attr].append(nominal_obj[attr][s.id])
                if self.include_percent:
                    footer_nominal[attr].append("")  # No percent
            for ru in self.nk.rental_units:
                footer_nominal[attr].append(nominal_obj[attr][ru.id])
                if self.include_percent:
                    footer_nominal[attr].append("")  # No percent

        # Difference
        footer_nominal_diff.append(footer_nominal["total"][1] - footer_total[1])
        footer_nominal_diff_reduced.append(footer_nominal["total"][1] - footer_total_reduced[1])
        if self.include_percent:
            stride = 2
        else:
            stride = 1
        for i in range(2, len(footer_total), stride):
            if footer_total[i] != "" and footer_nominal["total"][i] != "":
                footer_nominal_diff.append(footer_nominal["total"][i] - footer_total[i])
                if self.include_percent:
                    if footer_nominal["total"][i]:
                        footer_nominal_diff.append(
                            footer_nominal_diff[i] / footer_nominal["total"][i] * 100
                        )
                    else:
                        footer_nominal_diff.append("")
            else:
                footer_nominal_diff.append("")
                if self.include_percent:
                    footer_nominal_diff.append("")
            if footer_total_reduced[i] != "" and footer_nominal["total"][i] != "":
                footer_nominal_diff_reduced.append(
                    footer_nominal["total"][i] - footer_total_reduced[i]
                )
                if self.include_percent:
                    if footer_nominal["total"][i]:
                        footer_nominal_diff_reduced.append(
                            footer_nominal_diff_reduced[i] / footer_nominal["total"][i] * 100
                        )
                    else:
                        footer_nominal_diff_reduced.append("")
            else:
                footer_nominal_diff_reduced.append("")
                if self.include_percent:
                    footer_nominal_diff_reduced.append("")

        footer_total[1:] = list(map(self.format_amount, footer_total[1:]))
        footer_total_reduced[1:] = list(map(self.format_amount, footer_total_reduced[1:]))
        for attr in footer_nominal_items:
            footer_nominal[attr][1:] = list(map(self.format_amount, footer_nominal[attr][1:]))
        footer_nominal_diff[1:] = list(map(self.format_amount, footer_nominal_diff[1:]))
        footer_nominal_diff_reduced[1:] = list(
            map(self.format_amount, footer_nominal_diff_reduced[1:])
        )

        ## Remove totals from reduced, because it does not work with Allgemeinstromanteile
        footer_total_reduced[1] = ""
        footer_nominal_diff_reduced[1] = ""

        for attr in footer_nominal_items:
            self.footers[f"nominal_{attr}"] = footer_nominal[attr]
        self.footers["total_reduced"] = footer_total_reduced
        self.footers["nominal_diff_reduced"] = footer_nominal_diff_reduced
        self.footers["total"] = footer_total
        self.footers["nominal_diff"] = footer_nominal_diff

    ## TODO: Refactor / simplify
    def write_object_extra_info(self, writer):
        ## Additional information
        row = []
        row.append("Raumtyp")
        row.append("")
        for s in self.nk.sections:
            row.append(s.name)
            if self.include_percent:
                row.append("")
        for ru in self.nk.rental_units:
            row.append(ru.section.name)
            if self.include_percent:
                row.append("")
        writer.writerow(row)
        for field in ("rooms", "min_occupancy"):
            row = []
            row.append(field)
            row.append("")
            for _s in self.nk.sections:
                row.append("")
                if self.include_percent:
                    row.append("")
            for ru in self.nk.rental_units:
                row.append(getattr(ru, field))
                if self.include_percent:
                    row.append("")
            writer.writerow(row)

    ## TODO: Refactor / simplify
    def write_cost_extra_info(self, writer):
        for cost in self.nk.costs:
            lines = cost.get_export_extra_info(self.include_percent, self.format_amount)
            if lines:
                writer.writerow([])
                writer.writerow([f"{cost.name} Zusatzinfos:"])
                writer.writerows(lines)
                writer.writerow([])

    @staticmethod
    def format_amount(amount):
        if amount == "":
            return amount
        return nformat(amount, round_to=0.05)
