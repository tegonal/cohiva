import builtins
import contextlib
import csv
import datetime
import io
import re
import zipfile

from django.db import transaction
from django.db.models import Q
from openpyxl import load_workbook

## Installed from custom (modified) python-sepa subdirectory
from sepa import parser as sepa_parser

from .models import (
    Address,
    Child,
    Contract,
    Member,
    MemberAttribute,
    MemberAttributeType,
    RentalUnit,
)
from .sepa_reader import SepaReaderException, read_camt
from .utils import decode_from_iso8859

# prefix for eMonitor entries
EMONITOR_PREFIX = "eMon: "


def import_codes_from_file(empty_tables_first=False):
    response = []

    try:
        atype = MemberAttributeType.objects.get(name="Ausschreibung Code")
    except MemberAttributeType.DoesNotExist:
        response.append({"info": "ERROR: Mitglieder Attribut Typ nicht gefunden!"})
        return response

    if empty_tables_first:
        MemberAttribute.objects.filter(attribute_type=atype).delete()
        response.append({"info": "Deleting all codes from MemberAttribute!"})

    ## Load existing codes
    existing_codes = {}
    members_with_codes = []
    for c in MemberAttribute.objects.filter(attribute_type=atype):
        existing_codes[c.value] = c.member
        members_with_codes.append(c.member)

    free_codes = []
    found_codes = []
    try:
        with open("/tmp/Zugangscodes.csv", "rb") as csvfile:
            reader = csv.reader(csvfile, delimiter=b",", quotechar=b'"')
            header = []
            column_code = None
            column_status = None
            count = 0
            for row in reader:
                for i, val in enumerate(row):
                    row[i] = str(val.strip(), "utf-8")
                if count == 0:
                    header = row
                    for i, val in enumerate(header):
                        if val == "Zugangscode":
                            column_code = i
                        elif val == "Status":
                            column_status = i
                else:
                    if row[column_status] == "automatisch vergeben" and row[
                        column_code
                    ].startswith("WBM"):
                        if row[column_code] in existing_codes:
                            found_codes.append(row[column_code])
                        else:
                            free_codes.append(row[column_code])
                count += 1
    except OSError as e:
        response.append({"info": "ERROR: Konnte CSV Datei nicht lesen: %s" % e})
        return response

    today = datetime.datetime.today()
    missing_codes = []
    new_code_count = 0
    with transaction.atomic():
        for m in Member.objects.filter(Q(date_leave=None) | Q(date_leave__gt=today)):
            if m not in members_with_codes:
                if free_codes:
                    code = free_codes.pop()
                    new = MemberAttribute(member=m, attribute_type=atype, date=today, value=code)
                    new.save()
                    response.append({"info": "Code %s neu vergeben an %s." % (code, m)})
                    new_code_count += 1
                else:
                    missing_codes.append("%s" % m)

    if new_code_count:
        response.append({"info": "Es wurden %d Codes neu vergeben." % new_code_count})

    if missing_codes:
        response.append(
            {
                "info": "WARNUNG: Es fehlen %d Codes für folgende Mitglieder:"
                % len(missing_codes),
                "objects": missing_codes,
            }
        )
    else:
        response.append({"info": "Es hat noch %d freie Codes übrig." % len(free_codes)})

    if found_codes:
        response.append(
            {
                "info": "%d codes waren bereits an Mitglieder vergeben:" % len(found_codes),
                "objects": found_codes,
            }
        )

    return response


def import_rentalunits_from_file(empty_tables_first=False):
    response = []

    if empty_tables_first:
        RentalUnit.objects.all().delete()
        response.append({"info": "Deleting all RentalUnit objects!"})

    count = 0
    header = []
    with open("/tmp/export_objekte.csv", "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=b",", quotechar=b'"')
        for row in reader:
            if count == 0:
                header = row
            else:
                new_unit = RentalUnit()
                new_unit.building = "Holligerhof 8"
                fields = []
                rent_net = None
                for i, val in enumerate(row):
                    val = str(val.strip(), "utf-8")
                    # "Details","Bezeichnung","Typ","Bruttomiete","Nettomiete","Zimmer","Fläche","Loggiafläche","Balkonfläche","Ausschreibungstext","Stockwerk","Mindestbelegung total","Mietbedingungen","Anteilskapital","Erstellungsdatum"
                    if header[i] == "Bezeichnung":
                        new_unit.name = val
                    elif header[i] == "Typ":
                        new_unit.rental_type = val
                    elif header[i] == "Bruttomiete":
                        new_unit.rent_total = float(val)
                    elif header[i] == "Nettomiete":
                        rent_net = float(val)
                    elif header[i] == "Zimmer":
                        new_unit.rooms = float(val)
                    elif str(header[i], "utf-8") == "Fläche":
                        new_unit.area = float(val)
                    elif str(header[i], "utf-8") == "Loggiafläche":
                        if val == "":
                            new_unit.area_add = None
                        else:
                            new_unit.area_add = float(val)
                    elif str(header[i], "utf-8") == "Balkonfläche":
                        if val == "":
                            new_unit.area_balcony = None
                        else:
                            new_unit.area_balcony = float(val)
                    elif header[i] == "Ausschreibungstext":
                        new_unit.height = val
                    elif header[i] == "Stockwerk":
                        new_unit.floor = val
                    elif header[i] == "Mietbedingungen":
                        new_unit.min_occupancy = float(val)
                    elif header[i] == "Anteilskapital":
                        if val == "":
                            new_unit.share = None
                        else:
                            new_unit.share = float(val)
                    elif header[i] == "Erstellungsdatum":
                        new_unit.comment = "Von eMonitor %s" % (val)
                if rent_net and new_unit.rent_total:
                    new_unit.nk = new_unit.rent_total - rent_net

                new_unit.save()
                fields.append("Added new RentalUnit %s" % (new_unit.name))

                # fields = ( '%s: %s' % (header[i],val) for i,val in enumerate(row) )
                response.append({"info": "Importing unit %d" % count, "objects": fields})
            count += 1
    return response


def import_emonitor_children_from_file(empty_tables_first=False):
    response = []

    # if empty_tables_first:
    #    RentalUnit.objects.all().delete()
    #    response.append({'info': 'Deleting all RentalUnit objects!'})

    count = 0
    header = []
    with open("/tmp/export_kinder.csv", encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in reader:
            if count == 0:
                header = row
            else:
                new_adr = Address()
                new_child = Child()
                fields = []
                contract_id = None
                for i, val in enumerate(row):
                    val = val.strip()
                    # Bewerbung,ID,Vorname,Nachname,Anwesenheit Kinder,Eltern(teil) des Kindes,Geburtsdatum,Erstellungsdatum
                    # if str(header[i], 'utf-8') == "Bewerbung":
                    if header[i] == "Bewerbung":
                        contract_id = int(val)
                    elif header[i] == "ID":
                        new_child.import_id = EMONITOR_PREFIX + val
                    elif header[i] == "Vorname":
                        new_adr.first_name = val
                    elif header[i] == "Nachname":
                        new_adr.name = val
                    elif header[i] == "Geburtsdatum":
                        if val:
                            # new_adr.date_birth = datetime.datetime.strptime(val, '%Y-%m-%d').date()
                            new_adr.date_birth = datetime.datetime.strptime(val, "%d.%m.%y").date()
                    elif header[i] == "Anwesenheit Kinder":
                        new_child.presence = float(val)
                    elif header[i] == "Eltern(teil) des Kindes":
                        new_child.parents = val
                    elif header[i] == "Erstellungsdatum":
                        new_adr.comment = "Von eMonitor %s" % (val)
                        new_child.comment = "Von eMonitor %s" % (val)

                contract = Contract.objects.get(import_id=contract_id)

                if not new_adr.name and not new_adr.first_name:
                    fields.append("Ignoring empty name!")
                else:
                    new_adr.save()
                    new_child.name = new_adr
                    new_child.save()
                    fields.append("Added Child %s" % new_child)

                    contract.children.add(new_child)
                    contract.save()
                    fields.append("Added Child to contract %s" % (contract))

                # fields = ( '%s: %s' % (header[i],val) for i,val in enumerate(row) )
                response.append({"info": "Importing child %d" % count, "objects": fields})
            count += 1
    return response


def import_emonitor_addresses_from_file(empty_tables_first=False):
    response = []

    # if empty_tables_first:
    #    RentalUnit.objects.all().delete()
    #    response.append({'info': 'Deleting all RentalUnit objects!'})

    p_tel_swiss = re.compile(
        r"^\s*(?:0041 ?|\+?\+?41 ?|0|041 0)?(\d\d) ?(\d\d\d) ?(\d\d) ?(\d\d)[^0-9]*$"
    )

    count = 0
    header = []
    with open("/tmp/export_vertrag.csv", "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=b",", quotechar=b'"')
        for row in reader:
            if count == 0:
                header = row
            else:
                new_adr = Address()
                fields = []
                plz = None
                contract_id = None
                for i, val in enumerate(row):
                    val = str(val.strip(), "utf-8")
                    # Bewerbungs-ID,Erwachsener ID,Anrede,Vorname,Name,Nationalität,Aufenthaltsstatus,Zivilstand,Geburtsdatum,Beschäftigungsstatus,Beruf,Straße,PLZ,Ort,E-Mail,Telefonnummer,Arbeitgeber Telefon,Wohnung,Zusätzliche Objekte,Vertragsstatus,Anzahl Kinder
                    if str(header[i], "utf-8") == "Bewerbungs-ID":
                        contract_id = int(val)
                    elif str(header[i], "utf-8") == "Erwachsener ID":
                        new_adr.import_id = EMONITOR_PREFIX + val
                    elif str(header[i], "utf-8") == "Anrede":
                        new_adr.title = val
                    elif str(header[i], "utf-8") == "Vorname":
                        new_adr.first_name = val
                    elif str(header[i], "utf-8") == "Name":
                        new_adr.name = val
                    elif str(header[i], "utf-8") == "Geburtsdatum":
                        if val:
                            new_adr.date_birth = datetime.datetime.strptime(val, "%Y-%m-%d").date()
                    elif str(header[i], "utf-8") == "Straße":
                        ## TODO: Split Nr?
                        new_adr.street_name = val
                    elif str(header[i], "utf-8") == "PLZ":
                        new_adr.city_zipcode = val
                    elif str(header[i], "utf-8") == "Ort":
                        new_adr.city_name = val
                    elif str(header[i], "utf-8") == "E-Mail":
                        new_adr.email = val
                    elif str(header[i], "utf-8") == "Telefonnummer":
                        if val == "":
                            continue
                        if len(val) > 20:
                            parts = val.split("  ")
                            val = parts[0]
                        m = p_tel_swiss.match(val)
                        if m:
                            new_adr.telephone = "0%s %s %s %s" % (
                                m.group(1),
                                m.group(2),
                                m.group(3),
                                m.group(4),
                            )
                        else:
                            raise Exception('Couldnt parse telephone: "%s"' % val)
                if plz:
                    new_adr.city_name = "%s %s" % (plz, new_adr.city)

                contract = Contract.objects.get(import_id=contract_id)

                if not new_adr.name and not new_adr.first_name:
                    fields.append("Ignoring empty name!")
                else:
                    ## Try to find match
                    save = False
                    existing = Address.objects.filter(
                        name=new_adr.name, first_name=new_adr.first_name, organization=""
                    )
                    if not existing:
                        ## Try email+anrede
                        existing = Address.objects.filter(email=new_adr.email, title=new_adr.title)
                        fields.append(
                            "WARNING: Searching existing Address by email+title %s+%s"
                            % (new_adr.email, new_adr.title)
                        )
                    if not existing:
                        ## Try first name and tel
                        existing = Address.objects.filter(
                            first_name=new_adr.first_name, telephone=new_adr.telephone
                        )
                        fields.append(
                            "WARNING: Searching existing Address by first_name+telephone %s+%s"
                            % (new_adr.first_name, new_adr.telephone)
                        )
                    if not existing:
                        ## Try last name and tel
                        existing = Address.objects.filter(
                            name=new_adr.name, telephone=new_adr.telephone
                        )
                        fields.append(
                            "WARNING: Searching existing Address by name+telephone %s+%s"
                            % (new_adr.name, new_adr.telephone)
                        )
                    if len(existing) > 0:
                        if len(existing) != 1:
                            raise Exception("Too many matches found")
                        fields.append(
                            "Found existing Address %s, %s" % (new_adr.name, new_adr.first_name)
                        )
                        old_adr = existing[0]
                        for a in (
                            "import_id",
                            "title",
                            "date_birth",
                            "street",
                            "city",
                            "email",
                            "telephone",
                        ):
                            att_old = getattr(old_adr, a)
                            att_new = getattr(new_adr, a)
                            if att_new and att_old != att_new:
                                if a == "import_id" and not att_old:
                                    setattr(old_adr, a, att_new)
                                    fields.append("Setting %s: %s -> %s" % (a, att_old, att_new))
                                    save = True
                                elif a == "email" and not old_adr.email2:
                                    old_adr.email2 = att_new
                                    fields.append(
                                        "Adding 2nd email address: %s + %s" % (att_old, att_new)
                                    )
                                    save = True
                                elif a == "email" and att_new == old_adr.email2:
                                    ## Match with email2 is OK
                                    continue
                                elif a == "telephone" and not old_adr.mobile:
                                    old_adr.mobile = att_new
                                    fields.append(
                                        "Adding 2nd telephone: %s + %s" % (att_old, att_new)
                                    )
                                    save = True
                                elif a == "telephone" and att_new == old_adr.mobile:
                                    ## Match with phone2 is OK
                                    continue
                                else:
                                    fields.append(
                                        "NOT MATCHING %s: %s != %s" % (a, att_old, att_new)
                                    )
                        adr = old_adr
                    else:
                        fields.append(
                            "Adding new Address %s, %s" % (new_adr.name, new_adr.first_name)
                        )
                        save = True
                        adr = new_adr
                    if save:
                        adr.save()
                    contract.contractors.add(adr)
                    contract.save()
                    fields.append("Added Address to contract %s" % (contract))

                # fields = ( '%s: %s' % (header[i],val) for i,val in enumerate(row) )
                response.append({"info": "Importing address %d" % count, "objects": fields})
            count += 1
    return response


def import_keller_from_file(empty_tables_first=False):
    response = []

    if empty_tables_first:
        RentalUnit.objects.filter(rental_type="Kellerabteil").delete()
        response.append({"info": "Deleting all RentalUnit objects with type Kellerabteil!"})

    count = 0
    header = []
    with open("/tmp/Mieterkeller_Wohnungen.csv", "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=b",", quotechar=b'"')
        for row in reader:
            if count == 0:
                header = row
            else:
                new_unit = RentalUnit()
                new_unit.building = "Holligerhof 8"
                new_unit.rent_netto = 0.0
                new_unit.floor = "Keller"
                fields = []
                linked_unit = None
                desc = None
                for i, val in enumerate(row):
                    val = str(val.strip(), "utf-8")
                    # "Raumnr.","Bezeichnung","Zugewiesene Whg.","Bodenfläche (m2)","Raumhöhe (m)"
                    if header[i] == "Raumnr.":
                        new_unit.name = val
                    elif header[i] == "Bezeichnung":
                        desc = val
                        if val.startswith("Mieterkeller"):
                            new_unit.rental_type = "Kellerabteil"
                    elif header[i] == "Zugewiesene Whg.":
                        linked_unit = val
                    elif str(header[i], "utf-8") == "Bodenfläche (m2)":
                        vals = val.split("/")
                        if val == "":
                            new_unit.area = None
                            new_unit.area_add = None
                        elif len(vals) == 1:
                            new_unit.area = float(vals[0])
                            new_unit.area_add = None
                        elif len(vals) == 2:
                            new_unit.area = float(vals[0])
                            new_unit.area_add = float(vals[1])
                        else:
                            raise ValueError("More than two area values found!")
                    elif str(header[i], "utf-8") == "Raumhöhe (m)":
                        new_unit.height = val

                if desc:
                    new_unit.note = desc
                    if linked_unit:
                        new_unit.note = "%s %s" % (new_unit.note, linked_unit)

                if new_unit.rental_type:
                    new_unit.save()
                    fields.append("Added new RentalUnit %s" % (new_unit.name))
                    if linked_unit:
                        try:
                            other_unit = RentalUnit.objects.get(name=linked_unit)
                            contracts = Contract.objects.filter(rental_units__pk=other_unit.pk)
                            if contracts.count() == 1:
                                contract = contracts.first()
                                contract.rental_units.add(new_unit)
                                contract.save()
                                fields.append("Linked to contract %s" % (contract))
                            else:
                                fields.append(
                                    "WARNING: Not linking to contract (None or too many contracts found for %s)"
                                    % (other_unit.name)
                                )
                        except RentalUnit.DoesNotExist:
                            fields.append(
                                "WARNING: Not linking to contract (linked unit %s not found)"
                                % (linked_unit)
                            )

                # fields = ( '%s: %s' % (header[i],val) for i,val in enumerate(row) )
                response.append({"info": "Importing unit %d" % count, "objects": fields})
            count += 1
    return response


def import_emonitor_contracts_from_file(empty_tables_first=False):
    response = []

    if empty_tables_first:
        Contract.objects.all().delete()
        response.append({"info": "Deleting all Contract objects!"})

    count = 0
    header = []
    with open("/tmp/export_zuweisung.csv", "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=b",", quotechar=b'"')
        for row in reader:
            if count == 0:
                header = row
            else:
                new = Contract()
                new.state = "angeboten"
                new.date = datetime.date(2021, 11, 0o1)
                fields = []
                rentals = []
                for i, val in enumerate(row):
                    val = str(val.strip(), "utf-8")
                    # "ID","Erwachsene","Kinder","Erstellungsdatum","Zuweisung Wohnung","Parkplatz gewünscht","Zuweisung Parkplatz","Zuweisung Nebenräume","Telefonnummer","Status"
                    if str(header[i], "utf-8") == "ID":
                        new.import_id = EMONITOR_PREFIX + val  ## Bewerbungs-ID
                    elif str(header[i], "utf-8") == "Kinder":
                        new.children = val
                    elif str(header[i], "utf-8") == "Zuweisung Wohnung":
                        rental_ids = val.split("\n")
                        for r in rental_ids:
                            rentals.append(
                                RentalUnit.objects.get(name=r, building="Holligerhof 8")
                            )
                    elif str(header[i], "utf-8") == "Parkplatz gewünscht":
                        if val:
                            prep = ""
                            if new.note:
                                prep = "%s / " % new.note
                            new.note = prep + "Parkplatz: %s" % (val)
                    elif str(header[i], "utf-8") == "Status":
                        if val:
                            prep = ""
                            if new.note:
                                prep = "%s / " % new.note
                            new.note = prep + "eMonitor-Status: %s" % (val)

                if new.children:
                    fields.append("Children: %s" % new.children)
                if new.note:
                    fields.append("Note: %s" % new.note)

                ## Check if we have a contract already
                try:
                    contract = Contract.objects.get(import_id=new.import_id)
                    fields.append(
                        "===> FOUND EXISTING contract with import_id ID %s"
                        % (contract.emonitor_id)
                    )
                except Contract.DoesNotExist:
                    contract = new
                    fields.append(
                        "Creating new contract with import_id ID %s" % (contract.emonitor_id)
                    )

                ## Add rental unit(s)
                if rentals:
                    contract.save()
                    for rental in rentals:
                        contract.rental_units.add(rental)
                        fields.append("Adding rental_unit %s, %s" % (rental.name, rental.building))
                    contract.save()
                else:
                    fields.append("No rental unit found. IGNORING!")

                response.append({"info": "Importing contract %d" % count, "objects": fields})
            count += 1
    return response


def parse_transaction_file_camt(xmlfile):
    xml = xmlfile.read()
    data = {"log": []}

    try:
        camt_data = sepa_parser.parse_string(None, xml)
    except Exception as e:
        return {"type": "camt", "data": data, "error": f"SEPA parser error: {e}"}
    error = None
    doctype = camt_data["document_type"]
    try:
        data = read_camt(camt_data)
    except SepaReaderException as e:
        error = "Fehler beim Lesen der %s Datei: %s" % (doctype, e)
    return {"type": doctype, "data": data, "error": error}


def process_transaction_file(uploadfile, max_filesize=50 * 1024 * 1024, allowed_ext=None):
    if allowed_ext is None:
        allowed_ext = ["zip", "xml"]
    if uploadfile.size > max_filesize:
        return {"type": None, "data": None, "error": "Datei ist zu gross!"}
    ext = uploadfile.name[-3:]
    if ext not in allowed_ext:
        return {"type": None, "data": None, "error": f"Dateityp {ext} ist nicht erlaubt!"}
    if ext == "zip":
        ## Unpack and process zip files
        ret = None
        with zipfile.ZipFile(io.BytesIO(uploadfile.read())) as thezip:
            for zipinfo in thezip.infolist():
                if (
                    zipinfo.is_dir()
                    or zipinfo.filename.startswith(".")
                    or zipinfo.filename.startswith("_")
                    or ".DS_Store" in zipinfo.filename
                ):
                    continue
                with thezip.open(zipinfo) as thefile:
                    filedata = parse_transaction_file_camt(thefile)
                    if filedata["error"]:
                        return {"type": None, "data": None, "error": filedata["error"]}
                    filedata["data"]["log"].append(
                        {
                            "info": f"Imported {filedata['type']} file {zipinfo.filename} from ZIP-File {uploadfile.name}.",
                            "objects": [],
                        }
                    )
                    if not ret:
                        ret = filedata
                    else:
                        ## Merge data from files
                        if ret["type"] != filedata["type"]:
                            return {
                                "type": None,
                                "data": None,
                                "error": f"Incompatible document types in ZIP file: {ret['type']} vs. {filedata['type']}",
                            }
                        ret["data"]["log"].extend(filedata["data"]["log"])
                        ret["data"]["transactions"].extend(filedata["data"]["transactions"])
        return ret
    if ext == "xml":
        ret = parse_transaction_file_camt(uploadfile)
        ret["data"]["log"].append(
            {"info": f"Imported {ret['type']} file {uploadfile.name}.", "objects": []}
        )
        return ret
    if ext == "csv":
        return parse_transaction_file_csv(uploadfile)
    return {"type": None, "data": None, "error": f"Dateityp {ext} ist nicht implementiert!"}


def parse_transaction_file_csv(csvfile):
    csvreader = csv.reader(decode_from_iso8859(csvfile), delimiter=";", quotechar='"')
    header = True
    filetype = None
    data = []

    patterns = []
    ## New format
    patterns.append(
        {
            "type": "Post",
            "re": re.compile(
                "^GUTSCHRIFT (?P<account>CH[A-Z0-9]{19}) ABSENDER: (?P<person>.*) MITTEILUNGEN: (?P<note>.*)"
            ),
        }
    )
    patterns.append(
        {
            "type": "Post",
            "re": re.compile("^GUTSCHRIFT (?P<account>CH[A-Z0-9]{19}) ABSENDER: (?P<person>.*)"),
        }
    )
    patterns.append(
        {
            "type": "Bank",
            "re": re.compile(
                "^GUTSCHRIFT AUFTRAGGEBER: (?P<person>.*) MITTEILUNGEN: (?P<note>.*) SPESENBETRAG"
            ),
        }
    )
    patterns.append(
        {
            "type": "Bank",
            "re": re.compile(
                "^GUTSCHRIFT AUFTRAGGEBER: (?P<person>.*) MITTEILUNGEN: (?P<note>.*) REFERENZEN:"
            ),
        }
    )
    patterns.append(
        {"type": "Bank", "re": re.compile("^GUTSCHRIFT AUFTRAGGEBER: (?P<person>.*) SPESENBETRAG")}
    )
    patterns.append(
        {"type": "Bank", "re": re.compile("^GUTSCHRIFT AUFTRAGGEBER: (?P<person>.*) REFERENZEN:")}
    )
    ## Old format(?)
    patterns.append(
        {
            "type": "Bank",
            "re": re.compile(
                "^GUTSCHRIFT VON FREMDBANK.* AUFTRAGGEBER: (?P<person>.*) MITTEILUNGEN: (?P<note>.*) REFERENZEN:"
            ),
        }
    )  # 0
    patterns.append(
        {
            "type": "Bank",
            "re": re.compile(
                "^GUTSCHRIFT VON FREMDBANK.* AUFTRAGGEBER: (?P<person>.*) REFERENZEN:"
            ),
        }
    )  # 1
    patterns.append(
        {
            "type": "Post",
            "re": re.compile(
                "^GIRO AUS KONTO (?P<account>.*) ABSENDER: (?P<person>.*) MITTEILUNGEN: (?P<note>.*)"
            ),
        }
    )  # 2
    patterns.append(
        {
            "type": "Post",
            "re": re.compile("^GIRO AUS KONTO (?P<account>.*) ABSENDER: (?P<person>.*)"),
        }
    )  # 3
    patterns.append(
        {
            "type": "Post",
            "re": re.compile(
                "^GIRO AUS KONTO POSTFINANCE MOBILE (?P<account>[A-Z0-9]*) (?P<person>.*) MITTEILUNGEN: (?P<note>.*)"
            ),
        }
    )  # 4
    patterns.append(
        {
            "type": "Post",
            "re": re.compile(
                "^GIRO AUS KONTO POSTFINANCE MOBILE (?P<account>[A-Z0-9]*) (?P<person>.*)"
            ),
        }
    )  # 5
    patterns.append(
        {
            "type": "EZS",
            "re": re.compile(
                "^EINZAHLUNGSSCHEIN/QR-ZAHLTEIL ABSENDER: (?P<person>.*) REFERENZEN:"
            ),
        }
    )  # 6
    patterns.append({"type": "EZS", "re": re.compile("^EINZAHLUNGSSCHEIN")})  # 7

    for row in csvreader:
        if header:
            if row[0:5] == [
                "Buchungsdatum",
                "Avisierungstext",
                "Gutschrift in CHF",
                "Lastschrift in CHF",
                "Valuta",
            ]:
                filetype = "Postfinance"
                header = False
        elif len(row) > 2 and len(row[0]) == 10 and len(row[1]) and len(row[2]):
            ## Normalize date format
            date_str = row[0]
            date_patterns = ["%Y-%m-%d", "%d.%m.%Y"]
            for pattern in date_patterns:
                with contextlib.suppress(builtins.BaseException):
                    date_str = datetime.date.strftime(
                        datetime.datetime.strptime(row[0], pattern), "%d.%m.%Y"
                    )
            d = {
                "date": date_str,
                "person": None,
                "note": None,
                "account": None,
                "type": None,
                "received": False,
                "amount": 0,
            }
            text = row[1].strip()
            for p in patterns:
                m = p["re"].match(text)
                if m:
                    d["type"] = p["type"]
                    # print('Match found: %s' % (text))
                    for g in list(m.groupdict().items()):
                        # print(' %s -> %s' % g)
                        d[g[0]] = g[1]
                    # print('-------------')
                    d["type"] = p["type"]
                    d["received"] = True
                    d["amount"] = float(row[2])
                    break
            if d["type"] == "EZS":
                d["note"] = "Einzahlungsschein"

            data.append(d)

    if not filetype:
        return {"type": "csv", "data": None, "error": "Dateityp unbekannt"}
    elif data:
        return {"type": "csv", "data": data, "error": None}
    else:
        return {"type": "csv", "data": None, "error": "Keine Daten gefunden"}


def import_adit_serial():
    response = []

    filename = "/tmp/ADIT Belegungsplan.xlsm"
    wb = load_workbook(filename)
    if "ADIT1000" not in wb.sheetnames:
        response.append(
            {"info": "ERROR: Sheet ADIT1000 not found! (%s)" % str(wb.sheetname), "objects": []}
        )
        return response

    ws = wb["ADIT1000"]

    col_serial1 = 6
    col_notes = 10

    row_list_start = 17
    row_list_max = 1014

    serials = {}  ## serial -> room
    rooms = {}  ## room -> serial
    count_serials = 0
    count_rooms = 0

    room_pattern = re.compile(r"^(Wohnung|Joker) (\d{3})\b")
    for row in range(row_list_start, row_list_max):
        serial1 = ws.cell(row=row, column=col_serial1).value
        notes = ws.cell(row=row, column=col_notes).value
        # print("No=%s, Name=%s, Serial=%s, Notes=%s" % (ws.cell(row=row, column=col_nr).value, ws.cell(row=row, column=col_name).value, serial1, notes))
        if not serial1:
            # print("No serial1, assuming end of list!")
            break
        ## Parse room number
        match = room_pattern.match(notes)
        if match:
            # print("/%s/%s/" % (match.group(1),match.group(2)))
            room = match.group(2)
            if serial1 in serials:
                if serials[serial1] != room:
                    response.append(
                        {
                            "info": "ERROR: Multiple rooms for serial %s! (parsed room=%s)"
                            % (serial1, room),
                            "objects": [],
                        }
                    )
                    return response
                    # raise RuntimeError("Multiple rooms for serial %s! (parsed room=%s)" % (serial1, room))
                    # return
            else:
                serials[serial1] = room
                count_serials += 1
            if room in rooms:
                if rooms[room] != serial1:
                    response.append(
                        {
                            "info": "ERROR: Multiple serials for room %s! (parsed serial1=%s)"
                            % (room, serial1),
                            "objects": [],
                        }
                    )
                    return response
                    # raise RuntimeError("Multiple serials for room %s! (parsed serial1=%s)" % (room, serial1))
                    # return
            else:
                rooms[room] = serial1
                count_rooms += 1

        else:
            response.append({"info": "ERROR: No match! notes=%s" % notes, "objects": []})
            return response
            # raise RuntimeError("No match! notes=%s" % notes)
            # return 2

    response.append(
        {"info": "Read %d serials and %d rooms." % (count_serials, count_rooms), "objects": []}
    )
    # print("Imported %d serials and %d rooms." % (count_serials, count_rooms))
    # print(serials)

    update_obj = []
    added_obj = []

    for room in rooms:
        ru = RentalUnit.objects.get(name=room)
        if ru.adit_serial:
            if str(ru.adit_serial) != str(rooms[room]):
                update_obj.append(
                    "Update serial %s: %s -> %s" % (room, ru.adit_serial, rooms[room])
                )
                ru.adit_serial = rooms[room]
                ru.save()
        else:
            added_obj.append("Add serial %s: %s" % (room, rooms[room]))
            ru.adit_serial = rooms[room]
            ru.save()

    if update_obj:
        response.append(
            {"info": "Updated %d rental units:" % len(update_obj), "objects": update_obj}
        )
    if added_obj:
        response.append(
            {"info": "Added serial to %d rental units:" % len(added_obj), "objects": added_obj}
        )

    return response
