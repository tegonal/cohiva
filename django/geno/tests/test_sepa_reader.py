import datetime

from sepa import parser

from geno.sepa_reader import read_camt

from .base import GenoAdminTestCase


class SepaReaderTest(GenoAdminTestCase):
    def test_parse_testfiles(self):
        testfiles = [
            # camt.053
            {
                "file": "camt053_P_CH2909000000250094239_1110092698_0_2020062503071366_v2009.xml",
                "num_transactions": 0,
            },
            {
                "file": "camt053_P_CH2909000000250094239_1110092698_0_2020112503071366_v2019.xml",
                "num_transactions": 0,
            },
            {
                "file": "camt053_CH9100778208005522002_CHF_2024-01-23_2024-01-26.xml",
                "num_transactions": 4,
            },
            {"file": "camt.053_CH5600790016583351934_2025-06-27.xml", "num_transactions": 0},
            # camt.054
            {
                "file": "200519_camt054-ESR-ASR_P_CH2909000000250094239_"
                "1110092704_0_2019042500372179_v2009.xml",
                "num_transactions": 0,
            },
            {
                "file": "200519_camt054-ESR-ASR_P_CH2909000000250094239_"
                "1110092704_0_2019042500372179_v2019.xml",
                "num_transactions": 0,
            },
            {
                "file": "200519_camt054_P_CH2909000000250094239_"
                "1111091335_0_2020061900081727_v2009.xml",
                "num_transactions": 2,
            },
            {
                "file": "200519_camt054_P_CH2909000000250094239_"
                "1111091335_0_2020061900081727_v2019.xml",
                "num_transactions": 2,
            },
            {
                "file": "camt054_P_CH2909000000250094239_1111111112_0_2022031011011199_v2009.xml",
                "num_transactions": 0,
            },
            {
                "file": "camt054_P_CH2909000000250094239_1111111112_0_2022031011011199_v2019.xml",
                "num_transactions": 0,
            },
            {
                "file": "camt054_P_CH2909000000250094239_1111111119_0_2022030911011199_v2009.xml",
                "num_transactions": 0,
            },
            {
                "file": "camt054_P_CH2909000000250094239_1111111119_0_2022030911011199_v2019.xml",
                "num_transactions": 0,
            },
            {
                "file": "camt.054_P_CH5509000000895344367_1115969582_0_2024030423362882.xml",
                "num_transactions": 1,
            },
            {
                "file": "camt.054_CH5600790016583351934_2025-06-27_00070.xml",
                "num_transactions": 1,
                "data": {
                    "amount": "60.00",
                    "reference_nr": "360000000002000000003620253",
                    "debtor": "Hans Muster",
                    "extra_info": "Jahresbeitrag 2025",
                    "date": datetime.date(2025, 6, 27),
                },
            },
            {
                "file": "camt.054_CH5600790016583351934_2025-06-27_00070_with_charges.xml",
                "num_transactions": 1,
                "data": {
                    "amount": "50.00",
                    "reference_nr": "360000000002000000003620253",
                    "debtor": "Hans Muster",
                    "extra_info": "Jahresbeitrag 2025 mit Gebühren",
                    "charges": "1.20",
                    "date": datetime.date(2025, 6, 28),
                },
            },
        ]

        for testfile in testfiles:
            filename = f"geno/tests/camt_files/{testfile['file']}"
            infile = open(filename, "rb")
            xml = infile.read()
            infile.close()

            camt_data = parser.parse_string(None, xml)
            self.assertTrue("document_type" in camt_data)

            data = read_camt(camt_data)
            self.assertTrue("log" in data)
            self.assertTrue("transactions" in data)
            # for l in data['log']:
            #    print(" # %s" % l['info'])
            #    for o in l['objects']:
            #        print("   - %s" % o)
            # print(data['transactions'])
            self.assertEqual(len(data["transactions"]), testfile["num_transactions"])
            if "data" in testfile:
                for key, value in testfile["data"].items():
                    self.assertEqual(data["transactions"][0][key], value)
