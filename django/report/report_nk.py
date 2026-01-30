import copy
import csv
import io
import json

## Creating odt documents
import os
import re
import shutil
import tempfile
import zipfile
from collections import OrderedDict
from datetime import datetime, timedelta
from operator import add

## PDF tools
from subprocess import PIPE, Popen

import matplotlib.pyplot as plt

## Plots
import numpy as np

## Energy plot (pip install plotly kaleido)
import plotly.graph_objects as go
import plotly.io as pio
import requests
from appy.pod.renderer import Renderer
from django.conf import settings

from cohiva.utils.pdf import PdfGenerator
from geno.models import Invoice, InvoiceCategory, RentalUnit
from geno.utils import JSONDecoderDatetime, JSONEncoderDatetime
from report.models import ReportOutput

pio.kaleido.scope.mathjax = None


## API access
BASE_URI = settings.BASE_URL + "/api/v1"
API_TOKEN = settings.COHIVA_REPORT_API_TOKEN


def sum_if_list(values):
    try:
        return sum(values)
    except TypeError:
        return values


def fill_template_pod(template_file, context, output_format="odt"):
    tmpdir = nk.output_dir + "/nk_pod"
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)
    tmp_file = tempfile.NamedTemporaryFile(
        suffix=".%s" % output_format, prefix="nk_pod_", dir=tmpdir, delete=False
    )
    renderer = Renderer(
        template_file, context, tmp_file.name, overwriteExisting=True, metadata=False
    )
    renderer.run()

    return tmp_file.name


def odt2pdf(odtfile):
    tmpdir = nk.output_dir + "/odt2pdf"
    soffice_bin = "/usr/lib/libreoffice/program/soffice.bin"

    # my $file = shift;
    # my $stamp = shift;

    path, basename = os.path.split(odtfile)
    outfile = os.path.splitext(basename)

    cmd = [
        soffice_bin,
        #'--headless',
        "-env:UserInstallation=file://%s" % tmpdir,
        "--convert-to",
        "pdf:writer_pdf_Export",
        "--outdir",
        "%s" % path,
        "%s" % odtfile,
    ]
    # print cmd
    # ret = subprocess.call(cmd)
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    if p.returncode or len(err):
        if not os.path.isdir("%s/user/config/soffice.cfg" % tmpdir):
            ## Work around startup problems by trying again
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            if p.returncode or len(err):
                raise Exception("odt2pdf failed: %s - %s (2. attempt)" % (output, err))
        else:
            raise Exception("odt2pdf failed: %s - %s (1. attempt)" % (output, err))
    # print output
    # print err
    # print p.returncode

    pdf_file = "%s/%s.pdf" % (path, outfile[0])
    # print pdf_file
    if not os.path.isfile(pdf_file):
        raise Exception("odt2pdf failed")

    # my $pdf_file = $path."/".$filename.".pdf";
    # if (-e $pdf_file) {
    #    if ($stamp) {
    #        $cmd = $webstamp_root."/webstamp.pl \"".$pdf_file."\"";
    #        #print $cmd."\n";
    #        system($cmd);
    #    }

    return pdf_file


## Get monthly values for costs (e.g. split annual costs into months etc.)
def calc_monthly_amounts(cost):
    if "amount_factor" not in cost:
        cost["amount_factor"] = 1.0
    if cost["time_period"] == "yearly":
        w_total = sum(nk.monthly_weights[cost["monthly_weights"]])
        amounts = []
        for w in nk.monthly_weights[cost["monthly_weights"]]:
            amounts.append(w / w_total * cost["amount"] * cost["amount_factor"])
        return amounts
    elif cost["time_period"] == "monthly":
        if "amount_data" in cost:
            cost["amount"] = [
                amount * cost["amount_factor"] for amount in nk.data_amount[cost["amount_data"]]
            ]
        elif "amount_meta" in cost:
            for c in nk.costs:
                if c["name"] == cost["amount_meta"]:
                    # nk.log.append('Virtuelles Objekt "Allgemein": Kosten %s: %s' % (c['name'], c['cost_split']['objects']['0000']['monthly']['amount']))
                    cost["amount"] = c["cost_split"]["objects"]["0000"]["monthly"]["amount"]
                    break
        return cost["amount"]
    else:
        raise RuntimeError("time_period %s is not defined!" % cost["time_period"])


## Aggregate amounts for costs that we have by object already
def aggregate_cost_objects(amount_key, cost):
    split = cost["cost_split"]

    ## Initialize
    split["total"] = {
        "monthly": {
            "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "percent": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
            "weight": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "annual": {"amount": 0, "percent": 100, "weight": 0},
    }

    for s in nk.sections:
        split["sections"][s] = {
            "monthly": {
                "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "percent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "weight": 12 * [0],
            },
            "annual": {"amount": 0, "percent": 0, "weight": 0},
        }
    for o in nk.objects:
        split["objects"][o["name"]] = {
            "monthly": {
                "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "percent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "weight": 12 * [0],
            },
            "annual": {"amount": 0, "percent": 0, "weight": 0},
        }
    ## Copy and aggregate amounts
    for o in nk.objects:
        for m in range(12):
            split["objects"][o["name"]]["monthly"]["amount"][m] = o[amount_key][m]
            split["objects"][o["name"]]["annual"]["amount"] += o[amount_key][m]
            split["sections"][o["section"]]["monthly"]["amount"][m] += o[amount_key][m]
            split["sections"][o["section"]]["annual"]["amount"] += o[amount_key][m]
            split["total"]["monthly"]["amount"][m] += o[amount_key][m]
            split["total"]["annual"]["amount"] += o[amount_key][m]

    ## Calculate percentages
    for s in nk.sections:
        if split["total"]["annual"]["amount"]:
            split["sections"][s]["annual"]["percent"] = (
                split["sections"][s]["annual"]["amount"]
                / split["total"]["annual"]["amount"]
                * 100.0
            )
        else:
            split["sections"][s]["annual"]["percent"] = 0
        for m in range(12):
            if split["total"]["monthly"]["amount"][m]:
                split["sections"][s]["monthly"]["percent"][m] = (
                    split["sections"][s]["monthly"]["amount"][m]
                    / split["total"]["monthly"]["amount"][m]
                    * 100.0
                )
            else:
                split["sections"][s]["monthly"]["percent"][m] = 0
    for o in nk.objects:
        if split["total"]["annual"]["amount"]:
            split["objects"][o["name"]]["annual"]["percent"] = (
                split["objects"][o["name"]]["annual"]["amount"]
                / split["total"]["annual"]["amount"]
                * 100.0
            )
        else:
            split["objects"][o["name"]]["annual"]["percent"] = 0
        for m in range(12):
            if split["total"]["monthly"]["amount"][m]:
                split["objects"][o["name"]]["monthly"]["percent"][m] = (
                    split["objects"][o["name"]]["monthly"]["amount"][m]
                    / split["total"]["monthly"]["amount"][m]
                    * 100.0
                )
            else:
                split["objects"][o["name"]]["monthly"]["percent"][m] = 0


def split_cost_objects(amounts, cost):
    ## Prepare data fields
    split = cost["cost_split"]
    split["total"] = {
        "monthly": {
            "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "percent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "weight": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "annual": {"amount": 0, "percent": 0, "weight": 0},
    }

    for s in nk.sections:
        split["sections"][s] = {
            "monthly": {
                "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "percent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "weight": 12 * [0],
            },
            "annual": {"amount": 0, "percent": 0, "weight": 0},
        }
    for o in nk.objects:
        split["objects"][o["name"]] = {
            "monthly": {
                "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "percent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "weight": 12 * [0],
            },
            "annual": {"amount": 0, "percent": 0, "weight": 0},
        }
    ## Store total
    split["total"]["monthly"]["amount"] = amounts
    split["total"]["monthly"]["percent"] = [
        100,
        100,
        100,
        100,
        100,
        100,
        100,
        100,
        100,
        100,
        100,
        100,
    ]
    split["total"]["annual"]["amount"] = sum(amounts)
    split["total"]["annual"]["percent"] = 100

    ## Get weights and unit price
    for month in range(12):
        ## Total weight
        w_total = 0
        for o in nk.objects:
            if isinstance(o[cost["object_weights"]], list):
                weight = (
                    nk.monthly_weights[cost["monthly_weights"]][month]
                    * nk.section_weights[cost["section_weights"]][o["section"]]
                    * o[cost["object_weights"]][month]
                )
            else:
                weight = (
                    nk.monthly_weights[cost["monthly_weights"]][month]
                    * nk.section_weights[cost["section_weights"]][o["section"]]
                    * o[cost["object_weights"]]
                    / sum(nk.monthly_weights[cost["monthly_weights"]])
                )
            split["objects"][o["name"]]["monthly"]["weight"][month] = weight
            split["sections"][o["section"]]["monthly"]["weight"][month] += weight
            w_total += weight
        split["total"]["monthly"]["weight"][month] = w_total
    split["total"]["annual"]["weight"] = sum(split["total"]["monthly"]["weight"])
    split["unit_price"] = split["total"]["annual"]["amount"] / split["total"]["annual"]["weight"]
    unit_price = split["unit_price"]

    ## Calculate amounts
    for month in range(12):
        amount = amounts[month]
        # if amount == 0:
        #    continue

        ## Split by section
        section_amounts = {}
        for s in nk.sections:
            section_amounts[s] = split["sections"][s]["monthly"]["weight"][month] * unit_price
            split["sections"][s]["monthly"]["amount"][month] = section_amounts[s]
            if amount:
                split["sections"][s]["monthly"]["percent"][month] = (
                    section_amounts[s] / amount * 100.0
                )
            else:
                split["sections"][s]["monthly"]["percent"][month] = 0
            split["sections"][s]["annual"]["amount"] += section_amounts[s]
            # nk.log.append('Split: %s %s' % (s, split[s]))

        ## Split by object
        for o in nk.objects:
            split_amount = split["objects"][o["name"]]["monthly"]["weight"][month] * unit_price
            split["objects"][o["name"]]["monthly"]["amount"][month] = split_amount
            if amount:
                split["objects"][o["name"]]["monthly"]["percent"][month] = (
                    split_amount / amount * 100.0
                )
            else:
                split["objects"][o["name"]]["monthly"]["percent"][month] = 0
            split["objects"][o["name"]]["annual"]["amount"] += split_amount

    ## Calc annual percentages
    for s in nk.sections:
        split["sections"][s]["annual"]["weight"] = sum(split["sections"][s]["monthly"]["weight"])
        if split["total"]["annual"]["amount"]:
            split["sections"][s]["annual"]["percent"] = (
                split["sections"][s]["annual"]["amount"]
                / split["total"]["annual"]["amount"]
                * 100.0
            )
        else:
            split["sections"][s]["annual"]["percent"] = 0
    for o in nk.objects:
        split["objects"][o["name"]]["annual"]["weight"] = sum(
            split["objects"][o["name"]]["monthly"]["weight"]
        )
        if split["total"]["annual"]["amount"]:
            split["objects"][o["name"]]["annual"]["percent"] = (
                split["objects"][o["name"]]["annual"]["amount"]
                / split["total"]["annual"]["amount"]
                * 100.0
            )
        else:
            split["objects"][o["name"]]["annual"]["percent"] = 0


## Import costs from file
def import_amount_data():
    filename = nk.config["Messdaten:Liegenschaft"]
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        header = None
        count = 0
        for row in reader:
            if not header:
                header = row
                if header[0] != "Monat":
                    raise RuntimeError("Unexpected header in %s: %s" % (filename, header))
                for i in range(1, len(header)):
                    cost_name = header[i]
                    # nk.log.append(cost_name)
                    nk.data_amount[cost_name] = []
            else:
                for i in range(1, len(header)):
                    cost_name = header[i]
                    nk.data_amount[cost_name].append(float(row[i]))
                count += 1
                if count == 12:
                    break


## Import counter data from egon export files
def import_messung_data():
    fields = {
        "Strom": {
            "Gebäudeeinheit": "object",
            "Mieter Abrechnungsperiode": "time_period",
            "Strombezug Niedertarif(kWh)": "strom_ew_nieder",
            "Strombezug Hochtarif EW (kWh)": "strom_ew_hoch",
            "Solarstrom (kWh)": "strom_solar",
            "Strombezug Niedertarif(CHF)": "chf_netz_nieder",
            "Strombezug EW (CHF)": "chf_netz_hoch",
        },
        "Waerme": {
            "Gebäudeeinheit": "object",
            "Mieter Abrechnungsperiode": "time_period",
            "Warmwasser Verbrauch (Kubikmeter)": "warmwasser",
            "Wärmeverbrauch (kWh)": "heizung",
        },
    }

    with zipfile.ZipFile(nk.config["Messdaten:Mieteinheiten"]) as archive:
        for quantity in fields:
            month = 0
            for dat in nk.dates:
                filename = "egon_%s_%s.csv" % (quantity, dat["start"].strftime("%Y-%m"))
                try:
                    with io.TextIOWrapper(archive.open(filename), encoding="iso8859") as csvfile:
                        nk.log.append(" << %s" % filename)
                        read_messung_data_csv(
                            csvfile, fields, quantity, month, dat["start"], dat["end"]
                        )
                except FileNotFoundError:
                    nk.log.append(
                        "WARNING: Could not import data. File in ZIP not found: %s" % filename
                    )
                    raise RuntimeError(
                        "Konnte Mieteinheit-Messdaten nicht importieren. Datei im ZIP nicht gefunden: %s"
                        % filename
                    )
                except Exception as e:
                    nk.log.append(f"WARNING: Error while reading {filename}: {e}")
                    raise RuntimeError(
                        f"Fehler beim Import der Mieteinheit-Messdaten von {filename}: {e}"
                    )
                month += 1


def read_messung_data_csv(csvfile, fields, quantity, month_index, period_start, period_end):
    reader = csv.reader(csvfile, delimiter=";", quotechar='"')
    header = None
    for row in reader:
        if not row:
            continue
        if not header:
            header = row
        elif row[0] == "Gesamt":
            ## Skip line with totals
            continue
        else:
            data = {}
            for i in range(len(header)):
                if header[i] in fields[quantity]:
                    data[fields[quantity][header[i]]] = row[i]
            if len(data) != len(fields[quantity]):
                raise RuntimeError("Not all fields found: %s / %s." % (data, fields[quantity]))
            ## Check time period
            month_period = "%s - %s" % (
                period_start.strftime("%d.%m.%Y"),
                period_end.strftime("%d.%m.%Y"),
            )
            if data["time_period"] != month_period:
                nk.log.append(
                    "WARNING: Unusual time period %s for object %s"
                    % (data["time_period"], data["object"])
                )
                nk.add_warning(f"Ungewöhnliche Mess-Periode {data['time_period']}", data["object"])
            ## Add data to object
            obj_name = get_object_name(data["object"])
            if obj_name not in nk.object_messung:
                nk.object_messung[obj_name] = {
                    "imported_obj_names": [
                        data["object"],
                    ]
                }
            for d in data:
                if d not in ("object", "time_period"):
                    if d not in nk.object_messung[obj_name]:
                        nk.object_messung[obj_name][d] = []
                        for _i in range(month_index):
                            nk.object_messung[obj_name][d].append(0)
            else:
                if data["object"] not in nk.object_messung[obj_name]["imported_obj_names"]:
                    nk.object_messung[obj_name]["imported_obj_names"].append(data["object"])
            for d in data:
                if d not in ("object", "time_period"):
                    # nk.log.append(" %s / %s: len=%s, month_index=%s" % (obj_name, d, len(nk.object_messung[obj_name][d]), month_index))
                    # if d == 'warmwasser':
                    #    #for v in data[d]:
                    #    data[d] = float(data[d]) # Kubikmeter  // old: *0.001 # Convert Liter -> m3
                    if len(nk.object_messung[obj_name][d]) == month_index:
                        nk.object_messung[obj_name][d].append(float(data[d]))
                    else:
                        if float(data[d]) != 0:
                            if nk.object_messung[obj_name][d][month_index] != 0:
                                added_obj_names = " + ".join(
                                    nk.object_messung[obj_name]["imported_obj_names"]
                                )
                                nk.log.append(
                                    f"WARNUNG: Objekt {obj_name}: Addiere zusätzlichen Messwert '{d}' für Periode {month_period} ({data[d]} von {data['time_period']}) [{added_obj_names}]"
                                )
                                nk.add_warning(
                                    f"Addiere zusätzlichen Messwert für Periode {month_period}",
                                    f"{obj_name}/{d}",
                                )
                            nk.object_messung[obj_name][d][month_index] += float(data[d])


def add_calculated_weights():
    total_weight_warmwasser = 0
    for o in nk.objects:
        if o["name"] == "0000":
            messung_objname = "_allgemein"
        elif o["name"] == "9998":
            messung_objname = "_pauschal_nk"
        elif o["name"] == "9999":
            messung_objname = "_pauschal_strom"
        else:
            messung_objname = o["name"]
            ## Add NK pauschal to akonto of special object for Pauschal-NK
            nk.objects[nk.object_indices["9998"]]["akonto_obj"] += o["nk_pauschal_obj"]
            ## Add Strom pauschal to akonto of special object for Pauschal-Strom
            nk.objects[nk.object_indices["9999"]]["akonto_obj"] += o["strom_pauschal_obj"]
        if messung_objname in nk.object_messung and sum(
            nk.object_messung[messung_objname]["warmwasser"]
        ):
            # nk.log.append("--> WW-Area: %s" % o['#area'])
            # print ('%s/%s: %s' % (messung_objname,o['name'],nk.object_messung[messung_objname]['warmwasser']))
            o["area_warmwasser"] = o["area"]

            ## Sum for scaling
            total_weight_warmwasser += sum(nk.object_messung[messung_objname]["warmwasser"])
        else:
            # if messung_objname not in nk.object_messung:
            #    nk.log.append("WARNING: Keine Messdaten für Objekt %s vorhanden in nk.object_messung -> Setze area_warmwasser auf 0!" % o['name'])
            nk.log.append(
                "WARNING: Keine Messdaten für Objekt %s vorhanden (oder Null) in nk.object_messung -> Setze area_warmwasser auf 0!"
                % o["name"]
            )
            nk.add_warning(
                "Keine Warmwasser-Messdaten vorhanden. Berechne KEINE Warmwasser-Grundkosten",
                o["name"],
            )
            o["area_warmwasser"] = 0

    if total_weight_warmwasser == 0:
        raise RuntimeError(
            "Keine Messdaten für Warmwasser gefunden (total_weight_warmwasser == 0)"
        )

    ## Scale warmwasser -> wasser
    for cost in nk.costs:
        if cost["name"] == "Wasser_Abwasser_Verbrauch":
            factor = cost["scale_to_total_usage"] / total_weight_warmwasser
            for o in nk.objects:
                if o["name"] == "0000":
                    messung_objname = "_allgemein"
                elif o["name"] == "9999":
                    messung_objname = "_lager_strom"
                else:
                    messung_objname = o["name"]
                if messung_objname in nk.object_messung:
                    nk.object_messung[messung_objname]["wasser"] = []
                    for w in nk.object_messung[messung_objname]["warmwasser"]:
                        nk.object_messung[messung_objname]["wasser"].append(factor * w)


def map_messung_to_objects():
    objects_found = []
    for object_name in nk.object_messung:
        if object_name in nk.object_indices:
            obj = nk.objects[nk.object_indices[object_name]]
            if obj["allgemein"]:
                ## Map to special object for Allgemein
                objects_found.append(obj["name"])
                obj = nk.objects[nk.object_indices["0000"]]
                # nk.log.append('INFO: Mapping object_name %s -> Allgemein' % object_name)
            for data in nk.object_messung[object_name]:
                if "messung_%s" % data in obj:
                    # nk.log.append("Adding messung_%s to %s" % (data,obj['name']))
                    obj["messung_%s" % data] = list(
                        map(add, obj["messung_%s" % data], nk.object_messung[object_name][data])
                    )
                else:
                    obj["messung_%s" % data] = nk.object_messung[object_name][data]
                # if object_name != obj['name']:
                #    nk.log.append(" - Assigning %s from %s to %s" % (data,object_name,obj['name']))
            objects_found.append(obj["name"])
        elif object_name in ("_lager_strom",):
            ## Virtual object for Lager-Strom
            obj = nk.objects[nk.object_indices["9999"]]
            for data in nk.object_messung[object_name]:
                if "messung_%s" % data in obj:
                    # nk.log.append("Adding messung_%s to %s" % (data,obj['name']))
                    obj["messung_%s" % data] = list(
                        map(add, obj["messung_%s" % data], nk.object_messung[object_name][data])
                    )
                else:
                    obj["messung_%s" % data] = nk.object_messung[object_name][data]
            objects_found.append(obj["name"])
        elif object_name in ("_allgemein",):
            ## Virtual object for Allgemien
            obj = nk.objects[nk.object_indices["0000"]]
            for data in nk.object_messung[object_name]:
                if "messung_%s" % data in obj:
                    # nk.log.append("Adding messung_%s to %s" % (data,obj['name']))
                    obj["messung_%s" % data] = list(
                        map(add, obj["messung_%s" % data], nk.object_messung[object_name][data])
                    )
                else:
                    obj["messung_%s" % data] = nk.object_messung[object_name][data]
            objects_found.append(obj["name"])
        else:
            nk.log.append("ERROR: No object found with name %s" % object_name)
            raise RuntimeError("Unbekanntes Objekt in den Messdaten: %s" % object_name)

    # nk.log.append(" === DEBUG: Object 011 === ")
    # nk.log.append(objects[nk.object_indices['011']])
    # for c_id in nk.objects[nk.object_indices['011']]['contracts']:
    #    nk.log.append(nk.contracts[c_id])
    for o in nk.objects:
        if o["name"] not in objects_found:
            nk.log.append("WARNING: Keine Messdaten für object %s" % o["name"])
            nk.add_warning("Keine Messdaten für Objekt gefunden", o["name"])


def stromrechnung():
    ## Tarife in CHF/kWh
    tarif_eigenstrom = nk.config[
        "Strom:Tarif:Eigenstrom"
    ]  # 0.1453  ## Tarif für Eigenstromverbrauch (Berechnung in Messungen.ods)
    ## Einspeisevergütung EW      Jul   Aug   Sep   Okt   Nov   Dez    Jan    Feb    Mar    Apr    Mai    Jun
    tarif_einspeiseverguetung = nk.config[
        "Strom:Tarif:Einspeisevergütung"
    ]  # [0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.176, 0.176, 0.176, 0.176, 0.176, 0.176]
    tarif_hkn = nk.config[
        "Strom:Tarif:HKN"
    ]  # 0.07 # Einkauf Herkunftsnachweise siehe aktuelles Reglement und Tarife Stromallmend https://stromallmend.ch/reglement/
    # tarif_korrektur = 0.2007  ## Durchschnittlicher Strompreis
    ## Durchschnittlicher Strompreis für Korrekturen (für Mittelwert und für Hauptbezug in der Nacht/ohne Eigenstrom)
    tarif_korrektur = nk.config["Strom:Tarif:Korrekturen"]  # {'mittel': 0.28, 'nacht': 0.33}

    ## Sollen Solar-Speicher und HKN-Einkauf berücksichtig werden?
    solar_speicher_und_hkn_einkauf = True

    einspeisefaktor = []
    for m in range(12):
        if nk.data_amount["Strom_kwh_egon"][m]:
            if solar_speicher_und_hkn_einkauf:
                einspeisefaktor.append(
                    nk.data_amount["Strom_kwh_ruecklieferung"][m]
                    / nk.data_amount["Strom_kwh_egon"][m]
                )
            else:
                einspeisefaktor.append(0)
        else:
            einspeisefaktor.append(0)

    for o in nk.objects:
        if "messung_strom_ew_hoch" not in o:
            ## Keine Stromdaten
            o["chf_total"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            continue

        o["kwh_korrektur"] = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]  ## Spezielle Korrektur (z.B. Allgemeinnutzung von Mietobj. etc.)
        o["chf_korrektur"] = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]  ## Spezielle Korrektur (z.B. Allgemeinnutzung von Mietobj. etc.)
        korrektur_strom = nk.config["Strom:Korrekturen"]
        if o["name"] in korrektur_strom:
            for korr in korrektur_strom[o["name"]]:
                korr["chf"] = list(map(lambda x: x * tarif_korrektur[korr["tarif"]], korr["kwh"]))
                o["kwh_korrektur"] = list(map(add, o["kwh_korrektur"], korr["kwh"]))
                o["chf_korrektur"] = list(map(add, o["chf_korrektur"], korr["chf"]))
                summe_kwh = sum(korr["kwh"])
                summe_chf = sum(korr["chf"])
                nk.text_output(
                    "Strom-Korrektur",
                    "Manuelle Weiterverrechnung",
                    "Korrektur Strom von %s: %s kWh / CHF %s (%s)"
                    % (o["name"], summe_kwh, summe_chf, korr["desc"]),
                )
            total_kwh = sum(o["kwh_korrektur"])
            total_chf = sum(o["chf_korrektur"])
            if total_kwh != summe_kwh or total_chf != summe_chf:
                nk.text_output(
                    "Strom-Korrektur",
                    "Manuelle Weiterverrechnung",
                    "   Total von %s: %s kWh / CHF %s" % (o["name"], total_kwh, total_chf),
                )
        # messung_strom_solar         ## Eigenverbrauch Solarstrom
        o[
            "kwh_solar_speicher"
        ] = []  ## Eigener Solarstrom via Zwischenspeicher Stromallmend (in Netz eingespiesen und später wieder bezogen)
        o["kwh_solar_einkauf"] = []  ## Zusätzlich eingekaufter Solarstrom von Stromallmend
        o["kwh_netzstrom"] = []  ## Total bezogener Netzstrom (speicher + einkauf)
        o["kwh_total"] = []  ## Total bezogener Strom (eigenverbrauch + netzstrom)
        for m in range(12):
            o["kwh_netzstrom"].append(
                o["messung_strom_ew_hoch"][m] + o["messung_strom_ew_nieder"][m]
            )
            o["kwh_solar_speicher"].append(einspeisefaktor[m] * o["kwh_netzstrom"][m])
            if solar_speicher_und_hkn_einkauf:
                o["kwh_solar_einkauf"].append(o["kwh_netzstrom"][m] - o["kwh_solar_speicher"][m])
                o["kwh_total"].append(
                    o["messung_strom_solar"][m]
                    + o["kwh_solar_speicher"][m]
                    + o["kwh_solar_einkauf"][m]
                    + o["kwh_korrektur"][m]
                )
            else:
                o["kwh_solar_einkauf"].append(0)
                o["kwh_total"].append(
                    o["messung_strom_solar"][m] + o["kwh_netzstrom"][m] + o["kwh_korrektur"][m]
                )

        o["chf_solar_eigen"] = []  ## Kosten Eigenverbrauch
        o["chf_solar_einspeise"] = []  ## Einspeisevergütung
        o["chf_solar_hkn"] = []  ## Kosten Herkunftsnachweise Solarstrom
        # o['chf_netz_hoch'] = []         ## Kosten Netzstrombezug (Normaltarif)
        # o['chf_netz_nieder'] = []       ## Kosten Netzstrombezug (Spartarif)
        o["chf_total"] = []  ## Total Stromkosten
        for m in range(12):
            o["chf_solar_eigen"].append(
                o["messung_strom_solar"][m] * tarif_eigenstrom
            )  ## Kosten Eigenstromverbrauch
            o["chf_solar_einspeise"].append(
                o["kwh_solar_speicher"][m] * (tarif_eigenstrom - tarif_einspeiseverguetung[m])
            )  ## Ertrag aus eingespiesenem Solarstrom (Kosten Produktion minus Einspeisevergütung EW)
            o["chf_solar_hkn"].append(
                o["kwh_solar_einkauf"][m] * tarif_hkn
            )  ## Kosten Herkunftsnachweise für Einkauf Solarstrom
            # o['chf_netz_hoch'].append( o['messung_strom_ew_hoch'][m] * tarif_netz_hoch )
            # o['chf_netz_nieder'].append( o['messung_strom_ew_nieder'][m] * tarif_netz_nieder )
            o["chf_total"].append(
                o["chf_solar_eigen"][m]
                + o["chf_solar_einspeise"][m]
                + o["chf_solar_hkn"][m]
                + o["messung_chf_netz_hoch"][m]
                + o["messung_chf_netz_nieder"][m]
                + o["chf_korrektur"][m]
            )

            ## Sum Totals
            nk.strom_total["solar_eigen"]["kwh"][m] += o["messung_strom_solar"][m]
            nk.strom_total["solar_eigen"]["chf"][m] += o["chf_solar_eigen"][m]
            nk.strom_total["solar_speicher"]["kwh"][m] += o["kwh_solar_speicher"][m]
            nk.strom_total["solar_speicher"]["chf"][m] += o["chf_solar_einspeise"][m]
            nk.strom_total["solar_einkauf"]["kwh"][m] += o["kwh_solar_einkauf"][m]
            nk.strom_total["solar_einkauf"]["chf"][m] += o["chf_solar_hkn"][m]
            nk.strom_total["ew_hoch"]["kwh"][m] += o["messung_strom_ew_hoch"][m]
            nk.strom_total["ew_hoch"]["chf"][m] += o["messung_chf_netz_hoch"][m]
            nk.strom_total["ew_nieder"]["kwh"][m] += o["messung_strom_ew_nieder"][m]
            nk.strom_total["ew_nieder"]["chf"][m] += o["messung_chf_netz_nieder"][m]
            nk.strom_total["korrektur"]["kwh"][m] += o["kwh_korrektur"][m]
            nk.strom_total["korrektur"]["chf"][m] += o["chf_korrektur"][m]
            ## total CHF = eigen + speicher + einkauf + hoch + nieder + korrektur
            ## total kWh = eigen + hoch + nieder
            nk.strom_total["total"]["kwh"][m] += o["kwh_total"][m]
            nk.strom_total["total"]["chf"][m] += o["chf_total"][m]
            ## netz  kWh = hoch + nieder
            nk.strom_total["total_netz"]["kwh"][m] += o["kwh_netzstrom"][m]
            ## Total per section
            if o["section"] not in nk.strom_total["total_sect"]:
                nk.strom_total["total_sect"][o["section"]] = {"kwh": 12 * [0], "chf": 12 * [0]}
            nk.strom_total["total_sect"][o["section"]]["kwh"][m] += o["kwh_total"][m]
            nk.strom_total["total_sect"][o["section"]]["chf"][m] += o["chf_total"][m]


def internetrechnung():
    ## Internet Kostenmodell:
    internet_fee_object = nk.config["Internet:Tarif:ProWohnung"]  ## CHF per apartment and month
    internet_fee_occupant = nk.config[
        "Internet:Tarif:ProPerson"
    ]  ## CHF per person and month (min. occupancy)
    internet_fee_fixed = nk.config["Internet:Tarif:Fix"]

    for o in nk.objects:
        chf_per_month = 0
        if o["name"] in internet_fee_fixed:
            chf_per_month = internet_fee_fixed[o["name"]]
        elif o["min_occupancy"]:
            ## Berechnung aufgrund von Mindestbelegung
            chf_per_month = internet_fee_object + o["min_occupancy"] * internet_fee_occupant

        o["chf_internet"] = []
        for mw in nk.monthly_weights["default"]:
            o["chf_internet"].append(mw * chf_per_month)


def get_object_name(name):
    ## Map imported data names to object names
    if name in ("Allgemein Warmwasser u Heizen", "Allgemein"):
        return "_allgemein"
    if name == "Hobbyräume und Lager Gesamtstromverbrauch":
        return "_lager_strom"
    # match = re.search(r"^(\d{3,4}\.?\d?) ", name)
    match = re.search(r"^([0-9a-zA-Z.-]+) ?", name)
    if match:
        # nk.log.append("Match object %s -> %s" % (name, match.group(1)))
        if match.group(1) == "9696":
            return "_lager_strom"
        return match.group(1)
    raise RuntimeError("Ungültiger Objektname in den Messdaten: %s" % name)


def get_from_api(uri, params=None):
    headers = {"Authorization": "Token " + API_TOKEN}
    res = requests.get(BASE_URI + uri, headers=headers, params=params)
    if res.status_code != 200:
        raise RuntimeError(
            f"Unexpected status_code {res.status_code} retuned from API at {uri}: {res.content}."
        )
    return res.json()


def import_from_api():
    ## Get sum of akonto payments per contract
    request_params = {
        "billing_period_start": nk.dates[nk.period_start_index]["start"].strftime("%Y-%m-%d"),
        "billing_period_end": nk.dates[-1]["end"].strftime("%Y-%m-%d"),
    }
    akonto_resp = get_from_api("/geno/akonto/", params=request_params)
    if "akonto_billing" not in akonto_resp:
        raise RuntimeError("import_from_api() failed: Could not get akonto: %s" % (akonto_resp))
    akonto_totals = akonto_resp["akonto_billing"]

    ## Get Contracts and map it to rental units
    rental_unit_contracts = {}
    response = get_from_api("/geno/contract/")
    if "count" not in response:
        if "detail" in response:
            raise RuntimeError("import_from_api() failed: %s" % response["detail"])
        else:
            raise RuntimeError("import_from_api() failed: %s" % response)

    if response["next"] or response["previous"]:
        raise RuntimeError("API returned multiple pages but pagination is not implemented yet!")
    for contract in response["results"]:
        ## Convert dates and set billing_date_start/end
        if contract["date"]:
            d = contract["date"].split("-")
            contract["date"] = datetime(int(d[0]), int(d[1]), int(d[2]))
        if contract["date_end"]:
            d = contract["date_end"].split("-")
            contract["date_end"] = datetime(int(d[0]), int(d[1]), int(d[2]))
        if contract["billing_date_start"]:
            d = contract["billing_date_start"].split("-")
            contract["billing_date_start"] = datetime(int(d[0]), int(d[1]), int(d[2]))
        else:
            contract["billing_date_start"] = contract["date"]
        if contract["billing_date_end"]:
            d = contract["billing_date_end"].split("-")
            contract["billing_date_end"] = datetime(int(d[0]), int(d[1]), int(d[2]))
        else:
            contract["billing_date_end"] = contract["date_end"]
        ## Get akonto from billing
        # request_params = {
        #    'contract_id': contract['id'],
        #    'billing_period_start': nk.dates[nk.period_start_index]['start'].strftime('%Y-%m-%d'),
        #    'billing_period_end': nk.dates[-1]['end'].strftime('%Y-%m-%d'),
        # }
        # akonto_resp = get_from_api("/geno/akonto/", params=request_params)
        # if 'akonto_billing' not in akonto_resp:
        #    raise RuntimeError('import_from_api() failed: Could not get akonto for contract_id %s: %s' % (contract['id'], akonto_resp))
        contract["akonto_billing"] = akonto_totals.get(str(contract["id"]), 0)
        ## TEST
        # if contract['akonto_billing'] != akonto_resp['akonto_billing']:
        #    raise RuntimeError(f"akonto_totals != akonto_resp [{contract['akonto_billing']} != {akonto_resp['akonto_billing']} for contract {contract['id']}")
        ## Save contract to nk.contracts[<id>]
        nk.contracts[str(contract["id"])] = contract
        # id
        # contractors (list)
        # main_contact
        # rental_units (list)
        # date
        # date_end
        ## Add contract id to rental unit contract list
        if contract["billing_contract"]:
            ## Contract is linked to another contract for billing -> add object to that contract
            billing_contract = str(contract["billing_contract"])
        else:
            billing_contract = str(contract["id"])
        for ru_id in contract["rental_units"]:
            if ru_id in rental_unit_contracts:
                rental_unit_contracts[ru_id].append(billing_contract)
            else:
                rental_unit_contracts[ru_id] = [
                    billing_contract,
                ]

    ## Get RentalUnits
    response = RentalUnit.objects.filter(active=True).order_by("name")
    if nk.config["Liegenschaften"]:
        building_ids = [int(x) for x in json.loads(nk.config["Liegenschaften"].replace("'", '"'))]
        response = response.filter(building__in=building_ids)

    ru_section = {
        "Wohnung": "Wohnen",
        "Grosswohnung": "Wohnen",
        "Jokerzimmer": "Wohnen",
        "Selbstausbau": "Wohnen",
        "Kellerabteil": None,
        "Gewerbe": "Gewerbe",
        "Gemeinschaft": None,
        "Parkplatz": None,
        "Lager": "Lager",
        "Hobby": "Gewerbe",
    }
    for ru in response:
        section = ru_section[ru.rental_type]
        allgemein = False
        ## Gästerzimmer, Dachküche, Teeküche nicht mehr allgemein (Entscheid Finko/VW 25.10.22)
        # if ru['label'] in ("Gästezimmer", "Dachküche", "Teeküche","Einstellhalle Auto","Einstellhalle Velo"):
        if ru.label in ("Dachküche",):
            section = "Wohnen"
        elif ru.label in (
            "Teeküche",
            "Lückenraum Holliger rechts",
            "Lückenraum Holliger links",
            "Quartierraum Holliger",
        ):
            section = "Gewerbe"
        elif ru.label in ("Lagerraum", "Lagerabteil"):
            section = "Lager"
        elif ru.rental_type in ("Parkplatz", "Gemeinschaftsräume/Diverses"):
            allgemein = True

        if ru.label:
            label = "%s %s" % (ru.label, ru.name)  # , ru['label'])
        else:
            label = "%s %s" % (ru.rental_type, ru.name)

        akonto = 0
        nk_pauschal = 0
        strom_pauschal = 0
        rent_net = 0
        for mw in nk.monthly_weights["default"]:
            if ru.rent_total:
                rent_net += mw * float(ru.rent_total)
            if ru.nk:
                akonto += mw * float(ru.nk)
            if ru.nk_flat:
                nk_pauschal += mw * float(ru.nk_flat)
            if ru.nk_electricity:
                strom_pauschal += mw * float(ru.nk_electricity)
        if allgemein:
            area_weight = 0
            volume_weight = 0
            akonto = 0
            min_occupancy = 0
            rent_net = 0
        else:
            try:
                area_weight = float(ru.area)
                if ru.volume:
                    volume_weight = float(ru.volume)
                else:
                    nk.log.append("WARNING: Unit %s has no volume." % (label))
                    nk.add_warning("Kein Volumen definiert", label)
                    volume_weight = 0
                if ru.min_occupancy:
                    min_occupancy = float(ru.min_occupancy)
                else:
                    min_occupancy = 0
                if ru.rooms:
                    rooms = float(ru.rooms)
                else:
                    rooms = 0
            except TypeError as e:
                nk.log.append(ru)
                raise RuntimeError(
                    "ERROR: %s for %s (area=%s, volume=%s, min_occupancy=%s, rooms=%s)"
                    % (e, ru.name, ru.area, ru.volume, ru.min_occupancy, ru.rooms)
                )

        ru_contracts = rental_unit_contracts.get(ru.id, [])
        if section:
            nk.objects.append(
                {
                    "id": ru.id,
                    "name": ru.name,
                    "label": label,
                    "section": section,
                    "area": area_weight,
                    "volume": volume_weight,
                    "min_occupancy": min_occupancy,
                    "rooms": rooms,
                    "allgemein": allgemein,
                    "akonto_obj": akonto,
                    "nk_pauschal_obj": nk_pauschal,
                    "strom_pauschal_obj": strom_pauschal,
                    "rent_net": rent_net,
                    "costs": {},
                    "contracts": ru_contracts,
                }
            )
        else:
            nk.log.append("WARNING: Ignoring object %s (no section defined)" % (label))
            nk.add_warning("Ignoriere Objekte ohne Bereichs-Zuordnung", label)
        # nk.log.append(ru)


def export_csv():
    include_monthly = False
    include_percent = False
    output_filename = nk.get_output_filename(
        "Abrechnung.csv", "NK-Abrechnung Übersicht", "Übersicht"
    )

    header = ["Kosten", "Total"]
    for s in nk.sections:
        header.append(s)
        if include_percent:
            header.append("%")
    for o in nk.objects:
        header.append(o["name"])
        if include_percent:
            header.append("%")

    footer_total = ["Total"]
    footer_total_reduced = ["Total ohne Strom/Internet*"]
    footer_akonto = ["AkontoObj"]
    footer_akonto_diff = ["Differenz zu AkontoObj"]
    footer_akonto_diff_reduced = ["Differenz zu AkontoObj ohne Strom/Internet*"]
    # footer_akonto_diff_percent = ['  in Prozent']

    weight_rows = []
    with open(output_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for cost in nk.costs:
            ## Annual
            row = []
            wrow = []
            row.append(cost["name"])
            wrow.append(cost["name"])
            if "amount_meta" in cost:
                row.append("")
                wrow.append(cost["cost_split"]["total"]["annual"]["weight"])
            else:
                row.append(cost["cost_split"]["total"]["annual"]["amount"])
                wrow.append(cost["cost_split"]["total"]["annual"]["weight"])
            for s in nk.sections:
                row.append(cost["cost_split"]["sections"][s]["annual"]["amount"])
                wrow.append(cost["cost_split"]["sections"][s]["annual"]["weight"])
                if include_percent:
                    row.append(cost["cost_split"]["sections"][s]["annual"]["percent"])
                    wrow.append("")
            for o in nk.objects:
                row.append(cost["cost_split"]["objects"][o["name"]]["annual"]["amount"])
                wrow.append(cost["cost_split"]["objects"][o["name"]]["annual"]["weight"])
                if include_percent:
                    row.append(cost["cost_split"]["objects"][o["name"]]["annual"]["percent"])
                    wrow.append("")
            if "amount_meta" in cost:
                ## Exclude meta from totals
                start_index = 2
            else:
                start_index = 1
            if len(footer_total) > 1:
                footer_total[start_index:] = list(
                    map(add, footer_total[start_index:], row[start_index:])
                )
                if cost["name"] not in ("Strom_Total", "Internet/WLAN"):
                    footer_total_reduced[start_index:] = list(
                        map(add, footer_total_reduced[start_index:], row[start_index:])
                    )
            else:
                footer_total[start_index:] = row[start_index:]
                if cost["name"] not in ("Strom_Total", "Internet/WLAN"):
                    footer_total_reduced[start_index:] = row[start_index:]

            row[1:] = list(map(format_amount, row[1:]))
            wrow[1:] = list(map(format_amount, wrow[1:]))
            writer.writerow(row)
            weight_rows.append(wrow)

            ## Monthly
            if include_monthly:
                for m in range(12):
                    row = []
                    wrow = []
                    row.append(" - Monat %02d" % m)
                    wrow.append(" - Monat %02d" % m)
                    row.append(cost["cost_split"]["total"]["monthly"]["amount"][m])
                    wrow.append(cost["cost_split"]["total"]["monthly"]["weight"][m])
                    for s in nk.sections:
                        row.append(cost["cost_split"]["sections"][s]["monthly"]["amount"][m])
                        wrow.append(cost["cost_split"]["sections"][s]["monthly"]["weight"][m])
                        if include_percent:
                            row.append(cost["cost_split"]["sections"][s]["monthly"]["percent"][m])
                            wrow.append("")
                    for o in nk.objects:
                        row.append(
                            cost["cost_split"]["objects"][o["name"]]["monthly"]["amount"][m]
                        )
                        wrow.append(
                            cost["cost_split"]["objects"][o["name"]]["monthly"]["weight"][m]
                        )
                        if include_percent:
                            row.append(
                                cost["cost_split"]["objects"][o["name"]]["monthly"]["percent"][m]
                            )
                            wrow.append("")
                    row[1:] = list(map(format_amount, row[1:]))
                    wrow[1:] = list(map(format_amount, wrow[1:]))
                    writer.writerow(row)
                    weight_rows.append(wrow)

        ## adjust percents
        if include_percent:
            for i in range(2, len(footer_total), 2):
                if footer_total[1]:
                    footer_total[i + 1] = footer_total[i] / footer_total[1] * 100.0
                if footer_total_reduced[1]:
                    footer_total_reduced[i + 1] = (
                        footer_total_reduced[i] / footer_total_reduced[1] * 100.0
                    )

        ## Remove allgemein
        for i, head in enumerate(header):
            if head == "Allgemein" or head == "0000":
                footer_total[i] = ""
                footer_total_reduced[i] = ""
                if include_percent:
                    footer_total[i + 1] = ""
                    footer_total_reduced[i + 1] = ""

        ## Calc akonto etc.
        akonto_obj = {"total": 0}
        for s in nk.sections:
            akonto_obj[s] = 0
        for o in nk.objects:
            akonto_obj[o["section"]] += o["akonto_obj"]
            akonto_obj["total"] += o["akonto_obj"]

        footer_akonto.append(akonto_obj["total"])
        for s in nk.sections:
            footer_akonto.append(akonto_obj[s])
            if include_percent:
                footer_akonto.append("")  # No percent
        for o in nk.objects:
            footer_akonto.append(o["akonto_obj"])
            if include_percent:
                footer_akonto.append("")  # No percent

        footer_akonto_diff.append(footer_akonto[1] - footer_total[1])
        footer_akonto_diff_reduced.append(footer_akonto[1] - footer_total_reduced[1])
        if include_percent:
            stride = 2
        else:
            stride = 1
        for i in range(2, len(footer_total), stride):
            if footer_total[i] != "" and footer_akonto[i] != "":
                footer_akonto_diff.append(footer_akonto[i] - footer_total[i])
                if include_percent:
                    if footer_akonto[i]:
                        footer_akonto_diff.append(footer_akonto_diff[i] / footer_akonto[i] * 100)
                    else:
                        footer_akonto_diff.append("")
            else:
                footer_akonto_diff.append("")
                if include_percent:
                    footer_akonto_diff.append("")
            if footer_total_reduced[i] != "" and footer_akonto[i] != "":
                footer_akonto_diff_reduced.append(footer_akonto[i] - footer_total_reduced[i])
                if include_percent:
                    if footer_akonto[i]:
                        footer_akonto_diff_reduced.append(
                            footer_akonto_diff_reduced[i] / footer_akonto[i] * 100
                        )
                    else:
                        footer_akonto_diff_reduced.append("")
            else:
                footer_akonto_diff_reduced.append("")
                if include_percent:
                    footer_akonto_diff_reduced.append("")

        footer_total[1:] = list(map(format_amount, footer_total[1:]))
        footer_total_reduced[1:] = list(map(format_amount, footer_total_reduced[1:]))
        footer_akonto[1:] = list(map(format_amount, footer_akonto[1:]))
        footer_akonto_diff[1:] = list(map(format_amount, footer_akonto_diff[1:]))
        footer_akonto_diff_reduced[1:] = list(map(format_amount, footer_akonto_diff_reduced[1:]))

        ## Remove totals from reduced, because it does not work with Allgemeinstromanteile
        footer_total_reduced[1] = ""
        footer_akonto_diff_reduced[1] = ""

        writer.writerow([])
        writer.writerow(footer_akonto)
        writer.writerow([])
        writer.writerow(footer_total_reduced)
        writer.writerow(footer_akonto_diff_reduced)
        writer.writerow([])
        writer.writerow(footer_total)
        writer.writerow(footer_akonto_diff)
        writer.writerow([])
        # writer.writerow(footer_akonto_diff_percent)

        ## Additional information
        writer.writerow([])
        row = []
        row.append("Raumtyp")
        row.append("")
        for s in nk.sections:
            row.append(s)
            if include_percent:
                row.append("")
        for o in nk.objects:
            row.append(o["section"])
            if include_percent:
                row.append("")
        writer.writerow(row)
        for field in ("rooms", "min_occupancy"):
            row = []
            row.append(field)
            row.append("")
            for _s in nk.sections:
                row.append("")
                if include_percent:
                    row.append("")
            for o in nk.objects:
                row.append(o[field])
                if include_percent:
                    row.append("")
            writer.writerow(row)

        writer.writerow([])

        ## Stromrechnung
        for key in (
            "messung_strom_solar",
            "kwh_solar_speicher",
            "kwh_solar_einkauf",
            "kwh_netzstrom",
            "kwh_korrektur",
            "kwh_total",
            "chf_solar_eigen",
            "chf_solar_einspeise",
            "chf_solar_hkn",
            "messung_chf_netz_hoch",
            "messung_chf_netz_nieder",
            "chf_korrektur",
            "chf_total",
        ):
            obj_data = []
            total = 0
            for o in nk.objects:
                if key in o:
                    total += sum(o[key])
                    obj_data.append(sum(o[key]))
                else:
                    obj_data.append("")
                if include_percent:
                    obj_data.append("")

            row = []
            row.append(key)
            row.append(total)
            for _s in nk.sections:
                row.append("")
                if include_percent:
                    row.append("")
            row += obj_data
            writer.writerow(row)

        ## Add weights
        writer.writerow([])
        writer.writerow(["WEIGHTS"])
        for row in weight_rows:
            writer.writerow(row)

    nk.log.append("Output is in %s" % output_filename)


def plots():
    # for o in nk.objects:
    #    ## Kosten in Prozent der Nettomiete, nach verbrauchsunabh, verbrauchsabh, Strom, Internet
    #    if o['name'] == '011':
    #        for key in o:
    #            nk.log.append(" - %s: %s" % (key, o[key]))
    plot(
        {
            "relative_key": "rent_net",
            "ylabel": "% der Nettomiete",
            "sorted": True,
            "anon": False,
            "diff_relative": True,
        }
    )
    plot(
        {
            "relative_key": "area",
            "ylabel": "CHF pro 100m2 Fläche",
            "sorted": True,
            "anon": False,
            "diff_relative": False,
        }
    )


def plot(spec):
    data = {
        "Wohnen": [],
        "Gewerbe": [],
        "Lager": [],
    }
    for sect in data:
        for _cat in nk.categories:
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
    for o in nk.objects:
        if o["name"] in ("0000", "9998", "9999"):
            continue
        obj_relative_key = o[spec["relative_key"]]
        if not obj_relative_key:
            nk.log.append("Skipping object with no %s: %s" % (spec["relative_key"], o["name"]))
            continue
        elif obj_relative_key < 0:
            nk.log.append(
                "Skipping object with negative %s: %s" % (spec["relative_key"], o["name"])
            )
            continue
        # if o['name'] != "011":
        #    continue
        # for key in o:
        #    nk.log.append(" - %s: %s" % (key, o[key]))
        cost_bin = len(nk.categories) * [0]
        total = 0
        total_amount = 0
        reduced_amount = 0
        for c in nk.costs:
            amount = c["cost_split"]["objects"][o["name"]]["annual"]["amount"]
            cost_bin[nk.categories[c["category"]]["i"]] += amount / obj_relative_key * 100
            total += amount / obj_relative_key * 100
            total_amount += amount
            if c["name"] not in ("Strom_Total", "Internet/WLAN"):
                reduced_amount += amount

        if o["section"] in data:
            for cat in nk.categories:
                data[o["section"]][nk.categories[cat]["i"]].append(
                    cost_bin[nk.categories[cat]["i"]]
                )
            data_extra[o["section"]]["akonto"].append(o["akonto_obj"] / obj_relative_key * 100)
            data_extra[o["section"]]["relative_quantity"].append(obj_relative_key)
            data_extra[o["section"]]["akonto_amount"].append(o["akonto_obj"])
            data_extra[o["section"]]["obj"].append("_" + o["name"])
            data_extra[o["section"]]["total"].append(total)
            data_extra[o["section"]]["total_amount"].append(total_amount)
            data_extra[o["section"]]["reduced_amount"].append(reduced_amount)
            # if o['name'] == "001":
            #    nk.log.append("%s: total=%s total_amount=%s reduced_amount=%s akonto_amount=%s" % (o['name'],total,total_amount,reduced_amount,o['akonto']))

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
        nk.log.append(
            "Average total %s %s: %s (%s / %s)"
            % (spec["relative_key"], sect, total_sum / total_rel, total_sum, total_rel)
        )
        nk.log.append(
            "Average total_reduced %s %s: %s (%s / %s)"
            % (
                spec["relative_key"],
                sect,
                total_reduced_sum / total_rel,
                total_reduced_sum,
                total_rel,
            )
        )
        nk.log.append(
            "Average akonto %s %s: %s (%s / %s)"
            % (spec["relative_key"], sect, total_akonto / total_rel, total_akonto, total_rel)
        )
        grand_total_sum += total_sum
        grand_total_reduced_sum += total_reduced_sum
        grand_total_rel += total_rel
        grand_total_akonto_sum += total_akonto
    nk.log.append(
        "Average total %s %s: %s (%s / %s)"
        % (
            spec["relative_key"],
            "ALL",
            grand_total_sum / grand_total_rel,
            grand_total_sum,
            grand_total_rel,
        )
    )
    nk.log.append(
        "Average total_reduced %s %s: %s (%s / %s)"
        % (
            spec["relative_key"],
            "ALL",
            grand_total_reduced_sum / grand_total_rel,
            grand_total_reduced_sum,
            grand_total_rel,
        )
    )
    nk.log.append(
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
        for cat in nk.categories:
            y = np.array(data[section][nk.categories[cat]["i"]])
            if spec["sorted"]:
                y = y[sort]
            if nk.categories[cat]["i"] == 0:
                # nk.log.append(x)
                # nk.log.append(y)
                ax.bar(x, y, label=nk.categories[cat]["label"])
                y_bottom = y
            else:
                ax.bar(x, y, bottom=y_bottom, label=nk.categories[cat]["label"])
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
        filename = nk.get_output_filename(
            f"plots/nk_plot_{filename_part}.png", plot_name, "Übersicht"
        )
        # output = open(filename, 'w')
        # canvas.print_png(output)
        # output.close()
        plt.savefig(filename, dpi=300)
        plt.close()
        nk.log.append("Plot in %s" % filename)

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
            x, y2, "r-", label="Differenz zu Akonto-Zahlungen (ohne Strom/Internet)", where="mid"
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
        filename = nk.get_output_filename(
            f"plots/nk_plot_{filename_part}.png", plot_name, "Übersicht"
        )
        # output = open(filename, 'w')
        # canvas.print_png(output)
        # output.close()
        plt.savefig(filename, dpi=300)
        plt.close()
        nk.log.append("Plot in %s" % filename)


def format_amount(number):
    if number == "":
        return number
    return nformat(number, round_to=0.05)
    # return 0.05 * round(number/0.05)


def format_percent(number):
    return round(number)


def nformat(number, precision=2, round_to=False, thousands_separator="'"):
    if round_to:
        number = round_to * round(number / round_to)
    if thousands_separator:
        return format(number, ",.%df" % precision).replace(",", thousands_separator)
    else:
        return format(number, ".%df" % precision)


def calc_totals():
    ## Get total weights per section and overall (per month)
    for w in nk.object_weights:
        # totals[w] = {'all': [0,0,0,0,0,0,0,0,0,0,0,0] }
        nk.totals[w] = {"all": 0}
    for o in nk.objects:
        for w in nk.object_weights:
            if o["section"] not in nk.totals[w]:
                nk.totals[w][o["section"]] = 0  # [0,0,0,0,0,0,0,0,0,0,0,0]
            if w not in o:
                nk.log.append("WARNING: Object %s has no weight %s" % (o["name"], w))
                nk.add_warning(f"Objekt hat keine Gewichtung {w}", o["name"])
                o[w] = 0
                continue
            # if not isinstance(o[w], list):
            #    ## Expand weight to monthly array
            #    o["%s_scalar" % w] = o[w]
            #    o[w] = []
            #    for m in range(0,12):
            #        o[w].append(nk.monthly_weights['default'][m]*o["%s_scalar" % w])
            # for m in range(0,12):
            #    nk.totals[w][o['section']][m] += o[w][m]
            #    nk.totals[w]['all'][m] += o[w][m]
            if isinstance(o[w], list):
                nk.totals[w][o["section"]] += sum(o[w])
                nk.totals[w]["all"] += sum(o[w])
            else:
                nk.totals[w][o["section"]] += o[w]
                nk.totals[w]["all"] += o[w]


def add_admin_fee():
    ## Get totals and add admin fee
    admin_fee = {
        "name": "Verwaltungsaufwand",
        "category": "verwaltung",
        "cost_split": {"total": {}, "sections": {}, "objects": {}},
    }
    tot = {"name": "Gesamtbetrag", "cost_split": {"total": {}, "sections": {}, "objects": {}}}

    ## Initialize
    tot["cost_split"]["total"] = {
        "monthly": {
            "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "percent": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
            "weight": 12 * [0],
        },
        "annual": {"amount": 0, "percent": 100, "weight": 0},
    }
    admin_fee["cost_split"]["total"] = {
        "monthly": {
            "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "percent": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
            "weight": 12 * [0],
        },
        "annual": {"amount": 0, "percent": 100, "weight": 0},
    }
    for s in nk.sections:
        tot["cost_split"]["sections"][s] = {
            "monthly": {
                "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "percent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "weight": 12 * [0],
            },
            "annual": {"amount": 0, "percent": 100, "weight": 0},
        }
        admin_fee["cost_split"]["sections"][s] = {
            "monthly": {
                "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "percent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "weight": 12 * [0],
            },
            "annual": {"amount": 0, "percent": 100, "weight": 0},
        }
    for o in nk.objects:
        tot["cost_split"]["objects"][o["name"]] = {
            "monthly": {
                "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "percent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "weight": 12 * [0],
            },
            "annual": {"amount": 0, "percent": 100, "weight": 0},
        }
        admin_fee["cost_split"]["objects"][o["name"]] = {
            "monthly": {
                "amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "percent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "weight": 12 * [0],
            },
            "annual": {"amount": 0, "percent": 100, "weight": 0},
        }
    ## Do the adding
    for cost in nk.costs:
        if "amount_meta" in cost:
            ## Skip Allgemeinanteile
            continue
        tot["cost_split"]["total"]["annual"]["amount"] += cost["cost_split"]["total"]["annual"][
            "amount"
        ]
        for m in range(12):
            tot["cost_split"]["total"]["monthly"]["amount"][m] += cost["cost_split"]["total"][
                "monthly"
            ]["amount"][m]
    # admin_fee['cost_split']['total']['annual']['amount'] = nk.admin_fee_factor * tot['cost_split']['total']['annual']['amount']
    # tot['cost_split']['total']['annual']['amount'] += admin_fee['cost_split']['total']['annual']['amount']

    for s in nk.sections:
        for cost in nk.costs:
            tot["cost_split"]["sections"][s]["annual"]["amount"] += cost["cost_split"]["sections"][
                s
            ]["annual"]["amount"]
            for m in range(12):
                tot["cost_split"]["sections"][s]["monthly"]["amount"][m] += cost["cost_split"][
                    "sections"
                ][s]["monthly"]["amount"][m]
    #    admin_fee['cost_split']['sections'][s]['annual']['amount'] = nk.admin_fee_factor * tot['cost_split']['sections'][s]['annual']['amount']
    #    tot['cost_split']['sections'][s]['annual']['amount'] += admin_fee['cost_split']['sections'][s]['annual']['amount']

    for obj in nk.objects:
        o = obj["name"]
        if o in ("0000", "9998", "9999"):
            continue
        for cost in nk.costs:
            tot["cost_split"]["objects"][o]["annual"]["amount"] += cost["cost_split"]["objects"][
                o
            ]["annual"]["amount"]
            for m in range(12):
                tot["cost_split"]["objects"][o]["monthly"]["amount"][m] += cost["cost_split"][
                    "objects"
                ][o]["monthly"]["amount"][m]

        admin_fee["cost_split"]["objects"][o]["annual"]["amount"] = (
            nk.admin_fee_factor * tot["cost_split"]["objects"][o]["annual"]["amount"]
        )
        tot["cost_split"]["objects"][o]["annual"]["amount"] += admin_fee["cost_split"]["objects"][
            o
        ]["annual"]["amount"]

        admin_fee["cost_split"]["sections"][obj["section"]]["annual"]["amount"] += admin_fee[
            "cost_split"
        ]["objects"][o]["annual"]["amount"]
        tot["cost_split"]["sections"][obj["section"]]["annual"]["amount"] += admin_fee[
            "cost_split"
        ]["objects"][o]["annual"]["amount"]

        admin_fee["cost_split"]["total"]["annual"]["amount"] += admin_fee["cost_split"]["objects"][
            o
        ]["annual"]["amount"]
        tot["cost_split"]["total"]["annual"]["amount"] += admin_fee["cost_split"]["objects"][o][
            "annual"
        ]["amount"]

        for m in range(12):
            admin_fee["cost_split"]["objects"][o]["monthly"]["amount"][m] = (
                nk.admin_fee_factor * tot["cost_split"]["objects"][o]["monthly"]["amount"][m]
            )
            tot["cost_split"]["objects"][o]["monthly"]["amount"][m] += admin_fee["cost_split"][
                "objects"
            ][o]["monthly"]["amount"][m]

            admin_fee["cost_split"]["sections"][obj["section"]]["monthly"]["amount"][m] += (
                admin_fee["cost_split"]["objects"][o]["monthly"]["amount"][m]
            )
            tot["cost_split"]["sections"][obj["section"]]["monthly"]["amount"][m] += admin_fee[
                "cost_split"
            ]["objects"][o]["monthly"]["amount"][m]

            admin_fee["cost_split"]["total"]["monthly"]["amount"][m] += admin_fee["cost_split"][
                "objects"
            ][o]["monthly"]["amount"][m]
            tot["cost_split"]["total"]["monthly"]["amount"][m] += admin_fee["cost_split"][
                "objects"
            ][o]["monthly"]["amount"][m]

    nk.costs.append(admin_fee)
    nk.totals["amounts"] = tot
    # nk.costs.append(nk.totals)


def assign_to_contracts():
    monthly_weights_sum = sum(nk.monthly_weights["default"])
    ## Assign costs for every object and month to a contract or to 'owner' (Genossenschaft) or 'empty' (Leerstand)
    for o in nk.objects:
        if o["name"] in ("0000", "9998", "9999"):
            ## Skip special objects
            continue
        nk.log.append("+++ Object: %s" % o["name"])
        # if o['name'] == "108":
        #    nk.log.append(o)
        for idx, date in enumerate(nk.dates):
            active_contract = None
            if "contracts" in o:
                for c_id in o["contracts"]:
                    if nk.contracts[c_id]["billing_date_start"] <= date["start"] and (
                        not nk.contracts[c_id]["billing_date_end"]
                        or nk.contracts[c_id]["billing_date_end"] > date["start"]
                    ):
                        ## Contract is active in this month
                        if active_contract:
                            raise RuntimeError(
                                "More than one active contract for object %s and date %s: %s and %s"
                                % (o["name"], date["start"], active_contract, c_id)
                            )
                        active_contract = c_id
                        if "period_start" not in nk.contracts[c_id]:
                            nk.contracts[c_id]["period_start"] = date["start"]
                        if (
                            "period_end" not in nk.contracts[c_id]
                            or date["end"] > nk.contracts[c_id]["period_end"]
                        ):
                            nk.contracts[c_id]["period_end"] = date["end"]

                    # if len(o['contracts']):
                    #    nk.log.append("Object %s: Checking multiple contracts: %s -> active=%s [%s - %s]" % (o['name'],c_id,active_contract,date['start'],date['end']))

            if active_contract:
                c_id = active_contract
            else:
                ## Add to "virtual" contract
                if o["name"] in nk.virtual_contracts_map:
                    c_id = nk.virtual_contracts_map[o["name"]]
                elif o["allgemein"]:
                    c_id = "-5"  # Allgemein
                else:
                    c_id = "-6"  # Leerstand
                if c_id not in nk.contracts:
                    nk.contracts[c_id] = {
                        "id": c_id,
                        "virtual": nk.virtual_contracts[c_id],
                        "period_start": date["start"],
                        "akonto_billing": 0,
                    }
                if (
                    "period_end" not in nk.contracts[c_id]
                    or date["end"] > nk.contracts[c_id]["period_end"]
                ):
                    nk.contracts[c_id]["period_end"] = date["end"]
                nk.log.append(
                    " - %s: No contract -> virtual %s (%s)"
                    % (date["start"], c_id, nk.virtual_contracts[c_id])
                )

            if c_id not in nk.active_contracts:
                nk.active_contracts.append(c_id)

            if "objects" not in nk.contracts[c_id]:
                nk.contracts[c_id]["objects"] = {}
                nk.contracts[c_id]["all_objects"] = {
                    "amount": 0,
                    "akonto_obj": 0,
                    "building_total": 0,
                }

            if o["name"] not in nk.contracts[c_id]["objects"]:
                nk.contracts[c_id]["objects"][o["name"]] = {}

            obj_data = nk.contracts[c_id]["objects"][o["name"]]

            if "costs" not in obj_data:
                ## Create data structure
                obj_data["costs"] = {}
                for cost in nk.costs:
                    obj_data["costs"][cost["name"]] = {
                        "amount": 0,
                        "weight": 0,
                        #'weight_count': 0,
                        "total_amount": 0,
                        "total_weight": 0,
                        "total_weight_sect": 0,
                        "category": cost["category"],
                        "object_weights": cost.get("object_weights", None),
                        "section_weights": cost.get("section_weights", None),
                        "meta": "amount_meta" in cost,
                    }
                obj_data["messung"] = {
                    "warmwasser": 0,
                    "heizung": 0,
                }
                obj_data["strom"] = {
                    "solar_eigen": {"kwh": 0, "chf": 0},  ## Solar Eigenverbrauch
                    "solar_speicher": {"kwh": 0, "chf": 0},  ## Solar via Zwischenspeicher
                    "solar_einkauf": {"kwh": 0, "chf": 0},  ## Solar eingekauft
                    "ew_hoch": {"kwh": 0, "chf": 0},  ## Netzstrom (Normaltarif)
                    "ew_nieder": {"kwh": 0, "chf": 0},  ## Netzstrom (Spartarif)
                    "korrektur": {"kwh": 0, "chf": 0},  ## Korrektur
                    "total_netz": {"kwh": 0, "chf": 0},  ## Total Netzstrom (Speicher + Einkauf)
                    "total": {"kwh": 0, "chf": 0},  ## Total (Eigenverbrauch + Netzstrom)
                }
                obj_data["strom_building"] = copy.deepcopy(obj_data["strom"])
                obj_data["strom_building"]["total_sect"] = {
                    "kwh": 0,
                    "chf": 0,
                }  ## Total for section
                obj_data["unit"] = {
                    "rent_net": 0,
                    "akonto_obj": 0,
                    "akonto_obj_billing": 0,
                    "nk_pauschal_obj": 0,
                    "strom_pauschal_obj": 0,
                    "area": o["area"],
                    "volume": o["volume"],
                    "section": o["section"],
                    "id": o["id"],
                    "name": o["name"],
                    "label": o["label"],
                    "dates": [],
                }
                obj_data["amount_sum"] = 0

            ## Add data
            for cost in nk.costs:
                obj_data["costs"][cost["name"]]["amount"] += cost["cost_split"]["objects"][
                    o["name"]
                ]["monthly"]["amount"][idx]
                obj_data["amount_sum"] += cost["cost_split"]["objects"][o["name"]]["monthly"][
                    "amount"
                ][idx]
                nk.contracts[c_id]["all_objects"]["amount"] += cost["cost_split"]["objects"][
                    o["name"]
                ]["monthly"]["amount"][idx]
                obj_data["costs"][cost["name"]]["total_amount"] += cost["cost_split"]["total"][
                    "monthly"
                ]["amount"][idx]
                ## Weight
                obj_data["costs"][cost["name"]]["weight"] += cost["cost_split"]["objects"][
                    o["name"]
                ]["monthly"]["weight"][idx]
                obj_data["costs"][cost["name"]]["total_weight"] += cost["cost_split"]["total"][
                    "monthly"
                ]["weight"][idx]
                obj_data["costs"][cost["name"]]["total_weight_sect"] += cost["cost_split"][
                    "sections"
                ][o["section"]]["monthly"]["weight"][idx]
                # if 'object_weights' in cost:
                #    if cost['object_weights'].startswith('area'):
                #        obj_data['costs'][cost['name']]['weight'] += o[cost['object_weights']] * nk.section_weights[cost['section_weights']][o['section']]
                #        obj_data['costs'][cost['name']]['weight_count'] += 1
                #    else:
                #        obj_data['costs'][cost['name']]['weight'] += o[cost['object_weights']][idx] * nk.section_weights[cost['section_weights']][o['section']]
                #        obj_data['costs'][cost['name']]['weight_count'] = 1

            # if o['messung_warmwasser']:
            #    obj_data['messung']['warmwasser'] += o['messung_warmwasser'][idx]
            # if o['messung_heizung']:
            #    obj_data['messung']['heizung'] += o['messung_heizung'][idx]

            if "messung_strom_solar" in o:
                obj_data["strom"]["solar_eigen"]["kwh"] += o["messung_strom_solar"][idx]
                obj_data["strom"]["solar_eigen"]["chf"] += o["chf_solar_eigen"][idx]
                obj_data["strom"]["solar_speicher"]["kwh"] += o["kwh_solar_speicher"][idx]
                obj_data["strom"]["solar_speicher"]["chf"] += o["chf_solar_einspeise"][idx]
                obj_data["strom"]["solar_einkauf"]["kwh"] += o["kwh_solar_einkauf"][idx]
                obj_data["strom"]["solar_einkauf"]["chf"] += o["chf_solar_hkn"][idx]
                obj_data["strom"]["ew_hoch"]["kwh"] += o["messung_strom_ew_hoch"][idx]
                obj_data["strom"]["ew_hoch"]["chf"] += o["messung_chf_netz_hoch"][idx]
                obj_data["strom"]["ew_nieder"]["kwh"] += o["messung_strom_ew_nieder"][idx]
                obj_data["strom"]["ew_nieder"]["chf"] += o["messung_chf_netz_nieder"][idx]
                obj_data["strom"]["korrektur"]["kwh"] += o["kwh_korrektur"][idx]
                obj_data["strom"]["korrektur"]["chf"] += o["chf_korrektur"][idx]
                ## total CHF = eigen + speicher + einkauf + hoch + nieder + korrektur
                ## total kWh = eigen + hoch + nieder
                obj_data["strom"]["total"]["kwh"] += o["kwh_total"][idx]
                obj_data["strom"]["total"]["chf"] += o["chf_total"][idx]
                ## netz  kWh = hoch + nieder
                obj_data["strom"]["total_netz"]["kwh"] += o["kwh_netzstrom"][idx]

            if True:
                for item in (
                    "solar_eigen",
                    "solar_speicher",
                    "solar_einkauf",
                    "ew_hoch",
                    "ew_nieder",
                    "korrektur",
                    "total",
                    "total_netz",
                ):
                    for u in ("kwh", "chf"):
                        obj_data["strom_building"][item][u] += nk.strom_total[item][u][idx]
                for u in ("kwh", "chf"):
                    obj_data["strom_building"]["total_sect"][u] += nk.strom_total["total_sect"][
                        o["section"]
                    ][u][idx]

            obj_data["unit"]["rent_net"] += (
                o["rent_net"] / monthly_weights_sum * nk.monthly_weights["default"][idx]
            )
            obj_data["unit"]["akonto_obj"] += (
                o["akonto_obj"] / monthly_weights_sum * nk.monthly_weights["default"][idx]
            )
            nk.contracts[c_id]["all_objects"]["akonto_obj"] += (
                o["akonto_obj"] / monthly_weights_sum * nk.monthly_weights["default"][idx]
            )
            obj_data["unit"]["nk_pauschal_obj"] += (
                o["nk_pauschal_obj"] / monthly_weights_sum * nk.monthly_weights["default"][idx]
            )
            obj_data["unit"]["strom_pauschal_obj"] += (
                o["strom_pauschal_obj"] / monthly_weights_sum * nk.monthly_weights["default"][idx]
            )
            obj_data["unit"]["dates"].append(date)

    ## Calculate akonto_billing_obj from total aktonto_billing and ratio of akonto_obj to sum(akonto_obj)
    for c_id in nk.contracts:
        if "all_objects" in nk.contracts[c_id] and nk.contracts[c_id]["all_objects"]["akonto_obj"]:
            if (
                nk.contracts[c_id]["all_objects"]["akonto_obj"]
                != nk.contracts[c_id]["akonto_billing"]
            ):
                nk.log.append(
                    "WARNING: Billed akonto %s != sum(akonto_obj) %s for contract %s -> Scaling akonto accordingly per object."
                    % (
                        nk.contracts[c_id]["akonto_billing"],
                        nk.contracts[c_id]["all_objects"]["akonto_obj"],
                        c_id,
                    )
                )
            if "objects" in nk.contracts[c_id]:
                for o_id in nk.contracts[c_id]["objects"]:
                    obj_data = nk.contracts[c_id]["objects"][o_id]
                    obj_data["unit"]["akonto_billing_obj"] = (
                        obj_data["unit"]["akonto_obj"]
                        * nk.contracts[c_id]["akonto_billing"]
                        / nk.contracts[c_id]["all_objects"]["akonto_obj"]
                    )
                    if obj_data["unit"]["akonto_billing_obj"] != obj_data["unit"]["akonto_obj"]:
                        nk.log.append(
                            "    %s: %s -> %s"
                            % (
                                o_id,
                                obj_data["unit"]["akonto_obj"],
                                obj_data["unit"]["akonto_billing_obj"],
                            )
                        )
                        nk.add_warning(
                            f"Vertrag {c_id}: In Rechnung gestelltes NK-Akonto stimmt nicht mit NK-Akontosumme der Objekte überein. Skaliere Akonto pro Objekt entsprechend.",
                            f"{o_id}: {obj_data['unit']['akonto_obj']} -> {obj_data['unit']['akonto_billing_obj']}",
                        )

    ## Remove objects with no costs
    for c_id in nk.contracts:
        if "objects" in nk.contracts[c_id]:
            delete = []
            for o_id in nk.contracts[c_id]["objects"]:
                if not nk.contracts[c_id]["objects"][o_id]["amount_sum"]:
                    nk.log.append("Removing object %s from contract %s" % (o_id, c_id))
                    delete.append(o_id)
            for o_id in delete:
                del nk.contracts[c_id]["objects"][o_id]

    ## Add total costs of building
    for c_id in nk.contracts:
        if "all_objects" not in nk.contracts[c_id]:
            continue
        for cost in nk.costs:
            total = 0
            for idx, date in enumerate(nk.dates):
                if (
                    "period_start" in nk.contracts[c_id]
                    and date["start"] >= nk.contracts[c_id]["period_start"]
                    and date["start"] < nk.contracts[c_id]["period_end"]
                ):
                    total += cost["cost_split"]["total"]["monthly"]["amount"][idx]
            if "amount_meta" not in cost:
                ## Skip Anteile an Allgemein, da schon im Total enthalen!
                nk.contracts[c_id]["all_objects"]["building_total"] += total


#        nk.contracts[c_id]['all_objects']['building_costs'] = {}
#        nk.contracts[c_id]['all_objects']['building_weights'] = {}
#        nk.contracts[c_id]['all_objects']['building_total'] = 0
#        for cost in nk.costs:
#            total = 0
#            total_weight = 0
#            weight_count = 0
#            for idx, date in enumerate(dates):
#                if 'period_start' in nk.contracts[c_id] and date['start'] >= nk.contracts[c_id]['period_start'] and date['start'] < nk.contracts[c_id]['period_end']:
#                    total += cost['cost_split']['total']['monthly']['amount'][idx]
#                    if 'weight' in cost['cost_split']['total']['monthly']:
#                        total_weight += cost['cost_split']['total']['monthly']['weight'][idx]
#                        weight_count += 1
#            nk.contracts[c_id]['all_objects']['building_costs'][cost['name']] = total
#            if 'object_weights' in cost and cost['object_weights'].startswith('area') and weight_count:
#                nk.contracts[c_id]['all_objects']['building_weights'][cost['name']] = total_weight/weight_count
#            else:
#                nk.contracts[c_id]['all_objects']['building_weights'][cost['name']] = total_weight
#            #for obj_data in nk.contracts[c_id]['objects']:
#            #    nk.contracts[c_id]['all_objects']['building_weights'][cost['name']] += obj_data['costs'][cost['name']]['weight']/obj_data['costs'][cost['name']]['weight_count']
#            if 'amount_meta' not in cost:
#                ## Skip Anteile an Allgemein, da schon im Total enthalen!
#                nk.contracts[c_id]['all_objects']['building_total'] += total
#
## Measurements/weights
#        total_area = 0
#        total_area_warmwasser = 0
#        total_messung_warmwasser = 0
#        count = 0
#        for idx, date in enumerate(dates):
#            if 'period_start' in nk.contracts[c_id] and date['start'] >= nk.contracts[c_id]['period_start'] and date['start'] < nk.contracts[c_id]['period_end']:
#                total_area += nk.totals['area']['all'][idx]
#                total_area_warmwasser += nk.totals['area_warmwasser']['all'][idx]
#                total_messung_warmwasser += nk.totals['messung_warmwasser']['all'][idx]
#                count += 1
#        if count:
#            nk.contracts[c_id]['all_objects']['building_costs']['area'] = total_area/count
#            nk.contracts[c_id]['all_objects']['building_costs']['area_warmwasser'] = total_area_warmwasser/count
#        else:
#            nk.contracts[c_id]['all_objects']['building_costs']['area'] = 0
#            nk.contracts[c_id]['all_objects']['building_costs']['area_warmwasser'] = 0
#        nk.contracts[c_id]['all_objects']['building_costs']['messung_warmwasser'] = total_messung_warmwasser


def create_bills(regenerate_invoice_id=None):
    ## Overall costs
    bill_costs_map = OrderedDict()
    bill_costs_map["Hauswartung, Service Heizung/Lüftung"] = ["Hauswartung_ServiceHeizungLüftung"]
    bill_costs_map["Reinigung"] = ["Reinigung"]
    bill_costs_map["Winterdienst"] = ["Winterdienst"]
    bill_costs_map["Siedlung/Umgebungspflege"] = ["Umgebung_Siedlung"]
    bill_costs_map["Betriebskosten Gemeinschaftsanlagen"] = ["Betriebskosten_Gemeinschaft"]
    bill_costs_map["Lift"] = ["Lift"]
    bill_costs_map["Kehrichtgebühren"] = ["Kehrichtgebuehren"]
    bill_costs_map["Wärmekosten"] = [
        "Fernwaerme_Fussboden_Grundkosten",
        "Fernwaerme_Fussboden_Verbrauch",
        "Fernwaerme_Radiatoren",
        "Fernwaerme_Lueftung",
        "Fernwaerme_Warmwasser_Grundkosten",
        "Fernwaerme_Warmwasser_Verbrauch",
        "Anteil_Allgemein_Warmwasser_Verbrauch",
    ]
    bill_costs_map["Wasserkosten"] = [
        "Wasser_Abwasser_Grundkosten",
        "Wasser_Abwasser_Verbrauch",
        "Anteil_Allgemein_Wasser_Abwasser_Verbrauch",
    ]
    bill_costs_map["Stromkosten"] = [
        "Strom_Total",
        "Anteil_Allgemein_Strom",
        "Serviceabo Energiemessung",
    ]
    bill_costs_map["Internet/WLAN"] = ["Internet/WLAN"]
    bill_costs_map["Verwaltungsaufwand %s%%" % nformat(nk.admin_fee_factor * 100, 1)] = [
        "Verwaltungsaufwand"
    ]

    billing_date = nk.dates[-1]["end"].strftime("%d.%m.%Y")

    ## Detailed costs
    context_map = {
        "wwg": {"cost": "Fernwaerme_Warmwasser_Grundkosten"},
        "wwv": {"cost": "Fernwaerme_Warmwasser_Verbrauch"},
        "wwbt": {"sum": ["wwg", "wwv"]},
        "wwa": {"cost": "Anteil_Allgemein_Warmwasser_Verbrauch"},
        "wwt": {"sum": ["wwbt", "wwa"]},
        "hfg": {"cost": "Fernwaerme_Fussboden_Grundkosten"},
        "hfv": {"cost": "Fernwaerme_Fussboden_Verbrauch"},
        "hr": {"cost": "Fernwaerme_Radiatoren"},
        "hl": {"cost": "Fernwaerme_Lueftung"},
        "ht": {"sum": ["hfg", "hfv", "hr", "hl"]},
        "sw": {"sum": ["wwbt", "wwa", "ht"], "exclude_in_building_sum": ["wwa"]},
        "wag": {"cost": "Wasser_Abwasser_Grundkosten"},
        "wav": {"cost": "Wasser_Abwasser_Verbrauch"},
        "wat": {"sum": ["wag", "wav"]},
        "waa": {"cost": "Anteil_Allgemein_Wasser_Abwasser_Verbrauch"},
        "swa": {"sum": ["wat", "waa"], "exclude_in_building_sum": ["waa"]},
        ## Strom
        "ssd": {"strom": "solar_eigen"},
        "sss": {"strom": "solar_speicher"},
        "snh": {"strom": "ew_hoch"},
        "snt": {"strom": "ew_nieder"},
        "shk": {"strom": "solar_einkauf"},
        "sk": {"strom": "korrektur"},
        "st": {"strom": "total"},
        "stn": {"strom": "total_netz"},
        "sa": {"cost": "Anteil_Allgemein_Strom"},
        "snk": {"cost": "Serviceabo Energiemessung"},
        "stot": {"sum": ["st", "sa", "snk"], "exclude_in_building_sum": ["sa"]},
    }

    for c_id in nk.active_contracts:
        contract_str = "%s" % c_id
        contract_formal_str = "Dein/Euer"
        if int(c_id) < 1:  # or c_id != 92:
            contract_str = "virtual%s" % contract_str
            contract_info = contract_str
            # nk.log.append("Skipping virtual contract %s for now..." % c_id)
            # continue
        else:
            try:
                contract_info = "%05d" % int(c_id)
            except ValueError:
                contract_info = c_id
            if nk.contracts[c_id]["contact_formal"] == "Sie":
                contract_formal_str = "Ihr"
            # nk.log.append("Skipping normal contract %s for now..." % c_id)
            # continue

        ## Testing
        if nk.limit_bills_to_contract_ids and c_id not in nk.limit_bills_to_contract_ids:
            nk.log.append("Skipping contract %s for TESTING..." % c_id)
            continue

        # for oi in nk.contracts[c_id]['objects']:
        #    contract_str = "%s_%s" % (contract_str, oi)
        nk.log.append("Creating bill for contract %s" % contract_str)
        context = {
            "contract_id": c_id,
            "Euer": contract_formal_str,
            "contract_info": contract_info,
            "contract_period": "%s – %s"
            % (
                nk.contracts[c_id]["period_start"].strftime("%d.%m.%Y"),
                nk.contracts[c_id]["period_end"].strftime("%d.%m.%Y"),
            ),
            "billing_period": "%s – %s"
            % (
                nk.dates[nk.period_start_index]["start"].strftime("%d.%m.%Y"),
                nk.dates[-1]["end"].strftime("%d.%m.%Y"),
            ),
            "billing_period_start": nk.dates[nk.period_start_index]["start"].strftime("%Y-%m-%d"),
            "billing_period_end": nk.dates[-1]["end"].strftime("%Y-%m-%d"),
            "s_chft": nformat(nk.totals["amounts"]["cost_split"]["total"]["annual"]["amount"]),
            "bill_lines": [],
            "total_amount": 0,
            "total_akonto": nk.contracts[c_id]["akonto_billing"],
            "betreff": "Nebenkostenabrechnung",
        }
        objects = []
        for o_id in nk.contracts[c_id]["objects"]:
            ## Overall costs
            obj = nk.contracts[c_id]["objects"][o_id]
            if int(c_id) < 1:
                ## No akonto for virtual contracts
                obj_akonto = 0
                ## Border dates
                periods = []
                start = None
                prev = None
                for d in nk.dates[nk.period_start_index :]:
                    if d in obj["unit"]["dates"]:
                        if not start:
                            start = d
                    elif start and prev:
                        ## End of period
                        periods.append(
                            "%s – %s"
                            % (
                                start["start"].strftime("%d.%m.%Y"),
                                prev["end"].strftime("%d.%m.%Y"),
                            )
                        )
                        start = None
                    prev = d
                if start and prev:
                    periods.append(
                        "%s – %s"
                        % (start["start"].strftime("%d.%m.%Y"), prev["end"].strftime("%d.%m.%Y"))
                    )
                context["contract_period"] = ", ".join(periods)
            else:
                obj_akonto = obj["unit"]["akonto_billing_obj"]
            obj_diff = obj["amount_sum"] - obj_akonto
            context["rental_unit"] = obj["unit"]["label"]
            context["rental_nr"] = obj["unit"]["name"]
            context["s_chf"] = nformat(obj["amount_sum"])
            context["akonto_num"] = obj_akonto
            context["akonto_chf"] = nformat(obj_akonto)
            context["diff_chf"] = nformat(obj_diff)
            context["costs"] = []
            context["has_graph"] = False
            obj["has_graph"] = False
            for title, cost_names in bill_costs_map.items():
                object_cost = 0
                building_cost = 0
                for cname in cost_names:
                    if cname not in obj["costs"]:
                        continue
                    object_cost += obj["costs"][cname]["amount"]
                    if not obj["costs"][cname]["meta"]:
                        ## Exclude Allgemeinanteile since they are already in the total
                        # building_cost += obj['costs'][cname]['total_amount']
                        building_cost += nk.costs[nk.cost_indices[cname]]["cost_split"]["total"][
                            "annual"
                        ]["amount"]
                if object_cost == 0 and building_cost == 0:
                    continue
                if building_cost:
                    share = "%s%%" % nformat(object_cost / building_cost * 100.0, 2)
                else:
                    share = "-"
                c = {
                    "name": title,
                    "chft": nformat(building_cost),
                    "chf": nformat(object_cost),
                    "pctt": nformat(
                        building_cost
                        / nk.totals["amounts"]["cost_split"]["total"]["annual"]["amount"]
                        * 100.0,
                        1,
                    ),
                    "pct": nformat(object_cost / obj["amount_sum"] * 100, 1),
                    "share": share,
                }
                context["costs"].append(c)

            ## Detailed costs (Wärme, Wasser...)
            oc = obj["costs"]
            for abr in context_map:
                if "cost" in context_map[abr]:
                    ## Total building costs
                    # context[abr+"_chft"] = oc[ context_map[abr]['cost'] ]['total_amount']
                    context[abr + "_chft"] = nk.costs[nk.cost_indices[context_map[abr]["cost"]]][
                        "cost_split"
                    ]["total"]["annual"]["amount"]
                    ## Object costs
                    context[abr + "_chf"] = oc[context_map[abr]["cost"]]["amount"]
                    ## Total building weight
                    # context[abr+"t"] = oc[ context_map[abr]['cost'] ]['total_weight']
                    context[abr + "t"] = nk.costs[nk.cost_indices[context_map[abr]["cost"]]][
                        "cost_split"
                    ]["total"]["annual"]["weight"]
                    ## Price per unit
                    context[abr + "_eh"] = (
                        context[abr + "_chft"] / context[abr + "t"] if context[abr + "t"] else 0
                    )
                    ## Object weight
                    # oc[ context_map[abr]['cost'] ]['weight']
                    context[abr] = (
                        context[abr + "_chf"] / context[abr + "_eh"] if context[abr + "_eh"] else 0
                    )

            ## Detailed Strom
            oso = obj["strom"]
            for abr in context_map:
                if "strom" in context_map[abr]:
                    ## Total building costs
                    # context[abr+"_chft"] = ost[ context_map[abr]['strom'] ]['chf']
                    context[abr + "_chft"] = sum(nk.strom_total[context_map[abr]["strom"]]["chf"])
                    ## Object costs
                    context[abr + "_chf"] = oso[context_map[abr]["strom"]]["chf"]
                    ## Total building weight
                    # context[abr+"t"] = ost[ context_map[abr]['strom'] ]['kwh']
                    context[abr + "t"] = sum(nk.strom_total[context_map[abr]["strom"]]["kwh"])
                    ## Object weight
                    context[abr] = oso[context_map[abr]["strom"]]["kwh"]
                    ## Price per unit
                    context[abr + "_eh"] = (
                        context[abr + "_chft"] / context[abr + "t"] if context[abr + "t"] else 0
                    )

            ## Sums
            for abr in context_map:
                if "sum" in context_map[abr]:
                    context[abr + "_chft"] = 0
                    context[abr + "_chf"] = 0
                    context[abr + "t"] = 0
                    context[abr] = 0
                    context[abr + "_eh"] = 0
                    for parts in context_map[abr]["sum"]:
                        context[abr + "_chf"] += context[parts + "_chf"]
                        context[abr] += context[parts]
                        if (
                            "exclude_in_building_sum" in context_map[abr]
                            and parts in context_map[abr]["exclude_in_building_sum"]
                        ):
                            ## Exclude this in the total building sum because it is already included
                            continue
                        context[abr + "_chft"] += context[parts + "_chft"]
                        context[abr + "t"] += context[parts + "t"]

            ## Format
            for abr in context_map:
                context[abr + "_chft"] = nformat(context[abr + "_chft"])
                context[abr + "_chf"] = nformat(context[abr + "_chf"])
                context[abr + "t"] = nformat(context[abr + "t"], 0)
                if abr == "hfv":
                    context[abr] = nformat(context[abr], 0)
                else:
                    context[abr] = nformat(context[abr], 1)
                context[abr + "_eh"] = nformat(context[abr + "_eh"])

            file_prefix = "%s/bills/graphs/%s_object_%s" % (nk.output_dir, contract_str, o_id)

            if obj["unit"]["section"] == "Wohnen":
                graph_data = {
                    "Heizung": {
                        "total_sect": obj["costs"]["Fernwaerme_Fussboden_Verbrauch"][
                            "total_weight_sect"
                        ]
                        / nk.totals["area"][obj["unit"]["section"]]
                        * 100,
                        "unit": obj["costs"]["Fernwaerme_Fussboden_Verbrauch"]["weight"]
                        / obj["unit"]["area"]
                        * 100,
                    },
                    "Strom": {
                        "total_sect": obj["strom_building"]["total_sect"]["kwh"]
                        / nk.totals["area"][obj["unit"]["section"]]
                        * 100,
                        "unit": obj["strom"]["total"]["kwh"] / obj["unit"]["area"] * 100,
                    },
                    "Warmwasser": {
                        "total_sect": obj["costs"]["Fernwaerme_Warmwasser_Verbrauch"][
                            "total_weight_sect"
                        ]
                        / nk.totals["area"][obj["unit"]["section"]]
                        * 100,
                        "unit": obj["costs"]["Fernwaerme_Warmwasser_Verbrauch"]["weight"]
                        / obj["unit"]["area"]
                        * 100,
                    },
                }
                create_energy_consumption_graph(
                    graph_data, f"{file_prefix}_energy_graph.pdf", context
                )

            ## Create timeseries if we have previous data
            if "Vorperiode:Bezeichnung" in nk.config:
                create_timeseries(c_id, o_id, obj, context, file_prefix)

            if os.path.isfile(f"{file_prefix}_energy_timeseries.pdf") or os.path.isfile(
                f"{file_prefix}_energy_graph.pdf"
            ):
                context["has_graph"] = True
                obj["has_graph"] = True

            tmp_filename = fill_template_pod(
                nk.config["Vorlage:Abrechnung"], context, output_format="odt"
            )
            filename = "%s/bills/parts/%s_object_%s.odt" % (nk.output_dir, contract_str, o_id)
            os.rename(tmp_filename, filename)
            nk.log.append("Created %s" % filename)
            objects.append(o_id)

            context["bill_lines"].append(
                {
                    "date": billing_date,
                    "text": "Nebenkosten %s" % obj["unit"]["label"],
                    "total": context["s_chf"],
                }
            )
            context["total_amount"] += obj["amount_sum"]

        ## Get main bill from server, which also does the accounting
        context["obj_info_str"] = get_object_list_string(objects)
        if int(c_id) < 1:
            context["obj_info_str"] = "%s_%s" % (
                nk.virtual_contracts[c_id],
                context["obj_info_str"],
            )
        context["comment"] = "NK %s-%s %s" % (
            nk.dates[nk.period_start_index]["start"].strftime("%d.%m.%Y"),
            nk.dates[-1]["end"].strftime("%d.%m.%Y"),
            get_object_list_string(objects, delimiter="/"),
        )
        # nk.log.append(context['bill_lines'])
        # nk.log.append(context['total_amount'])
        context["betreff"] = "Nebenkostenabrechnung %s – %s" % (
            nk.dates[nk.period_start_index]["start"].strftime("%d.%m.%Y"),
            nk.dates[-1]["end"].strftime("%d.%m.%Y"),
        )
        if context["total_akonto"]:
            context["bill_lines"].append(
                {
                    "date": billing_date,
                    "text": "Abzüglich Akontozahlungen",
                    "total": nformat(context["total_akonto"] * -1),
                }
            )
            context["total_amount"] -= context["total_akonto"]

        if regenerate_invoice_id:
            context["regenerate_invoice_id"] = regenerate_invoice_id

        context["total_amount"] = round(context["total_amount"], 2)
        qr_pdf = get_qrbill(context)
        if qr_pdf:
            qr_pdf_filename = "%s/bills/parts/%s_QR-Rechnung.pdf" % (nk.output_dir, contract_str)
            nk.log.append("Did accounting on server and got QR-Bill: %s" % qr_pdf_filename)
            with open(qr_pdf_filename, "wb") as ofile:
                ofile.write(qr_pdf)
        else:
            nk.log.append("ERROR: Could not get qrbill!")
            raise RuntimeError(
                "Konnte QR-Rechnung/Buchungen nicht erzeugen. Ist Buchhaltung gesperrt?\n\n"
                f"{nk.get_log_tail(5)}"
            )

        context["akonto_threshold"] = (
            10  ## Prozent ab wann eine Anpassung des Akontobeitrags empfohlen wird
        )
        context["get_akonto_qrbill"] = False
        if (
            context["total_amount"] > 0
            and context["total_akonto"] > 0
            and context["total_amount"] / context["total_akonto"]
            > context["akonto_threshold"] / 100
        ):
            ## Empfehlung zur Anpassung des Akontos
            context["get_akonto_qrbill"] = True
            context["akonto_change"] = nformat(
                context["total_amount"] / sum(nk.monthly_weights["default"]), 0
            )
            context["akonto_change_sum"] = nformat(
                round(context["total_amount"] / sum(nk.monthly_weights["default"])) * 6, 0
            )

            tmp_filename2 = fill_template_pod(
                nk.config["Vorlage:EmpfehlungAkonto"], context, output_format="odt"
            )
            filename2 = "%s/bills/parts/%s_EmpfehlungAkonto.odt" % (nk.output_dir, contract_str)
            os.rename(tmp_filename2, filename2)
            nk.log.append("Created %s" % filename2)
            akonto_pdf_filename = odt2pdf(filename2)

            qr_pdf_akonto = get_qrbill(context)
            if not qr_pdf_akonto:
                nk.log.append("ERROR: Could not get akonto-qrbill!")
                raise RuntimeError("Could not get akonto-qrbill")
            qr_pdf_filename2 = "%s/bills/parts/%s_QR-Zusatzzahlung.pdf" % (
                nk.output_dir,
                contract_str,
            )
            nk.log.append("QR-Zusatzzahlung: %s" % qr_pdf_filename2)
            with open(qr_pdf_filename2, "wb") as ofile:
                ofile.write(qr_pdf_akonto)

        ## Put everything together.
        # 1. Bill with QR-Code
        # 2. Detail pages per object, including graph
        # 3. Additional payment info (if applicable)

        pdfgen = PdfGenerator()
        pdfgen.append_pdf_file(qr_pdf_filename)

        for o_id in objects:
            if nk.contracts[c_id]["objects"][o_id]["has_graph"]:
                image_pdf_files = [
                    "%s/bills/graphs/%s_object_%s_energy_timeseries.pdf"
                    % (nk.output_dir, contract_str, o_id),
                    "%s/bills/graphs/%s_object_%s_energy_timeseries_building.pdf"
                    % (nk.output_dir, contract_str, o_id),
                    "%s/bills/graphs/%s_object_%s_energy_graph.pdf"
                    % (nk.output_dir, contract_str, o_id),
                ]
            else:
                image_pdf_files = []
            object_filename = "%s/bills/parts/%s_object_%s.odt" % (
                nk.output_dir,
                contract_str,
                o_id,
            )
            pdfgen.append_pdf_file(
                odt2pdf(object_filename),
                merge_pdfs_on_last_page=image_pdf_files,
                transform={"tx": 60, "ty": 560, "dy": -250, "scale": 0.7},
            )

        if context["get_akonto_qrbill"]:
            pdfgen.append_pdf_file(akonto_pdf_filename, qr_pdf_filename2)

        filename = f"Nebenkosten-{context['obj_info_str']}-{contract_str}.pdf"
        if nk.dry_run:
            regeneration_data = None
        else:
            regeneration_data = {
                "type": "nk_bills",
                "contract_id": c_id,
                "object_ids": objects,
                "invoice_id": regenerate_invoice_id,
            }
        final_output_pdf = nk.get_output_filename(
            f"bills/{filename}", filename, "Abrechnungen", regeneration_data=regeneration_data
        )
        pdfgen.write_file(final_output_pdf)
        nk.log.append("OUTPUT is in %s" % final_output_pdf)


def get_object_list_string(objects, max_itemcount=8, delimiter="_"):
    count = len(objects)
    if count > max_itemcount:
        return delimiter.join(objects[0:max_itemcount]) + f"_und_{count - max_itemcount}_Weitere"
    else:
        return delimiter.join(objects)


def create_timeseries(c_id, o_id, obj, context, file_prefix):
    prev_key = nk.config["Vorperiode:Bezeichnung"]
    has_prev_contract = c_id in nk.previous_data[prev_key]["active_contracts"]
    if has_prev_contract:
        has_prev_contract_obj = o_id in nk.previous_data[prev_key]["contracts"][c_id]["objects"]
    else:
        has_prev_contract_obj = False
    if has_prev_contract_obj:
        # data_amount_prev = nk.previous_data[prev_key]['data_amount']
        obj_prev = nk.previous_data[prev_key]["contracts"][c_id]["objects"][o_id]

        ## Timeseries for unit
        graph_data = {
            "Strom": {
                "prev": obj_prev["strom"]["total"]["kwh"],
                "curr": obj["strom"]["total"]["kwh"],
            },
            "Warmwasser": {
                "prev": obj_prev["costs"]["Fernwaerme_Warmwasser_Verbrauch"]["weight"],
                "curr": obj["costs"]["Fernwaerme_Warmwasser_Verbrauch"]["weight"],
            },
            "months_prev": len(obj_prev["unit"]["dates"]),
            "months": len(obj["unit"]["dates"]),
        }
        if obj["unit"]["section"] == "Wohnen":
            ## Fussbodenheizung
            prev = sum_if_list(obj_prev["costs"]["Fernwaerme_Fussboden_Verbrauch"]["weight"])
            graph_data["Heizung"] = {
                "prev": sum_if_list(prev),
                "curr": sum_if_list(obj["costs"]["Fernwaerme_Fussboden_Verbrauch"]["weight"]),
            }
        context["graph_label_str"] = context["Euer"]
        context["graph_title"] = "Entwicklung Energieverbrauch Mieteinheit"
        create_energy_timeseries_graph(graph_data, f"{file_prefix}_energy_timeseries.pdf", context)

        ## Timeseries for building
        graph_data = {
            "Strom": {
                "prev": obj_prev["strom_building"]["total"]["kwh"],
                "curr": obj["strom_building"]["total"]["kwh"],
            },
            "Warmwasser": {
                "prev": obj_prev["costs"]["Fernwaerme_Warmwasser_Verbrauch"]["total_weight"],
                "curr": obj["costs"]["Fernwaerme_Warmwasser_Verbrauch"]["total_weight"],
            },
            "months_prev": len(obj_prev["unit"]["dates"]),
            "months": len(obj["unit"]["dates"]),
        }
        extra_text_append = ""
        if obj["unit"]["section"] == "Wohnen":
            prev = (
                sum_if_list(obj_prev["costs"]["Fernwaerme_Fussboden_Verbrauch"]["total_weight"]),
            )
            graph_data["Heizung"] = {
                "prev": sum_if_list(prev),
                "curr": sum_if_list(
                    obj["costs"]["Fernwaerme_Fussboden_Verbrauch"]["total_weight"]
                ),
            }
        context["graph_label_str"] = "Ganzes Haus"
        context["graph_title"] = "Entwicklung Energieverbrauch ganzes Haus"
        create_energy_timeseries_graph(
            graph_data,
            f"{file_prefix}_energy_timeseries_building.pdf",
            context,
            extra_text=f"* Nur Fussbodenheizung (Wohnungen){extra_text_append}",
        )
    else:
        nk.log.append(
            f"NO data history found => NOT creating timeseries! (c_id={c_id}, o_id={o_id}, has_prev_contract={has_prev_contract}, has_prev_contract_obj={has_prev_contract_obj}, prev_key={prev_key})"
        )


def get_qrbill(context):
    headers = {"Authorization": "Token " + API_TOKEN}
    request_data = context
    if not nk.dry_run:
        request_data["dry_run"] = False
    response = requests.post(BASE_URI + "/geno/qrbill/", json=request_data, headers=headers)
    if response.status_code != 200:  # not response.ok:
        nk.log.append(
            "ERROR: qrbill API returned: %s %s / %s"
            % (response.status_code, response.reason, response.text)
        )
        return None
    # nk.log.append('Got response: %s' % response.headers)
    if response.headers["Content-Type"] == "application/pdf":
        return response.getvalue()
    else:
        nk.log.append("ERROR: qrbill API did not return a application/pdf data.")
        nk.log.append(response.headers)
        return None


def create_energy_consumption_graph(data, output_filename, context):
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
                "%s kWh<br>%s%%" % (nformat(data["Heizung"]["unit"], 0), diff_percent_heizung_str),
                "%s m³<br>%s%%" % (nformat(data["Warmwasser"]["unit"], 0), diff_percent_ww_str),
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


def create_energy_timeseries_graph(data, output_filename, context, extra_text=None):
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
        text.append("%s kWh<br>%s%%" % (nformat(data["Strom"]["curr"], 0), diff_percent_strom_str))

    if "Vorperiode:Bezeichnung" in nk.config:
        name_prev_txt = "Periode " + nk.config["Vorperiode:Bezeichnung"]
        if "months_prev" in data:
            name_prev_txt = "%s (%s Mte.)" % (name_prev_txt, data["months_prev"])
    name_txt = f"Periode {nk.period_name}"
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


## TODO: Make this a class-based report generator
class ReportGenerator:
    default_config = {}

    def __init__(self, report, *args, **kwargs):
        self.config = copy.deepcopy(self.default_config)
        self.config.update(report.get_report_config())

        self._warnings = {}

    def add_warning(self, text, obj):
        if text in self._warnings:
            if obj not in self._warnings[text]:
                self._warnings[text].append(obj)
        else:
            self._warnings[text] = [obj]

    def get_warnings(self, space_lines_longer_than=250):
        lines = []
        for warning, objects in self._warnings.items():
            line = f"{warning}: {', '.join(objects)}"
            if space_lines_longer_than and len(line) > space_lines_longer_than:
                lines.extend(["", line, ""])
            else:
                lines.append(line)
        return lines


class Nebenkosten:
    default_costs = [
        {"name": "Hauswartung_ServiceHeizungLüftung"},
        {"name": "Betriebskosten_Gemeinschaft"},
        {
            "name": "Reinigung",
            "section_weights": "reinigung",
        },
        {
            "name": "Winterdienst",
        },
        {"name": "Umgebung_Siedlung"},
        {
            "name": "Wasser_Abwasser_Grundkosten",
            "category": "waerme_wasser_grund",
            "amount_factor": 0.3,
        },
        {
            "name": "Wasser_Abwasser_Verbrauch",
            "category": "waerme_wasser_verbrauch",
            "amount_factor": 0.7,
            "object_weights": "messung_wasser",
        },
        {"name": "Kehrichtgebuehren"},
        {
            "name": "Lift",
        },
        {
            "name": "Fernwaerme_Fussboden_Grundkosten",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Fussboden",  ## Will be imported
            "amount_factor": 0.3,  ## 30% Grundkosten gemäss Modell Verbrauchsabh. NK-Abrechnung
            "section_weights": "nur_wohnen",
            "object_weights": "volume",  #'area',
        },
        {
            "name": "Fernwaerme_Fussboden_Verbrauch",
            "category": "waerme_wasser_verbrauch",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Fussboden",  ## Will be imported
            "amount_factor": 0.7,
            "section_weights": "nur_wohnen",
            "object_weights": "messung_heizung",
        },
        {
            "name": "Fernwaerme_Radiatoren",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Radiatoren",  ## Will be imported
            "section_weights": "radiatoren",
            "object_weights": "volume",
        },
        {
            "name": "Fernwaerme_Lueftung",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Lueftung",  ## Will be imported
            "section_weights": "lueftung",  #'default',
            "object_weights": "volume",  #'area',
        },
        {
            "name": "Fernwaerme_Warmwasser_Grundkosten",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Warmwasser",  ## Will be imported
            "amount_factor": 0.3,  ## 30% Grundkosten gemäss Modell Verbrauchsabh. NK-Abrechnung
            "object_weights": "area_warmwasser",
        },
        {
            "name": "Fernwaerme_Warmwasser_Verbrauch",
            "category": "waerme_wasser_verbrauch",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Warmwasser",  ## Will be imported
            "amount_factor": 0.7,  ## 70% Verbrauchsabhängige Kosten gemäss Modell Verbrauchsabh. NK-Abrechnung
            "object_weights": "messung_warmwasser",
        },
        {
            "name": "Strom_Total",
            "category": "strom",
            "time_period": "monthly",
            "amount_from_objects": "chf_total",
            "section_weights": None,
            "object_weights": None,
        },
        {"name": "Serviceabo Energiemessung"},
        {
            "name": "Internet/WLAN",
            "category": "internet",
            "time_period": "monthly",
            "amount_from_objects": "chf_internet",
            "section_weights": None,
            "object_weights": None,
        },
        ## Anteile an "Allgemein" (special object 0000)
        {
            "name": "Anteil_Allgemein_Warmwasser_Verbrauch",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_meta": "Fernwaerme_Warmwasser_Verbrauch",  ## Will be imported
            "section_weights": "wasser_allgemein",
        },
        {
            "name": "Anteil_Allgemein_Wasser_Abwasser_Verbrauch",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_meta": "Wasser_Abwasser_Verbrauch",  ## Will be imported
            "section_weights": "wasser_allgemein",
        },
        {
            "name": "Anteil_Allgemein_Strom",
            "category": "strom_allgemein",
            "time_period": "monthly",
            "amount_meta": "Strom_Total",  ## Will be imported
        },
    ]

    # def as_list(self):
    #    return self.default_costs


class NebenkostenReportGenerator(ReportGenerator):
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
        self.period_start_index = 0
        if self.start_month == 1:
            self.period_name = str(self.start_year)
        else:
            self.period_name = f"{self.start_year}/{self.start_year + 1}"
        self.dry_run = dry_run
        self.report = report

        ## TODO: Move this to Nebenkosten class
        self.costs = copy.deepcopy(Nebenkosten.default_costs)
        self.cost_indices = {}

        self.objects = [
            {
                "name": "0000",
                "section": "Allgemein",
                "area": 0,
                "volume": 0,
                "min_occupancy": 0,
                "rooms": 0,
                "allgemein": False,
                "akonto_obj": 0,
                "nk_pauschal_obj": 0,
                "strom_pauschal_obj": 0,
                "rent_net": 0,
                "costs": {},
            },
            {
                "name": "9998",
                "section": "Lager",
                "area": 0,
                "volume": 0,
                "min_occupancy": 0,
                "rooms": 0,
                "allgemein": False,
                "akonto_obj": 0,
                "nk_pauschal_obj": 0,
                "strom_pauschal_obj": 0,
                "rent_net": 0,
                "costs": {},
            },
            {
                "name": "9999",
                "section": "Lager",
                "area": 0,
                "volume": 0,
                "min_occupancy": 0,
                "rooms": 0,
                "allgemein": False,
                "akonto_obj": 0,
                "nk_pauschal_obj": 0,
                "strom_pauschal_obj": 0,
                "rent_net": 0,
                "costs": {},
            },
        ]
        self.object_indices = {}

        self.contracts = {}
        self.active_contracts = []

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

        self.sections = ["Allgemein", "Wohnen", "Gewerbe", "Lager"]

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
        self.fill_dates()

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
        temp_out_file = f"%s/{filename}" % (self.output_dir)
        self._output_files.append(
            {
                "temp_file": temp_out_file,
                "name": name,
                "group": group,
                "regeneration_data": regeneration_data,
            }
        )
        return temp_out_file

    def get_group_name(self, group):
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

    def fill_dates(self):
        self.dates = []
        for m in range(12):
            month = self.start_month + m
            if month > 12:
                year = self.start_year + 1
                month -= 12
            else:
                year = self.start_year
            start_date = datetime(year, month, 1)

            next_month = month + 1
            if next_month > 12:
                next_month_year = year + 1
                next_month -= 12
            else:
                next_month_year = year
            end_date = datetime(next_month_year, next_month, 1) + timedelta(days=-1)

            self.dates.append({"start": start_date, "end": end_date})

    # def get_costs(self):
    #    return self._costs.as_list()

    def load_saved_data(self):
        filename = f"{self.root}/Rohdaten.json"
        with open(filename) as f:
            data = json.load(f, cls=JSONDecoderDatetime)
        for dataset in data:
            setattr(self, dataset, data[dataset])
        if "cost_indices" not in data:
            for i in range(len(nk.costs)):
                self.cost_indices[nk.costs[i]["name"]] = i
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

    def get_period_string(self):
        return "%s-%s" % (
            self.dates[self.period_start_index]["start"].strftime("%d.%m.%Y"),
            self.dates[-1]["end"].strftime("%d.%m.%Y"),
        )

    def get_log_tail(self, lines=5):
        log = f"== Letzte {lines} Zeilen des Logs: ==\n"
        log += "\n".join(nk.log[-lines:])
        return log


def main(report, dry_run=True, output_root=settings.SMEDIA_ROOT):
    global nk
    nk = NebenkostenReportGenerator(report, dry_run, output_root)

    nk.load_previous_data()
    import_from_api()

    ## Save object indices
    for i in range(len(nk.objects)):
        nk.object_indices[nk.objects[i]["name"]] = i

    import_amount_data()
    import_messung_data()

    add_calculated_weights()
    map_messung_to_objects()
    # nk.log.append(nk.object_messung['_allgemein'])

    stromrechnung()
    internetrechnung()

    calc_totals()
    for cost in nk.costs:
        if "amount_from_objects" in cost:
            ## Amount split is already there, just aggregate totals
            aggregate_cost_objects(cost["amount_from_objects"], cost)
        else:
            ## Split costs
            amount_monthly = calc_monthly_amounts(cost)
            # nk.log.append('%s: %s total=%s' % (cost['name'], amount_monthly, sum(amount_monthly)))
            split_cost_objects(amount_monthly, cost)

    add_admin_fee()

    for i in range(len(nk.costs)):
        nk.cost_indices[nk.costs[i]["name"]] = i

    if nk.output_object_data:
        export_csv()
    if nk.config["Ausgabe:Plots"]:
        plots()

    ## Assign costs to contracts based on start and end date of contract
    assign_to_contracts()

    if nk.config["Ausgabe:QR-Rechnungen"]:
        create_bills()

    ## Save data
    if nk.save_json_data:
        out_file = nk.get_output_filename("Rohdaten.json", "NK-Abrechnung Rohdaten", "Rohdaten")
        nk.log.append("Saving data to %s" % out_file)
        with open(out_file, "w") as f:
            json.dump(
                {
                    "start_month": nk.start_month,
                    "start_year": nk.start_year,
                    "admin_fee_factor": nk.admin_fee_factor,
                    "objects": nk.objects,
                    "costs": nk.costs,
                    "cost_indices": nk.cost_indices,
                    "monthly_weights": nk.monthly_weights,
                    "dates": nk.dates,
                    "sections": nk.sections,
                    "section_weights": nk.section_weights,
                    "korrektur_strom": nk.config["Strom:Korrekturen"],
                    "object_indices": nk.object_indices,
                    "object_messung": nk.object_messung,
                    "object_weights": nk.object_weights,
                    "totals": nk.totals,
                    "strom_total": nk.strom_total,
                    "categories": nk.categories,
                    "data_amount": nk.data_amount,
                    "contracts": nk.contracts,
                    "active_contracts": nk.active_contracts,
                    "virtual_contracts": nk.virtual_contracts,
                },
                f,
                sort_keys=True,
                cls=JSONEncoderDatetime,
            )

    nk.log.append("Done.")
    nk.text_output("Log", "Rohdaten", "\n".join(nk.log))

    nk.add_output_to_report()

    nk.delete_temp_files()

    warnings = nk.get_warnings()
    if warnings:
        return "Nebenkostenabrechung mit WARNUNGEN erstellt:\n\n" + "\n".join(warnings)
    else:
        return "Nebenkostenabrechnung erstellt"


def regenerate_bill(report, contract_id, dry_run=False, output_root=settings.SMEDIA_ROOT):
    global nk
    nk = NebenkostenReportGenerator(report, dry_run, output_root)
    nk.load_previous_data()
    nk.load_saved_data()
    nk.active_contracts = [
        str(contract_id),
    ]

    invoice_id = None
    if int(contract_id) >= 0:
        ## Find invoice id
        invoice_category = InvoiceCategory.objects.get(reference_id=12)  # Nebenkostenabrechnung
        invoice_comment = "NK %s" % (nk.get_period_string())
        for invoice in (
            Invoice.objects.filter(contract__id=contract_id)
            .filter(invoice_type="Invoice")
            .filter(invoice_category=invoice_category)
            .filter(active=True)
            .order_by("-date")
        ):
            if invoice.comment.startswith(invoice_comment):
                invoice_id = invoice.id
                break
        if not invoice_id:
            nk.log.append(f"Could not find corresponding invoice for contract {contract_id}!")
    if invoice_id or int(contract_id) < 0:
        create_bills(invoice_id)
        nk.update_report_output()
    nk.delete_temp_files()
    nk.log.append(f"Bill regenerated {contract_id}/{invoice_id}")
    print("\n".join(nk.log))
    return "OK"
