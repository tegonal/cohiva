#!/usr/bin/env python3
"""Helper script for tesing the output of the Cohiva report app"""

import csv
import dataclasses
import json
import re


@dataclasses.dataclass
class Table:
    """Holds table data to compare CSVs"""

    header: dict
    rownames: dict
    data: dict


class CompareCSV:
    """Compare a test CVS file with a table to a reference file"""

    valid_empty_values = ("", "[empty]", "NULL")

    def __init__(self, test_file, reference_file):
        self._files = {"test": test_file, "ref": reference_file}
        self._table = Table(header={}, rownames={}, data={})
        self._maxcol = 0
        self._maxrow = 0
        self._mincol = None
        self._minrow = None
        self._result = []

    def compare(self):
        """Compare test to ref data"""
        self.read_csv("test")
        self.read_csv("ref")
        self._compare_header()
        self._compare_rownames()
        self._compare_data()
        return self._result

    def read_csv(self, filetype):
        """Read CSV file to table"""
        with open(self._files[filetype], encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            header = True
            for row in reader:
                if header:
                    self._table.rownames[filetype] = []
                    self._table.header[filetype] = row[1:]
                    self._table.data[filetype] = []
                    header = False
                else:
                    if row:
                        self._table.rownames[filetype].append(row[0])
                        self._table.data[filetype].append(row[1:])
                    else:
                        self._table.rownames[filetype].append("[empty]")
                        self._table.data[filetype].append([""])

    def _compare_header(self):
        test = self._table.header["test"]
        ref = self._table.header["ref"]
        if len(test) > len(ref):
            self._maxcol = len(test)
            self._mincol = len(ref)
        else:
            self._maxcol = len(ref)
            self._mincol = len(test)
        for i in range(self._maxcol):
            if i >= len(test):
                self._result.append(f"Header only in ref: {ref[i]}")
            elif i >= len(ref):
                self._result.append(f"Header only in test: {test[i]}")
            elif ref[i] != test[i]:
                self._result.append(f"Header differ: test={test[i]}, ref={ref[i]}")
        # print(test, "\n======")
        # print(ref)

    def _compare_rownames(self):
        test = self._table.rownames["test"]
        ref = self._table.rownames["ref"]
        if len(test) > len(ref):
            self._maxrow = len(test)
            self._minrow = len(ref)
        else:
            self._maxrow = len(ref)
            self._minrow = len(test)
        for i in range(self._maxrow):
            if i >= len(test):
                self._result.append(f"Row only in ref: {ref[i]}")
            elif i >= len(ref):
                self._result.append(f"Row only in test: {test[i]}")
            elif ref[i] in self.valid_empty_values and test[i] in self.valid_empty_values:
                continue
            elif ref[i] != test[i]:
                self._result.append(f"Rows differ: test={test[i]}, ref={ref[i]}")
        # print(test, "\n======")
        # print(ref)

    def _compare_data(self):
        test = self._table.data["test"]
        ref = self._table.data["ref"]
        for i in range(self._minrow):
            for j in range(self._mincol):
                try:
                    refval = ref[i][j]
                except IndexError:
                    refval = ""
                try:
                    testval = test[i][j]
                except IndexError:
                    testval = ""
                if refval in self.valid_empty_values and testval in self.valid_empty_values:
                    continue
                try:
                    ## Accept rounding errors after the tenth decimal place
                    refval = round(float(refval), 10)
                    testval = round(float(testval), 10)
                except ValueError:
                    ## Not a float
                    pass
                if refval != testval:
                    rowname = self._table.rownames["ref"][i]
                    header = self._table.header["ref"][j]
                    self._result.append(
                        f"Data differ for {rowname}: {header} test={testval}, ref={refval}"
                    )


class CompareJSON:
    """Compare a test JSON file to a reference file"""

    _refdata2022_workaround = False

    if _refdata2022_workaround:
        _ignore_path_re = (
            r"^\.contracts\.\d+\.url$",
            r"^\.contracts\.\d+\.ts_modified$",
            r"^\.contracts\.\d+\.contractors",
            r"^\.contracts\.\d+\.main_contact",
            r"^\.contracts\.\d+\.send_qrbill",
            r"^\.contracts\.\d+\.comment",
            r"^\.contracts\.\d+\.date_end",
            r"^\.contracts\.\d+\.share_reduction",
            r"^\.korrektur_strom\.0000\[1\]\.desc",
        )
    else:
        _ignore_path_re = (
            r"^\.contracts\.\d+\.url$",
            r"^\.contracts\.\d+\.ts_",
            # r"^\.contracts\.\d+\.contractors",
            # r"^\.contracts\.\d+\.rental_units",
            # r"^\.contracts\.\d+\.main_contact",
        )

    if _refdata2022_workaround:
        _ignore_keys = ("dates", "amount", "monthly_weights", "section_weights", "object_weights")
    else:
        _ignore_keys = "has_graph"

    def __init__(self, test_file, reference_file):
        self._files = {"test": test_file, "ref": reference_file}
        self._data = {"test": None, "ref": None}
        self._contract_id_offset = 0
        self._object_id_offset = 0
        self._address_id_offset = 0
        self._result = []

    def compare(self):
        """Compare test to ref data"""
        self.read_json("test")
        self.read_json("ref")
        self._compare_data()
        return self._result

    def read_json(self, filetype):
        """Read JSON file to table"""
        with open(self._files[filetype], encoding="utf8") as jsonfile:
            self._data[filetype] = json.load(jsonfile)

    def _compare_data(self):
        test_contract_id = self._data["test"]["active_contracts"][0]
        ref_contract_id = self._data["ref"]["active_contracts"][0]
        self._contract_id_offset = int(test_contract_id) - int(ref_contract_id)
        self._object_id_offset = int(self._data["test"]["objects"][2]["id"]) - int(
            self._data["ref"]["objects"][2]["id"]
        )
        self._address_id_offset = int(
            self._data["test"]["contracts"][test_contract_id]["contractors"][0]
        ) - int(self._data["ref"]["contracts"][ref_contract_id]["contractors"][0])
        self._compare_item(self._data["test"], self._data["ref"])

    def _compare_item(self, test, ref, path=""):
        for pattern in self._ignore_path_re:
            if re.match(pattern, path):
                return
        if isinstance(ref, dict):
            self._compare_dict(test, ref, path)
            return
        elif isinstance(ref, list):
            self._compare_list(test, ref, path)
            return
        elif re.match(r"\.contracts\.\d+.contractors\[\d+\]$", path):
            if self._add_address_offset(ref) == str(test):
                return
        elif re.match(r".*contracts(?:\[\d+\]|\.\d+\.id)$", path):
            if self._add_contract_offset(ref) == str(test):
                return
        elif re.match(r".*\.objects(?:\[\d+\]|\..*\.unit)\.id$", path) or re.match(
            r".*rental_units\[\d+\]$", path
        ):
            if self._add_object_offset(ref) == str(test):
                return
        else:
            if (
                self._refdata2022_workaround
                and isinstance(test, str)
                and test.endswith(" 00:00:00.000000")
            ):
                testval = test[0:10]
            else:
                testval = test
            if testval == ref:
                return
        self._result.append(
            f"{path}: Values differ: test={test} != ref={ref} [contract_offset={self._contract_id_offset}, object_offset={self._object_id_offset}, address_offset={self._address_id_offset}"
        )

    def _compare_dict(self, test, ref, path):
        if not isinstance(test, dict):
            self._result.append(f"{path}: Reference is a dict but test is not!")
            return
        found_keys = []
        for key in ref:
            if key in test:
                found_keys.append(key)
                self._compare_item(test[key], ref[key], f"{path}.{key}")
            elif self._add_contract_offset(key) in test:
                test_key = self._add_contract_offset(key)
                found_keys.append(test_key)
                self._compare_item(test[test_key], ref[key], f"{path}.{key}")
            elif key != "has_graph":  ## Will be missing in reduced tests
                self._result.append(f"{path}: Key {key} is missing in TEST data.")
        for key in test:
            if key not in found_keys:
                if key not in self._ignore_keys:  ## dates added after 2022/2023
                    self._result.append(f"{path}: Key {key} is missing in REF data.")

    def _compare_list(self, test, ref, path):
        if not isinstance(test, list):
            self._result.append(f"{path}: Reference is a list but test is not!")
            return
        for i in range(max(len(ref), len(test))):
            try:
                testval = test[i]
            except IndexError:
                testval = ""
            try:
                refval = ref[i]
            except IndexError:
                refval = ""
            self._compare_item(testval, refval, f"{path}[{i}]")

    def _add_contract_offset(self, key):
        try:
            return str(int(key) + self._contract_id_offset)
        except (TypeError, ValueError):
            return "___NOT_FOUND___"

    def _add_object_offset(self, key):
        try:
            return str(int(key) + self._object_id_offset)
        except (TypeError, ValueError):
            return "___NOT_FOUND___"

    def _add_address_offset(self, key):
        try:
            return str(int(key) + self._address_id_offset)
        except (TypeError, ValueError):
            return "___NOT_FOUND___"


def run_checks(test_output_root="/var/www/g8/django-test/smedia"):
    """Run checks on Cohiva report output"""
    result = []
    csvdiff = CompareCSV(
        test_output_root + "/report/1/Abrechnung.csv",
        "/var/www/g8/django/report/tests/reference_export_2022-2023.csv",
    )
    result.extend(csvdiff.compare())

    jsondiff = CompareJSON(
        test_output_root + "/report/1/Rohdaten.json",
        "/var/www/g8/django/report/tests/reference_data_2022-2023.json",
    )
    result.extend(jsondiff.compare())
    return result


if __name__ == "__main__":
    output = run_checks("/var/www/g8/django-production/smedia")
    # output = run_checks("/var/www/g8/django-test/tests")
    print("\n".join(output))
