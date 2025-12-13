import datetime


class SepaReaderException(Exception):
    """SEPA reader exception"""


def read_camt_transaction(data, tr, date_str, entry_ref=None):
    log = []

    if (
        "message_id" not in tr["refs"]
        and "instruction_id" not in tr["refs"]
        and "account_servicer_reference" not in tr["refs"]
    ):
        return [
            "Ignoring transaction without message_id/instruction_id/account_servicer_reference: %s"
            % tr["amount"]["_value"],
        ]

    tx_id = "%s_%s_%s" % (
        tr["refs"].get("message_id", ""),
        tr["refs"].get("account_servicer_reference", ""),
        tr["refs"].get("instruction_id", ""),
    )
    amount = tr["amount"]["_value"]
    charges = ""
    if "charges" in tr:
        if "total" in tr["charges"]:
            charges = tr["charges"]["total"]
        elif tr["charges"].get("record", []):
            if len(tr["charges"]["record"]) == 1:
                charges = tr["charges"]["record"][0]["amount"]["_value"]
            else:
                raise SepaReaderException(
                    "More than one charge record: %s %s" % (tx_id, tr["charges"])
                )
    if "related_parties" not in tr or "debtor" not in tr["related_parties"]:
        return [
            "Ignoring transaction without debtor: %s" % tr["amount"]["_value"],
        ]
    else:
        debtor_party = tr["related_parties"]["debtor"].get(
            "party", tr["related_parties"]["debtor"]
        )
        if "name" in debtor_party:
            debtor = debtor_party["name"]
        elif "postal_address" in debtor_party:
            debtor = ", ".join(debtor_party["postal_address"].get("address", []))
        else:
            debtor = "<Unbekannt>"
    try:
        account = tr["related_parties"]["creditor_account"]["id"]["iban"]
    except KeyError:
        if (
            isinstance(entry_ref, str)
            and len(entry_ref) > 10
            and entry_ref[0:2]
            in ("CH", "DE", "FR", "IT", "GB", "ES", "LI", "LU", "BE", "NL", "PT", "AT")
        ):
            account = entry_ref
        else:
            account = data["account_iban"]
    if "remittance_information" not in tr or "structured" not in tr["remittance_information"]:
        return [
            "Ignoring transaction without structured information: %s %s %s"
            % (tx_id, debtor, amount),
        ]
    re_info = tr["remittance_information"]["structured"]
    if len(re_info) != 1:
        raise SepaReaderException(
            "More than one structured remittance_information: %s %s" % (tx_id, debtor)
        )
    if "creditor_reference_information" not in re_info[0]:
        return ["Ignoring transaction without creditor reference information."]
    reference_type = re_info[0]["creditor_reference_information"]["type"]["document_line"][
        "property"
    ]
    if reference_type != "QRR":
        raise SepaReaderException(
            "Unknown creditor reference type: %s - %s %s" % (reference_type, tx_id, debtor)
        )
    reference_nr = re_info[0]["creditor_reference_information"]["reference"]

    if "additional_information" in re_info[0]:
        # if len(re_info[0]['additional_information']) > 1:
        #    log.append("WARNING: More than one additional_information: %s %s" % (tx_id, debtor))
        add_info_arr = []
        for add_info in re_info[0]["additional_information"]:
            ## Warn about errors and filter non-error messages
            exclude_info = False
            if add_info.startswith("?REJECT?"):
                if add_info == "?REJECT?0":
                    exclude_info = True
                else:
                    log.append(f"WARNING: REJECT code is not zero: {add_info}")
            if add_info.startswith("?ERROR?"):
                if add_info == "?ERROR?000":
                    exclude_info = True
                else:
                    log.append(f"WARNING: ERROR code is not zero: {add_info}")
            if not exclude_info:
                add_info_arr.append(add_info)
        additional_info = "|".join(add_info_arr)
    else:
        additional_info = ""

    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    data["transactions"].append(
        {
            "id": tx_id,
            "account": account,
            "date": date,
            "amount": amount,
            "reference_nr": reference_nr,
            "debtor": debtor,
            "extra_info": additional_info,
            "charges": charges,
        }
    )
    return log


def read_camt(input_data):
    data = {"transactions": [], "log": []}

    if "statements" in input_data:
        ## camt.053
        statements = input_data["statements"]
    elif "notifications" in input_data:
        ## camt.054
        statements = input_data["notifications"]
    else:
        raise SepaReaderException(
            "Statements/Notifications not found in input data. keys: %s" % list(input_data.keys())
        )
    if len(statements) != 1:
        raise SepaReaderException("More than one statement/notification: %s" % len(statements))

    data["account_iban"] = statements[0]["account"]["id"]["iban"]
    data["log"].append({"info": "account_iban = %s" % data["account_iban"], "objects": []})

    for entry in statements[0]["entries"]:
        read_camt_entry(data, entry)

    return data


def read_camt_entry(data, entry):
    if "reference" in entry:
        entry_ref = entry["reference"]
    else:
        entry_ref = ""
    entry_amount = entry["amount"]["_value"]
    entry_currency = entry["amount"]["currency"]
    entry_date = entry["booking_date"]["date"]
    if entry["credit_debit_indicator"] == "DBIT":
        data["log"].append(
            {"info": "Ignoring DBIT entry: %s %s" % (entry_date, entry_amount), "objects": []}
        )
        return
    if entry_date != entry["value_date"]["date"]:
        data["log"].append(
            {
                "info": "WARNING: booking and value dates differ: %s != %s"
                % (entry_date, entry["value_date"]["date"]),
                "objects": [],
            }
        )
    if entry_currency != "CHF":
        raise SepaReaderException("Unknown entry currency: %s" % entry_currency)
    entry_log_info = "Entry: ref = %s, amount = %s %s, date = %s" % (
        entry_ref,
        entry_amount,
        entry_currency,
        entry_date,
    )

    entry_details = entry["entry_details"]
    if len(entry_details) != 1:
        raise SepaReaderException("More than one entry detail: %s" % len(entry_details))

    transaction_log = []
    if "transaction_details" in entry_details[0]:
        for transaction in entry_details[0]["transaction_details"]:
            transaction_log += read_camt_transaction(data, transaction, entry_date, entry_ref)

    data["log"].append({"info": entry_log_info, "objects": transaction_log})
