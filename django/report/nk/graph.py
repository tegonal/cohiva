import os

import matplotlib.pyplot as plt
import numpy as np

## Energy plot (pip install plotly kaleido)
import plotly.graph_objects as go
import plotly.io as pio
from django.conf import settings

from geno.utils import nformat

pio.kaleido.scope.mathjax = None


class NkGraph:
    def __init__(self, file_prefix, period_name=None, previous_period_name=None):
        self.file_prefix = file_prefix
        self.period_name = period_name or "Aktuelle Periode"
        self.previous_period_name = previous_period_name or "Vorherige Periode"

    def create_energy_consumption_graph(self, context):
        output_filename = f"{self.file_prefix}_energy_graph.pdf"
        data = context["energy_consumption_data"]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=["Heizung", "Warmwasser", "Strom"],
                y=[100, 100, 100],
                name="Alle Wohnungen (pro 100 m²)",
                text=[
                    "%s kWh" % nformat(data["Heizung"]["total_sect"], 0),
                    "%s m³" % nformat(data["Warmwasser"]["total_sect"], 0),
                    "%s kWh" % nformat(data["Strom"]["total_sect"], 0),
                ],
                marker_color="white",
                marker_line_color="black",
                marker_line_width=0.8,
            )
        )
        percent_heizung = data["Heizung"]["unit"] / data["Heizung"]["total_sect"] * 100
        percent_ww = data["Warmwasser"]["unit"] / data["Warmwasser"]["total_sect"] * 100
        percent_strom = data["Strom"]["unit"] / data["Strom"]["total_sect"] * 100
        diff_percent_heizung = percent_heizung - 100
        if diff_percent_heizung >= 0:
            diff_percent_heizung_str = "+%s" % nformat(diff_percent_heizung, 0)
        else:
            diff_percent_heizung_str = "%s" % nformat(diff_percent_heizung, 0)
        diff_percent_ww = percent_ww - 100
        if diff_percent_ww >= 0:
            diff_percent_ww_str = "+%s" % nformat(diff_percent_ww, 0)
        else:
            diff_percent_ww_str = "%s" % nformat(diff_percent_ww, 0)
        diff_percent_strom = percent_strom - 100
        if diff_percent_strom >= 0:
            diff_percent_strom_str = "+%s" % nformat(diff_percent_strom, 0)
        else:
            diff_percent_strom_str = "%s" % nformat(diff_percent_strom, 0)

        fig.add_trace(
            go.Bar(
                x=["Heizung", "Warmwasser", "Strom"],
                y=[percent_heizung, percent_ww, percent_strom],
                name="%s Verbrauch (pro 100 m²)" % context["Euer"],
                text=[
                    "%s kWh<br>%s%%"
                    % (nformat(data["Heizung"]["unit"], 0), diff_percent_heizung_str),
                    "%s m³<br>%s%%"
                    % (nformat(data["Warmwasser"]["unit"], 0), diff_percent_ww_str),
                    "%s kWh<br>%s%%" % (nformat(data["Strom"]["unit"], 0), diff_percent_strom_str),
                ],
                marker_color="black",
            )
        )

        fig.update_yaxes(title_text="Relativer Verbrauch in Prozent")
        fig.update_layout(
            font_family=settings.COHIVA_TEXT_FONT,
            font_size=16,
            font_color="black",
            title={
                "text": "%s Energieverbrauch im Vergleich" % context["Euer"],
                "font": {
                    "family": settings.COHIVA_TITLE_FONT,
                    "size": 30,
                },
            },
        )

        fig.write_image(output_filename)
        if not os.path.isfile(output_filename):
            raise RuntimeError(f"Could not write {output_filename}")
        return output_filename

    def create_energy_timeseries_graph(self, data, output_filename, context, extra_text=None):
        data_x = []
        data_y_prev = []
        data_y = []
        text_prev = []
        text = []
        percent_heizung_prev = 0
        percent_heizung = 0
        if "Heizung" in data:
            if data["Heizung"]["prev"]:
                percent_heizung_prev = 100
                percent_heizung = data["Heizung"]["curr"] / data["Heizung"]["prev"] * 100
            elif data["Heizung"]["curr"]:
                percent_heizung = 100
        if percent_heizung_prev or percent_heizung:
            diff_percent_heizung = percent_heizung - 100
            if diff_percent_heizung >= 0:
                diff_percent_heizung_str = "+%s" % nformat(diff_percent_heizung, 0)
            else:
                diff_percent_heizung_str = "%s" % nformat(diff_percent_heizung, 0)
            data_x.append("Heizung*")
            data_y_prev.append(percent_heizung_prev)
            data_y.append(percent_heizung)
            text_prev.append("%s kWh" % nformat(data["Heizung"]["prev"], 0))
            text.append(
                "%s kWh<br>%s%%" % (nformat(data["Heizung"]["curr"], 0), diff_percent_heizung_str)
            )

        percent_ww_prev = 0
        percent_ww = 0
        if data["Warmwasser"]["prev"]:
            percent_ww_prev = 100
            percent_ww = data["Warmwasser"]["curr"] / data["Warmwasser"]["prev"] * 100
        else:
            if data["Warmwasser"]["curr"]:
                percent_ww = 100
        if percent_ww_prev or percent_ww:
            diff_percent_ww = percent_ww - 100
            if diff_percent_ww >= 0:
                diff_percent_ww_str = "+%s" % nformat(diff_percent_ww, 0)
            else:
                diff_percent_ww_str = "%s" % nformat(diff_percent_ww, 0)
            data_x.append("Warmwasser")
            data_y_prev.append(percent_ww_prev)
            data_y.append(percent_ww)
            text_prev.append("%s m³" % nformat(data["Warmwasser"]["prev"], 0))
            text.append(
                "%s m³<br>%s%%" % (nformat(data["Warmwasser"]["curr"], 0), diff_percent_ww_str)
            )

        percent_strom_prev = 0
        percent_strom = 0
        if data["Strom"]["prev"]:
            percent_strom_prev = 100
            percent_strom = data["Strom"]["curr"] / data["Strom"]["prev"] * 100
        else:
            if data["Strom"]["curr"]:
                percent_strom = 100
        if percent_strom_prev or percent_strom:
            diff_percent_strom = percent_strom - 100
            if diff_percent_strom >= 0:
                diff_percent_strom_str = "+%s" % nformat(diff_percent_strom, 0)
            else:
                diff_percent_strom_str = "%s" % nformat(diff_percent_strom, 0)

            data_x.append("Strom")
            data_y_prev.append(percent_strom_prev)
            data_y.append(percent_strom)
            text_prev.append("%s kWh" % nformat(data["Strom"]["prev"], 0))
            text.append(
                "%s kWh<br>%s%%" % (nformat(data["Strom"]["curr"], 0), diff_percent_strom_str)
            )

        # if "Vorperiode:Bezeichnung" in nk.config:
        if self.previous_period_name:
            if "months_prev" in data:
                name_prev_txt = f"Periode {self.previous_period_name}"
                name_prev_txt = "%s (%s Mte.)" % (name_prev_txt, data["months_prev"])
        name_txt = f"Periode {self.period_name}"
        if "months" in data:
            name_txt = "%s (%s Mte.)" % (name_txt, data["months"])

        if not data_x:
            return

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=data_x,
                y=data_y_prev,
                name=name_prev_txt,
                text=text_prev,
                marker_color="white",
                marker_line_color="black",
                marker_line_width=0.8,
            )
        )

        fig.add_trace(
            go.Bar(
                x=data_x,
                y=data_y,
                name=name_txt,
                text=text,
                marker_color="black",
            )
        )

        #    layout=go.Layout(
        #        annotations=[
        #            go.layout.Annotation(
        #                text='Some<br>multi-line<br>text',
        #                align='left',
        #                showarrow=False,
        #                xref='paper',
        #                yref='paper',
        #                x=1.1,
        #                y=0.8,
        #                bordercolor='black',
        #                borderwidth=1
        #            )
        #        ]
        #    )
        if extra_text:
            fig.add_annotation(
                text=extra_text,
                align="left",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=-0.12,
                y=-0.15,
            )

        fig.update_yaxes(title_text="Relativer Verbrauch in Prozent")
        fig.update_layout(
            font_family=settings.COHIVA_TEXT_FONT,
            font_size=16,
            font_color="black",
            title={
                "text": context["graph_title"],
                "font": {
                    "family": settings.COHIVA_TITLE_FONT,
                    "size": 30,
                },
            },
        )

        fig.write_image(output_filename)
        if not os.path.isfile(output_filename):
            raise RuntimeError(f"Could not write {output_filename}")


class NkOverviewGraph:
    def __init__(self, categories, costs, rental_units, log, get_output_filename_function):
        self.categories = categories
        self.rental_units = rental_units
        self.costs = costs
        self.log = log
        self.get_output_filename = get_output_filename_function

    @classmethod
    def create_plots(cls, nk):
        # for o in nk.objects:
        #    ## Kosten in Prozent der Nettomiete, nach verbrauchsunabh, verbrauchsabh, Strom, Internet
        #    if o['name'] == '011':
        #        for key in o:
        #            nk.log.append(" - %s: %s" % (key, o[key]))
        graph = NkOverviewGraph(nk)
        graph.plot(
            {
                "relative_key": "rent_net",
                "ylabel": "% der Nettomiete",
                "sorted": True,
                "anon": False,
                "diff_relative": True,
            }
        )
        graph.plot(
            {
                "relative_key": "area",
                "ylabel": "CHF pro 100m2 Fläche",
                "sorted": True,
                "anon": False,
                "diff_relative": False,
            }
        )

    def plot(self, spec):
        data = {
            "Wohnen": [],
            "Gewerbe": [],
            "Lager": [],
        }
        for sect in data:
            for _cat in self.categories:
                data[sect].append([])
        data_extra = {
            "Wohnen": {
                "akonto": [],
                "total": [],
                "akonto_amount": [],
                "total_amount": [],
                "reduced_amount": [],
                "relative_quantity": [],
                "obj": [],
            },
            "Gewerbe": {
                "akonto": [],
                "total": [],
                "akonto_amount": [],
                "total_amount": [],
                "reduced_amount": [],
                "relative_quantity": [],
                "obj": [],
            },
            "Lager": {
                "akonto": [],
                "total": [],
                "akonto_amount": [],
                "total_amount": [],
                "reduced_amount": [],
                "relative_quantity": [],
                "obj": [],
            },
        }
        for o in self.rental_units:
            if o["name"] in ("0000", "9998", "9999"):
                continue
            obj_relative_key = o[spec["relative_key"]]
            if not obj_relative_key:
                self.log.append(
                    "Skipping object with no %s: %s" % (spec["relative_key"], o["name"])
                )
                continue
            elif obj_relative_key < 0:
                self.log.append(
                    "Skipping object with negative %s: %s" % (spec["relative_key"], o["name"])
                )
                continue
            # if o['name'] != "011":
            #    continue
            # for key in o:
            #    self.log.append(" - %s: %s" % (key, o[key]))
            cost_bin = len(self.categories) * [0]
            total = 0
            total_amount = 0
            reduced_amount = 0
            for c in self.costs:
                amount = c["cost_split"]["objects"][o["name"]]["annual"]["amount"]
                cost_bin[self.categories[c["category"]]["i"]] += amount / obj_relative_key * 100
                total += amount / obj_relative_key * 100
                total_amount += amount
                if c["name"] not in ("Strom_Total", "Internet/WLAN"):
                    reduced_amount += amount

            if o["section"] in data:
                for cat in self.categories:
                    data[o["section"]][self.categories[cat]["i"]].append(
                        cost_bin[self.categories[cat]["i"]]
                    )
                data_extra[o["section"]]["akonto"].append(o["akonto_obj"] / obj_relative_key * 100)
                data_extra[o["section"]]["relative_quantity"].append(obj_relative_key)
                data_extra[o["section"]]["akonto_amount"].append(o["akonto_obj"])
                data_extra[o["section"]]["obj"].append("_" + o["name"])
                data_extra[o["section"]]["total"].append(total)
                data_extra[o["section"]]["total_amount"].append(total_amount)
                data_extra[o["section"]]["reduced_amount"].append(reduced_amount)
                # if o['name'] == "001":
                #    self.log.append("%s: total=%s total_amount=%s reduced_amount=%s akonto_amount=%s" % (o['name'],total,total_amount,reduced_amount,o['akonto']))

        ## Calculate averages
        grand_total_sum = 0
        grand_total_reduced_sum = 0
        grand_total_rel = 0
        grand_total_akonto_sum = 0
        for sect in data:
            total_sum = sum(data_extra[sect]["total_amount"])
            total_reduced_sum = sum(data_extra[sect]["reduced_amount"])
            total_rel = sum(data_extra[sect]["relative_quantity"])
            total_akonto = sum(data_extra[sect]["akonto_amount"])
            self.log.append(
                "Average total %s %s: %s (%s / %s)"
                % (spec["relative_key"], sect, total_sum / total_rel, total_sum, total_rel)
            )
            self.log.append(
                "Average total_reduced %s %s: %s (%s / %s)"
                % (
                    spec["relative_key"],
                    sect,
                    total_reduced_sum / total_rel,
                    total_reduced_sum,
                    total_rel,
                )
            )
            self.log.append(
                "Average akonto %s %s: %s (%s / %s)"
                % (spec["relative_key"], sect, total_akonto / total_rel, total_akonto, total_rel)
            )
            grand_total_sum += total_sum
            grand_total_reduced_sum += total_reduced_sum
            grand_total_rel += total_rel
            grand_total_akonto_sum += total_akonto
        self.log.append(
            "Average total %s %s: %s (%s / %s)"
            % (
                spec["relative_key"],
                "ALL",
                grand_total_sum / grand_total_rel,
                grand_total_sum,
                grand_total_rel,
            )
        )
        self.log.append(
            "Average total_reduced %s %s: %s (%s / %s)"
            % (
                spec["relative_key"],
                "ALL",
                grand_total_reduced_sum / grand_total_rel,
                grand_total_reduced_sum,
                grand_total_rel,
            )
        )
        self.log.append(
            "Average total_akonto %s %s: %s (%s / %s)"
            % (
                spec["relative_key"],
                "ALL",
                grand_total_akonto_sum / grand_total_rel,
                grand_total_akonto_sum,
                grand_total_rel,
            )
        )

        if spec["anon"]:
            plt.rc("xtick", labelsize=0)
        else:
            plt.rc("xtick", labelsize=8)
        for section in data:
            fig, ax = plt.subplots(figsize=(1.2 * 10, 1.2 * 7))
            x = np.array(data_extra[section]["obj"])
            if spec["sorted"]:
                sort = np.array(data_extra[section]["total"]).argsort()
                x = x[sort]
            for cat in self.categories:
                y = np.array(data[section][self.categories[cat]["i"]])
                if spec["sorted"]:
                    y = y[sort]
                if self.categories[cat]["i"] == 0:
                    # self.log.append(x)
                    # self.log.append(y)
                    ax.bar(x, y, label=self.categories[cat]["label"])
                    y_bottom = y
                else:
                    ax.bar(x, y, bottom=y_bottom, label=self.categories[cat]["label"])
                    y_bottom += y

            akonto = np.array(data_extra[section]["akonto"])
            if spec["sorted"]:
                akonto = akonto[sort]
            ax.step(x, akonto, "k-", label="Akonto", where="mid")

            # fig = Figure(figsize=(10, 7))
            # ax = fig.add_subplot(111)
            # ax.boxplot(np.array(stat), labels=labels)
            # ax.stackplot(np.array(data[section]['obj']), np.array( [ data[section]['base'], data[section]['waerme'], data[section]['strom'], data[section]['internet'] ] ), labels=('Basis', 'Indiv. Verbrauch Wärme/Wasser', 'Strom', 'Internet'))
            plt.xticks(rotation=90)
            ax.set_ylabel(spec["ylabel"])
            # ax.axvline(5.5)
            ax.set_title("Nebenkosten %s pro Mietobjekt" % section)
            ax.legend()
            # ax.grid(axis='y', linestyle=':')
            # canvas = FigureCanvas(fig)
            # output = io.BytesIO()
            tag = ""
            if spec["sorted"]:
                tag = "%s_sorted" % tag
            filename_part = f"{spec['relative_key']}{tag}_{section}"
            if spec["relative_key"] == "area":
                plot_name = f"Grafik: NK pro Fläche ({section})"
            elif spec["relative_key"] == "rent_net":
                plot_name = f"Grafik: NK in % der Nettomiete ({section})"
            filename = self.get_output_filename(
                f"plots/nk_plot_{filename_part}.png", plot_name, "Übersicht"
            )
            # output = open(filename, 'w')
            # canvas.print_png(output)
            # output.close()
            plt.savefig(filename, dpi=300)
            plt.close()
            self.log.append("Plot in %s" % filename)

            ## Differenz zu akonto
            fig, ax = plt.subplots(figsize=(1.2 * 10, 1.2 * 7))
            x = np.array(data_extra[section]["obj"])
            y = np.array(data_extra[section]["total_amount"]) - np.array(
                data_extra[section]["akonto_amount"]
            )
            y2 = np.array(data_extra[section]["reduced_amount"]) - np.array(
                data_extra[section]["akonto_amount"]
            )
            if spec["diff_relative"]:
                y = y / np.array(data_extra[section]["akonto_amount"]) * 100
                y2 = y2 / np.array(data_extra[section]["akonto_amount"]) * 100
            if spec["sorted"]:
                sort = y.argsort()
                x = x[sort]
                y = y[sort]
                y2 = y2[sort]
            ax.bar(x, y, label="Differenz zu Akonto-Zahlungen")
            ax.step(
                x,
                y2,
                "r-",
                label="Differenz zu Akonto-Zahlungen (ohne Strom/Internet)",
                where="mid",
            )
            plt.xticks(rotation=90)
            if spec["diff_relative"]:
                ax.set_ylabel("% der Akontozahlungen")
            else:
                ax.set_ylabel("CHF")

            # ax.axvline(5.5)
            ax.set_title("Nebenkosten %s pro Mietobjekt" % section)
            ax.legend()
            # ax.grid(axis='y', linestyle=':')
            # canvas = FigureCanvas(fig)
            # output = io.BytesIO()
            tag = ""
            if spec["sorted"]:
                tag = "%s_sorted" % tag
            if spec["diff_relative"]:
                plotname = "diff_akonto_relative"
                plot_name = f"Grafik: Differenz zu Akonto in % ({section})"
            else:
                plotname = "diff_akonto"
                plot_name = f"Grafik: Differenz zu Akonto in CHF ({section})"
            filename_part = f"{plotname}{tag}_{section}"
            filename = self.get_output_filename(
                f"plots/nk_plot_{filename_part}.png", plot_name, "Übersicht"
            )
            # output = open(filename, 'w')
            # canvas.print_png(output)
            # output.close()
            plt.savefig(filename, dpi=300)
            plt.close()
            self.log.append("Plot in %s" % filename)
