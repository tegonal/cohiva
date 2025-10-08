import datetime
import io
from zipfile import ZipFile

from geno.models import Address, Contract
from geno.tests import data as geno_testdata


def create_nk_data(cls):
    geno_testdata.create_rentalunits(cls, 3)
    create_contracts(cls)
    create_measurement_data(cls)
    create_templates(cls)


def create_contracts(cls):
    cls.contracts = []
    cls.addresses = []

    ## Create a default contract for each rental unit
    for i, ru in enumerate(cls.rentalunits):
        address = Address.objects.create(
            name=f"Muster{i + 1}",
            first_name="Hans",
            email="hans.muster{i}@example.com",
            title="Herr",
            formal="Sie",
            street_name=cls.buildings[0].name.split(" ")[0],
            house_number=cls.buildings[0].name.split(" ")[1],
            city_zipcode="3000",
            city_name="Bern",
        )
        contract = Contract.objects.create(
            comment=f"Default contract {i + 1}",
            state="unterzeichnet",
            date=datetime.date(2001, 4, 1),
        )
        contract.rental_units.set([ru])
        contract.contractors.set([address])
        contract.save()
        cls.contracts.append(contract)
        cls.addresses.append(address)


def create_templates(cls):
    cls.filer_template_qrbill = cls.addFilerFile("report/tests/test_data/nk_template_qrbill.odt")
    cls.filer_template_akonto = cls.addFilerFile("report/tests/test_data/nk_template_akonto.odt")


def create_measurement_data(cls):
    cls.filer_measurements_building = cls.addFilerFile("report/tests/test_data/nk_messdaten.csv")

    ## Rental unit data
    fields = {
        "Strom": {
            "Gebäudeeinheit": "object",
            "Mieter Abrechnungsperiode": "time_period",
            "Strombezug Niedertarif(kWh)": lambda ru: ru.area * 2,
            "Strombezug Hochtarif EW (kWh)": lambda ru: ru.area * 6,
            "Solarstrom (kWh)": lambda ru: ru.area * 4,
            "Strombezug Niedertarif(CHF)": lambda ru: ru.area * 2 * 0.28,
            "Strombezug EW (CHF)": lambda ru: ru.area * 6 * 0.30,
        },
        "Waerme": {
            "Gebäudeeinheit": "object",
            "Mieter Abrechnungsperiode": "time_period",
            "Warmwasser Verbrauch (Kubikmeter)": lambda ru: ru.area * 0.4,
            "Wärmeverbrauch (kWh)": lambda ru: ru.area * 7,
        },
    }
    months = [
        {"month": "07", "year": "2023", "days": "31"},
        {"month": "08", "year": "2023", "days": "31"},
        {"month": "09", "year": "2023", "days": "30"},
        {"month": "10", "year": "2023", "days": "31"},
        {"month": "11", "year": "2023", "days": "30"},
        {"month": "12", "year": "2023", "days": "31"},
        {"month": "01", "year": "2024", "days": "31"},
        {"month": "02", "year": "2024", "days": "29"},
        {"month": "03", "year": "2024", "days": "31"},
        {"month": "04", "year": "2024", "days": "30"},
        {"month": "05", "year": "2024", "days": "31"},
        {"month": "06", "year": "2024", "days": "30"},
    ]
    file_like_object = io.BytesIO()
    with ZipFile(file_like_object, "w") as archive:
        for mtype in fields:
            for month in months:
                filename = f"egon_{mtype}_{month['year']}-{month['month']}.csv"
                archive.writestr(
                    filename,
                    create_monthly_measurement_data(cls, month, fields[mtype]).encode("iso8859"),
                )
    file_like_object.seek(0)
    cls.filer_measurements_units = cls.addFilerFD(file_like_object, "measurement_units.zip")


def create_monthly_measurement_data(cls, month, fields):
    lines = []
    ## Header
    cols = []
    for field in fields:
        cols.append(f'"{field}"')
    lines.append(";".join(cols))
    ## RentalUnits
    for ru in cls.rentalunits:
        cols = []
        for value in fields.values():
            if value == "object":
                cols.append(f'"{ru.name} {ru.rental_type}"')
            elif value == "time_period":
                cols.append(
                    f'"01.{month["month"]}.{month["year"]} - {month["days"]}.{month["month"]}.{month["year"]}"'
                )
            else:
                monthly_value = value(ru) / 12
                cols.append(f'"{monthly_value}"')
        lines.append(";".join(cols))
    return "\n".join(lines)
