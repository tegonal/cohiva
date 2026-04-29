import csv
import datetime
import io
import re
import zipfile
from typing import TYPE_CHECKING

from django.utils.translation import gettext as _

if TYPE_CHECKING:
    from report.nk.generator import NkReportGenerator


class NkMeasurementDataBase:
    def __init__(self, report_generator: "NkReportGenerator", measurements_config):
        self.data = {}
        self.imported_rental_unit_names = {}
        self.warnings = []

    def load(self):
        pass

    def get(self, key="verbrauch", default=None):
        return self.data.get(key, default)


class NkMeasurementDataMonthly(NkMeasurementDataBase):
    """The default time resolution is monthly data."""

    def __init__(self, report_generator: "NkReportGenerator", measurements_config):
        super().__init__(report_generator, measurements_config)
        self.num_months = report_generator.num_months
        self.dates = report_generator.dates


class NkMeasurementDataAnnual(NkMeasurementDataBase):
    """Simple annual measurement data for the whole building (one number equally distributed over the months)."""

    def __init__(self, report_generator: "NkReportGenerator", measurements_config):
        super().__init__(report_generator, measurements_config)
        self.annual_value = report_generator.config.get(measurements_config.get("value_key"))

    def load(self):
        self.data["verbrauch"] = self.annual_value


class NkMeasurementDataCSVFile(NkMeasurementDataBase):
    def __init__(self, report_generator: "NkReportGenerator", measurements_config):
        super().__init__(report_generator, measurements_config)
        self.file = report_generator.config.get(measurements_config.get("file_key"))
        self.headers = measurements_config.get("headers")

    def _read_csv_data(self, csvfile):
        dialect = csv.Sniffer().sniff("".join(csvfile.readlines(10)))
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)  # , delimiter=";", quotechar='"')
        header_map = {}
        ret = []
        skip_rows = self.get_skip_rows()
        ignore_duplicate_headers = self.get_ignore_duplicate_headers()
        for row in reader:
            if not row:
                continue
            if not header_map:
                header = row
                for field, title in self.headers.items():
                    for i, header_str in enumerate(header):
                        if header_str == title:
                            if field in header_map:
                                if title not in ignore_duplicate_headers:
                                    raise ValueError(
                                        _(
                                            "Duplicate header {title} in the measurement CSV file"
                                        ).format(title=title)
                                    )
                            header_map[field] = i
                    if field not in header_map:
                        raise ValueError(
                            _("Could not find header {title} in the measurement CSV file").format(
                                title=title
                            )
                        )
            elif row[0] in skip_rows:
                ## Skip some lines (e.g. with totals)
                continue
            else:
                data = {}
                for field in header_map:
                    data[field] = row[header_map[field]]
                if data:
                    ret.append(data)
        return ret

    @staticmethod
    def get_skip_rows() -> list[str]:
        return []

    @staticmethod
    def get_ignore_duplicate_headers() -> list[str]:
        return []


class NkMeasurementDataZippedMonthly(NkMeasurementDataCSVFile):
    def __init__(self, report_generator: "NkReportGenerator", measurements_config):
        super().__init__(report_generator, measurements_config)
        self.file_prefix = measurements_config.get("file_prefix")
        self.dates = report_generator.dates

    def load(self):
        with zipfile.ZipFile(self.file) as archive:
            month = 0
            for dat in self.dates:
                date_str = dat["start"].strftime("%Y-%m")
                filename = f"{self.file_prefix}_{date_str}.csv"
                try:
                    with io.TextIOWrapper(archive.open(filename), encoding="iso8859") as csvfile:
                        # nk.log.append(" << %s" % filename)
                        data = self._read_csv_data(csvfile)
                        self._validate_and_store_data(data, month, dat["start"], dat["end"])
                except FileNotFoundError:
                    # self.warnings.append(
                    #    "Could not import data. File in ZIP not found: %s" % filename
                    # )
                    raise RuntimeError(
                        "Konnte Mieteinheit-Messdaten nicht importieren. Datei im ZIP nicht gefunden: %s"
                        % filename
                    )
                except Exception as e:
                    # self.warnings.append(f"Error while reading {filename}: {e}")
                    raise RuntimeError(
                        f"Fehler beim Import der Mieteinheit-Messdaten von {filename}: {e}"
                    )
                month += 1

    def _validate_and_store_data(self, data, month_index, period_start, period_end):
        raise NotImplementedError


class NkMeasurementDataMonthlyCSVFile(NkMeasurementDataMonthly, NkMeasurementDataCSVFile):
    def load(self):
        with open(self.file) as csvfile:
            data = self._read_csv_data(csvfile)
            self._validate_and_store_data(data)

    def _validate_and_store_data(self, data_to_store):
        if len(data_to_store) != len(self.dates):
            raise ValueError(
                _("Number of months in measurement data does not match the billing period.")
            )
        for i, row in enumerate(data_to_store):
            for field, value in row.items():
                if field == "month":
                    self._validate_month(value, self.dates[i])
                else:
                    if field not in self.data:
                        self.data[field] = []
                    self.data[field].append(float(value))

    def _validate_month(self, month_str, date_range):
        expected_month_names = [
            ("Januar", "Jan", "1", "01"),
            ("Februar", "Feb", "2", "02"),
            ("März", "Mär", "3", "03", "MÃ¤rz", "MÃ¤r"),
            ("April", "Apr", "4", "04"),
            ("Mai", "Mai", "5", "05"),
            ("Juni", "Jun", "6", "06"),
            ("Juli", "Jul", "7", "07"),
            ("August", "Aug", "8", "08"),
            ("September", "Sep", "9", "09"),
            ("Oktober", "Okt", "10"),
            ("November", "Nov", "11"),
            ("Dezember", "Dez", "12"),
        ]
        month_index = date_range["start"].month - 1
        if month_str not in expected_month_names[month_index]:
            self.warnings.append(
                (
                    _(
                        "Unexpected month name {month} for period {period}".format(
                            month=month_str,
                            period=f"{date_range['start'].strftime('%d.%m.%Y')}-{date_range['end'].strftime('%d.%m.%Y')}",
                        )
                    ),
                    f"{self.file}/{month_str}",
                )
            )


class NkMeasurementDataEgon(NkMeasurementDataZippedMonthly):
    @staticmethod
    def get_skip_rows() -> list[str]:
        # Ignore rows with totals in Egon data export.
        return ["Gesamt"]

    @staticmethod
    def get_ignore_duplicate_headers() -> list[str]:
        # To work around an issue in the Egon data export. Takes the last column with that header.
        return ["Strombezug EW (CHF)"]

    def _validate_and_store_data(self, data, month_index, period_start, period_end):
        for row in data:
            ru_name = row["rental_unit"]
            ru_id = self._map_to_rental_unit_id(ru_name)
            if not self._validate_time_period(row["time_period"], period_start, period_end):
                self.warnings.append(
                    (
                        _("Unusual measurement period {period}".format(period=row["time_period"])),
                        ru_id,
                    )
                )

            self._store_rental_unit_data(ru_id, ru_name, row, month_index)

    def _store_rental_unit_data(self, ru_id, ru_name, data_to_store, month_index):
        if ru_id not in self.data:
            self.data[ru_id] = {}
            self.imported_rental_unit_names[ru_id] = []
        ru_data = self.data[ru_id]
        for field in self.headers:
            if field not in ("rental_unit", "time_period"):
                if field not in ru_data:
                    ## Initialize
                    ru_data[field] = []
                    for _i in range(month_index):
                        ru_data[field].append(0)
                # else:
                #    if data["object"] not in nk.object_messung[obj_name]["imported_obj_names"]:
                #        nk.object_messung[obj_name]["imported_obj_names"].append(data["object"])
                if len(ru_data[field]) == month_index:
                    ru_data[field].append(float(data_to_store[field]))
                    if ru_name not in self.imported_rental_unit_names[ru_id]:
                        self.imported_rental_unit_names[ru_id].append(ru_name)
                else:
                    if float(data_to_store[field]) != 0:
                        if ru_data[field][month_index] != 0:
                            self.warnings.append(
                                (
                                    _(
                                        "Adding additional measurement for month index {month_index}".format(
                                            month_index=month_index
                                        )
                                    ),
                                    f"{ru_name}/{field}",
                                )
                            )
                        ru_data[field][month_index] += float(data_to_store[field])
                        if ru_name not in self.imported_rental_unit_names[ru_id]:
                            self.imported_rental_unit_names[ru_id].append(ru_name)

    @staticmethod
    def _validate_time_period(
        period: str, period_start: datetime.datetime, period_end: datetime.datetime
    ):
        month_period = "%s - %s" % (
            period_start.strftime("%d.%m.%Y"),
            period_end.strftime("%d.%m.%Y"),
        )
        return period == month_period
        # if period != month_period:
        #     nk.log.append(
        #         "WARNING: Unusual time period %s for object %s"
        #         % (data["time_period"], data["object"])
        #     )
        #     nk.add_warning(
        #         f"Ungewöhnliche Mess-Periode {data['time_period']}", data["object"]
        #     )
        #     return False
        # return True

    @staticmethod
    def _map_to_rental_unit_id(rental_unit_name: str):
        ## Map imported rental unit names to rental unit IDs
        if rental_unit_name in ("Allgemein Warmwasser u Heizen", "Allgemein"):
            return "allg"
        if rental_unit_name == "Hobbyräume und Lager Gesamtstromverbrauch":
            return "strom_pauschal"
        # match = re.search(r"^(\d{3,4}\.?\d?) ", name)
        match = re.search(r"^([0-9a-zA-Z.-]+) ?", rental_unit_name)
        if match:
            # nk.log.append("Match object %s -> %s" % (name, match.group(1)))
            if match.group(1) == "9696":
                return "strom_pauschal"
            return match.group(1)
        raise ValueError(
            _("Invalid rental unit name '{name}' in the measurement data.").format(
                name=rental_unit_name
            )
        )
