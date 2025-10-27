import collections
import datetime

## For interest calc.
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Q

from finance.accounting import AccountingManager
from finance.accounting.accounts import Account, AccountKey

from .models import Address, RentalUnit, Share, ShareType, get_active_contracts, get_active_shares
from .utils import is_member, nformat


class IncompatibleInterestRates(Exception):
    pass


class IncompatibleDates(Exception):
    pass


def get_share_statement_data(adr, year, enddate=None):
    now = datetime.datetime.now()
    year_current = now.year
    year_prev = year - 1
    response_duedate = now + datetime.timedelta(days=30)
    if enddate:
        enddate_str = enddate.strftime("%d.%m.%Y")
        if not enddate_str.endswith(str(year)):
            raise IncompatibleDates(
                "Jahr %s und Enddatum %s sind nicht kompatibel!" % (year, enddate)
            )
    else:
        enddate_str = "31.12.%d" % year
    line_count = 0
    statement_data = {
        "sect_shares": False,
        "n_shares": 0,
        "s_shares": 0,
        "sect_bvg": False,
        "s_shares_bvg": 0,
        "sect_loan": False,
        "loan_noint": False,
        "s_loan_no": 0,
        "loan_int": False,
        "s_loan": 0,
        "inter_loan_int": [],
        "p_loan": 0,
        "sect_loan_int_total": False,
        "loan_no_duedates": "",
        "loan_duedates": "",
        "sect_deposit": False,
        "dep_start": 0,
        "dep_end": 0,
        "dep_out": 0,
        "dep_in": 0,
        "deposit_changes": [],
        "sect_interest": False,
        "sect_tax": False,
        "s_int": 0,
        "s_tax": 0,
        "s_pay": 0,
        "tax_info_text": "",
        "sect_donation": False,
        "s_donation": 0,
        "year": year,
        "year_current": year_current,
        "year_prev": year_prev,
        "enddate": enddate_str,
        "betreff": "Kontoauszug/Bestätigung Beteiligung",
        "response_duedate": response_duedate.strftime("%-d. %B"),
        "thankyou": False,
        "form": False,
        "form_option_one": "direkt meinem Darlehen anrechnen",
        "loan_default_action": "",
        "loan_and_deposit_int": False,
        "pagebreak1": False,
        "pagebreak2": False,
    }

    ## Get assets by end of the year and calculate interest/taxes
    inter = share_interest_calc(adr, year, enddate)
    if inter["end_amount"][0]:
        ## Anteilscheine
        statement_data["sect_shares"] = True
        statement_data["n_shares"] = inter["end_quantity"][0]
        statement_data["s_shares"] = inter["end_amount"][0]
        statement_data["s_shares_bvg"] = inter["bvg_amount"][0]
        if statement_data["s_shares_bvg"] > 0:
            statement_data["sect_bvg"] = True
        if statement_data["n_shares"] > settings.GENO_SMALL_NUMBER_OF_SHARES_CUTOFF:
            statement_data["thankyou"] = True
    if inter["end_amount"][1]:
        ## Zinslose Darlehen
        statement_data["sect_loan"] = True
        statement_data["loan_noint"] = True
        statement_data["thankyou"] = True
        statement_data["s_loan_no"] = inter["end_amount"][1]
        if inter["due_date_min"][1]:
            statement_data["loan_no_duedates"] = ", Fälligkeit: %s" % inter["due_date_min"][
                1
            ].strftime("%d.%m.%Y")
            if inter["due_date_max"][1] != inter["due_date_min"][1]:
                statement_data["loan_no_duedates"] += "/%s" % inter["due_date_max"][1].strftime(
                    "%d.%m.%Y"
                )
    if inter["end_amount"][2] or inter["total"][2]:
        ## Verzinste Darlehen
        statement_data["sect_loan"] = True
        statement_data["loan_int"] = True
        statement_data["sect_interest"] = True
        statement_data["thankyou"] = True
        statement_data["s_loan"] = inter["end_amount"][2]
        if inter["due_date_min"][2]:
            statement_data["loan_duedates"] = ", Fälligkeit: %s" % inter["due_date_min"][
                2
            ].strftime("%d.%m.%Y")
            if inter["due_date_max"][2] != inter["due_date_min"][2]:
                statement_data["loan_duedates"] += "/%s" % inter["due_date_max"][2].strftime(
                    "%d.%m.%Y"
                )
    if inter["dates"][3] or inter["total"][3]:
        ## Depositenkasse
        statement_data["sect_deposit"] = True
        statement_data["sect_interest"] = True
        statement_data["thankyou"] = True
        statement_data["dep_start"] = inter["start_amount"][3]
        statement_data["dep_end"] = inter["end_amount"][3]
        last = statement_data["dep_start"]
        last_enddate = datetime.date(year, 1, 1)
        for d in inter["dates"][3]:
            # pprint.pprint(d)
            diff = d["amount"] - last
            if diff > 0:
                statement_data["dep_in"] += diff
                statement_data["deposit_changes"].append(
                    {
                        "date": d["start"].strftime("%d.%m.%Y"),
                        "text": "Einzahlung",
                        "out": "",
                        "in": nformat(diff),
                        "bal": nformat(d["amount"]),
                    }
                )
            elif diff < 0:
                statement_data["dep_out"] += -1 * diff
                statement_data["deposit_changes"].append(
                    {
                        "date": d["start"].strftime("%d.%m.%Y"),
                        "text": "Auszahlung",
                        "in": "",
                        "out": nformat(-1 * diff),
                        "bal": nformat(d["amount"]),
                    }
                )
            last = d["amount"]
            last_enddate = d["end"]
        if last != statement_data["dep_end"]:
            diff = statement_data["dep_end"] - last
            if diff < 0:
                statement_data["dep_out"] += -1 * diff
                statement_data["deposit_changes"].append(
                    {
                        "date": last_enddate.strftime("%d.%m.%Y"),
                        "text": "Auszahlung",
                        "in": "",
                        "out": nformat(-1 * diff),
                        "bal": nformat(statement_data["dep_end"]),
                    }
                )
            else:
                raise RuntimeError("Assert failed in last != dep_end handling")
    if inter["end_amount"][4] or inter["total"][4]:
        ## Darlehen Spezial --> Überschreibt normale verzinste Darlehen!
        statement_data["sect_loan"] = True
        statement_data["loan_int"] = True
        statement_data["sect_interest"] = True
        statement_data["thankyou"] = True
        statement_data["s_loan"] = inter["end_amount"][4]
        if inter["due_date_min"][4]:
            statement_data["loan_duedates"] = ", Fälligkeit: %s" % inter["due_date_min"][
                4
            ].strftime("%d.%m.%Y")
            if inter["due_date_max"][4] != inter["due_date_min"][4]:
                statement_data["loan_duedates"] += "/%s" % inter["due_date_max"][4].strftime(
                    "%d.%m.%Y"
                )

    ## Add interest information
    if statement_data["sect_interest"]:
        ## Zins Darlehen
        if inter["end_amount"][4] or inter["total"][4]:
            ## Darlehen Spezial --> Überschreibt normale verzinste Darlehen!
            statement_data["p_loan"] = nformat(inter["pay"][4])
            inter_dates = inter["dates"][4]
            inter_tax = inter["tax"][4]
            inter_total = inter["total"][4]
        else:
            ## Darlehen Normal
            statement_data["p_loan"] = nformat(inter["pay"][2])
            inter_dates = inter["dates"][2]
            inter_tax = inter["tax"][2]
            inter_total = inter["total"][2]
        for d in inter_dates:
            statement_data["inter_loan_int"].append(
                {
                    "date": enddate_str,
                    "text": "Zinsen %s-%s, %d Tage"
                    % (d["start"].strftime("%d.%m.%y"), d["end"].strftime("%d.%m.%y"), d["days"]),
                    "amount": "Fr. %s zu %s%%"
                    % (nformat(d["amount"]), nformat(d["interest_rate"])),
                    "total": nformat(d["interest"]),
                }
            )
        if statement_data["loan_int"] and statement_data["sect_deposit"]:
            statement_data["sect_loan_int_total"] = True
            if inter_tax:
                statement_data["inter_loan_int"].append(
                    {
                        "date": enddate_str,
                        "text": "Verrechnungssteuer",
                        "amount": "Fr. %s zu 35%%" % (inter_total),
                        "total": nformat(-1 * inter_tax),
                    }
                )

        ## Zins Depositenkasse
        statement_data["dep_end"] += inter["total"][3]
        statement_data["dep_in"] += inter["total"][3]
        if inter["total"][3] != 0:
            statement_data["deposit_changes"].append(
                {
                    "date": enddate_str,
                    "text": "Brutto-Zinsen Depositenkasse %s%%"
                    % inter["dates"][3][0]["interest_rate"],
                    "out": "",
                    "in": nformat(inter["total"][3]),
                    "bal": nformat(statement_data["dep_end"]),
                }
            )
        if inter["tax"][3]:
            statement_data["dep_end"] -= inter["tax"][3]
            statement_data["dep_out"] += inter["tax"][3]
            statement_data["deposit_changes"].append(
                {
                    "date": enddate_str,
                    "text": "Verrechnungssteuer 35%",
                    "out": nformat(inter["tax"][3]),
                    "in": "",
                    "bal": nformat(statement_data["dep_end"]),
                }
            )

        ## Zinsausweis
        if inter["tax_alltypes"]:
            statement_data["sect_tax"] = True
            statement_data["tax_info_text"] = (
                " und für die Rückforderung der Verrechnungssteuer, welche wir für "
                "Zinsgutschriften über Fr. 200.- entrichten müssen. Die Verrechnungssteuer "
                "kann beim Einreichen der Steuererklärung von der Steuerverwaltung "
                "zurückgefordert werden"
            )
        statement_data["s_int"] = nformat(inter["total_alltypes"])
        statement_data["s_tax"] = -1 * inter["tax_alltypes"]
        statement_data["s_pay"] = inter["pay_alltypes"]
        statement_data["betreff"] = "Kontoauszug / Zinsausweis"

    ## Formular:
    if inter["total"][2]:
        statement_data["form"] = True
        if adr.interest_action == "Bank" and adr.bankaccount:
            statement_data["loan_default_action"] = "auf das Konto %s überweisen" % adr.bankaccount
        elif adr.interest_action == "Loan":
            statement_data["loan_default_action"] = "direkt dem Darlehen anrechnen"
        elif adr.interest_action == "Deposit":
            statement_data["loan_default_action"] = "direkt dem Depositenkonto anrechnen"
        if inter["total"][3]:
            statement_data["form_option_one"] = "direkt meinem Depositenkonto anrechnen"
            statement_data["loan_and_deposit_int"] = True

    ## Spenden:
    donations = share_get_donations(adr, year, enddate)
    if donations > 0:
        statement_data["sect_donation"] = True
        statement_data["s_donation"] = nformat(donations)

    ## Seitenumbruch
    if statement_data["sect_shares"]:
        line_count += 3
    if statement_data["sect_loan"]:
        line_count += 2
        if statement_data["loan_noint"]:
            line_count += 1
        if statement_data["loan_int"]:
            line_count += 2 + len(statement_data["inter_loan_int"])
            if statement_data["sect_loan_int_total"]:
                line_count += 1
    if statement_data["sect_deposit"]:
        line_count += 4 + len(statement_data["deposit_changes"]) + 1
    if statement_data["sect_interest"]:
        line_count += 3
        if statement_data["sect_tax"]:
            line_count += 2
    line_count += 3
    if statement_data["sect_tax"]:
        line_count += 2
    line_count += 3
    if statement_data["thankyou"]:
        line_count += 2
    line_count += 3

    if line_count <= 28:
        statement_data["pagebreak2"] = True
    elif line_count <= 40:
        statement_data["pagebreak1"] = True
    elif line_count > 41:
        raise RuntimeError("Auszug mit mehr als 41 Zeilen wird derzeit nicht unterstützt.")

    for k in (
        "s_shares",
        "s_shares_bvg",
        "s_loan_no",
        "s_loan",
        "dep_start",
        "dep_end",
        "dep_out",
        "dep_in",
    ):
        statement_data[k] = nformat(statement_data[k])
    if statement_data["n_shares"] == 1:
        statement_data["n_shares"] = "1 Anteilschein"
    else:
        statement_data["n_shares"] = "%s Anteilscheine" % nformat(statement_data["n_shares"], 0)

    statement_data["line_count"] = line_count

    return statement_data


## Returns dict with:
##  A) Arrays for each share type [0=Anteilschein, 1=Darlehen zinslos,
##     2=Darlehen verzinst, 3=Depositenkasse, 4=Darlehen spezial]
##
##  -'start_quantity'  Quantities and amounts at start and end of period
##  -'start_amount'
##  -'end_quantity'
##  -'end_amount'
##
##  -'total'           Sum of interest and number of day for full time period
##  -'total_days'
##  -'tax'             Tax and interest minus tax for full time period
##  -'pay'
##
##  -'dates'           Detailed list for all the sub-periods [array of dict
##                     {'start','end','type','amount','days','interest_rate','interest'}]
##
## B) Totals for all shares [single value]
##
##  - 'total_alltypes' Single values (all shares) for interest, tax and interest without taxes
##  - 'tax_alltypes'
##  - 'pay_alltypes'
##
def share_interest_calc(address, year, enddate=None):
    period_start = datetime.date(year, 1, 1)
    year_end = datetime.date(year + 1, 1, 1)
    if enddate:
        period_end = enddate + datetime.timedelta(days=1)
    else:
        period_end = year_end
    year_days = (year_end - period_start).days

    stype_share = list(ShareType.objects.filter(name__startswith="Anteilschein"))  ## type index 0
    stype_loan_noint = list(ShareType.objects.filter(name="Darlehen zinslos"))  ## type index 1
    stype_loan_int = list(ShareType.objects.filter(name="Darlehen verzinst"))  ## type index 2
    stype_deposit = list(ShareType.objects.filter(name="Depositenkasse"))  ## type index 3
    stype_loan_special = list(ShareType.objects.filter(name="Darlehen spezial"))  ## type index 4

    total_interest_alltypes = 0
    list_dates = []
    list_due_date_min = []
    list_due_date_max = []
    list_total_days = []
    list_total_interest = []
    list_start_quantity = []
    list_start_amount = []
    list_end_quantity = []
    list_end_amount = []
    list_bvg_amount = []
    # pp = pprint.PrettyPrinter(indent=4)
    for stype in (
        stype_share,
        stype_loan_noint,
        stype_loan_int,
        stype_deposit,
        stype_loan_special,
    ):
        # print('### %s -- %s' % (address, stype.name))
        ## Get relevant dates and items
        dates = []
        items = []
        due_date_min = None
        due_date_max = None
        total_interest = 0
        total_days = 0
        count = 0
        start_amount = 0
        start_quantity = 0
        end_quantity = 0
        end_amount = 0
        bvg_amount = 0
        stype_str = "/".join(map(str, stype))
        for share in (
            Share.objects.filter(name=address)
            .filter(share_type__in=stype)
            .filter(state="bezahlt")
            .filter(date__lt=period_end)
            .filter(Q(date_end=None) | Q(date_end__gte=period_start))
            .exclude(
                Q(date=datetime.date(year, 12, 31))
                & Q(is_interest_credit=True)  ## Exclude already booked interest of this period
            )
            .order_by("date")
        ):
            amount = share.quantity * share.value
            if share.date < period_start:
                start = period_start
                start_amount += amount
                start_quantity += share.quantity
            else:
                start = share.date
            if share.date_end is None or share.date_end >= period_end:
                end = period_end
                end_quantity += share.quantity
                end_amount += amount
                if share.is_pension_fund:
                    bvg_amount += amount

                if share.date_due:
                    duedate = share.date_due
                elif share.duration:
                    duedate = share.date + relativedelta(years=share.duration)
                else:
                    duedate = None
                if duedate:
                    if not due_date_min or duedate < due_date_min:
                        due_date_min = duedate
                    if not due_date_max or duedate > due_date_max:
                        due_date_max = duedate
            else:
                end = share.date_end + datetime.timedelta(days=1)
            if start not in dates:
                dates.append(start)
            if end not in dates:
                dates.append(end)

            items.append(
                {
                    "start": start,
                    "end": end,
                    "amount": amount,
                    "interest": share.interest(),
                    "is_interest_credit": share.is_interest_credit,
                }
            )

        ## Aggregate items for time periods [a,b]
        a = None
        b = None
        objects = []
        for date in sorted(dates):
            # print(str(date))
            if a is None:
                ## First element
                a = date
                continue
            if date == datetime.date(year, 12, 31):
                b = date
                a_next = date + datetime.timedelta(days=1)
            else:
                b = date - datetime.timedelta(days=1)
                a_next = date

            ## Aggregate and calculate interest
            total = 0
            interest_rate = None
            for i in items:
                if i["start"] <= a and i["end"] >= b:
                    total += i["amount"]
                    if interest_rate is not None and interest_rate != i["interest"]:
                        raise IncompatibleInterestRates(
                            f"Inkompatible Zinssätze: {interest_rate} vs. {i['interest']} "
                            f"von Beteiligung CHF {i['amount']}/{i['start']} [{address}]"
                        )
                    interest_rate = i["interest"]

            days = (b - a).days + 1
            if total > 0 and days > 0:  # and interest_rate > 0:
                interest = total * interest_rate / Decimal("100") * days / year_days
                interest = interest.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
                objects.append(
                    {
                        "start": a,
                        "end": b,
                        "type": stype_str,
                        "amount": total,
                        "days": days,
                        "interest_rate": interest_rate,
                        "interest": interest,
                    }
                )
                count += 1
                total_days += days
                total_interest += interest
                total_interest_alltypes += interest

            ## Move on
            a = a_next
            b = None

        ## Add data for type
        list_dates.append(objects)
        list_due_date_min.append(due_date_min)
        list_due_date_max.append(due_date_max)
        list_total_days.append(total_days)
        list_total_interest.append(total_interest)
        list_start_amount.append(start_amount)
        list_start_quantity.append(start_quantity)
        list_end_quantity.append(end_quantity)
        list_end_amount.append(end_amount)
        list_bvg_amount.append(bvg_amount)

    ## Return data
    interest_tax = []
    interest_pay = []
    if total_interest_alltypes > 200:
        interest_tax_alltypes = Decimal("0.35") * total_interest_alltypes
        interest_tax_alltypes = interest_tax_alltypes.quantize(
            Decimal(".01"), rounding=ROUND_HALF_UP
        )
        interest_pay_alltypes = total_interest_alltypes - interest_tax_alltypes
        for t in list_total_interest:
            tax = Decimal("0.35") * t
            tax = tax.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
            interest_tax.append(tax)
            interest_pay.append(t - tax)
    else:
        interest_tax_alltypes = 0
        interest_pay_alltypes = total_interest_alltypes
        for t in list_total_interest:
            interest_tax.append(0)
            interest_pay.append(t)

    ret = {
        "dates": list_dates,
        "due_date_min": list_due_date_min,
        "due_date_max": list_due_date_max,
        "start_quantity": list_start_quantity,
        "start_amount": list_start_amount,
        "end_quantity": list_end_quantity,
        "end_amount": list_end_amount,
        "bvg_amount": list_bvg_amount,
        "total_days": list_total_days,
        "total": list_total_interest,
        "total_alltypes": total_interest_alltypes,
        "tax": interest_tax,
        "tax_alltypes": interest_tax_alltypes,
        "pay": interest_pay,
        "pay_alltypes": interest_pay_alltypes,
    }
    return ret


def create_interest_transactions():
    year_current = datetime.datetime.now().year
    book_date = datetime.date(year_current - 1, 12, 31)
    ret = []

    ## Try to guess if transactions have already been made
    count = Share.objects.filter(is_interest_credit=True).filter(date=book_date).count()
    if count:
        ret.append(
            {
                "info": "WARNUNG: Es sieht so aus als ob die Zinsbuchungen schon ausgeführt "
                "wurden (%d Zins-Beteiligungen gefunden). Bitte überprüfen!" % count
            }
        )

    result = create_interest_transactions_execute(book_date)
    ret.extend(result)
    return ret


def create_interest_transactions_execute(book_date):
    ret = []
    transaction_info = {
        # 2 - Darlehen normal: Zinsaufwand Darlehen => Verbindlichkeiten
        2: {
            "name": "Darlehen",
            "acc_zins": Account.from_settings(AccountKey.INTEREST_LOAN),
            "acc_pay": Account.from_settings(AccountKey.SHARES_INTEREST),
            "acc_tax": Account.from_settings(AccountKey.SHARES_INTEREST_TAX),
        },
        # 4 - Darlehen spezial: Zinsaufwand Darlehen => Verbindlichkeiten
        4: {
            "name": "Darlehen",
            "acc_zins": Account.from_settings(AccountKey.INTEREST_LOAN),
            "acc_pay": Account.from_settings(AccountKey.SHARES_INTEREST),
            "acc_tax": Account.from_settings(AccountKey.SHARES_INTEREST_TAX),
        },
        # 3 - Depositenkasse: Zinsaufwand Depositenkasse => Depositenkasse
        3: {
            "name": "Depositenkasse",
            "acc_zins": Account.from_settings(AccountKey.INTEREST_DEPOSIT),
            "acc_pay": Account.from_settings(AccountKey.SHARES_DEPOSIT),
            "acc_tax": Account.from_settings(AccountKey.SHARES_INTEREST_TAX),
        },
    }

    book_messages = []
    with AccountingManager(book_messages) as book:
        if not book:
            ret.append({"info": f"FEHLER: {book_messages[-1]}"})
            return ret

        ## Create transactions
        new_shares = []
        for adr in Address.objects.filter(active=True).order_by("name"):
            obj = []
            try:
                interest = share_interest_calc(adr, book_date.year)
                for idx in (2, 3, 4):
                    if interest["total"][idx] > 0:
                        info = add_interest_transaction(
                            book,
                            book_date,
                            adr,
                            transaction_info[idx]["name"],
                            interest["dates"][idx][0]["interest_rate"],
                            interest["total"][idx],
                            interest["tax"][idx],
                            interest["pay"][idx],
                            transaction_info[idx]["acc_zins"],
                            transaction_info[idx]["acc_pay"],
                            transaction_info[idx]["acc_tax"],
                        )
                        obj.append(info)
                if interest["total"][3] > 0:
                    ## New share for Depositenkassen-Zins
                    interest_rate = interest["dates"][3][0]["interest_rate"]
                    new_shares.append(
                        Share(
                            name=adr,
                            share_type=ShareType.objects.get(name="Depositenkasse"),
                            date=book_date,
                            quantity=1,
                            value=interest["pay"][3],
                            is_interest_credit=True,
                            state="bezahlt",
                            note="Bruttozinsen %s%% Depositenkasse %d"
                            % (nformat(interest_rate), book_date.year),
                        )
                    )
                    obj.append(
                        "Erzeuge Zins-Beteiligung Depositenkasse (%s, %s)"
                        % (nformat(interest["pay"][3]), nformat(interest_rate))
                    )
            except Exception as e:
                obj.append(str(e))
                ret.append({"info": f"FEHLER bei der Verarbeitung von {adr}", "objects": obj})
                ret.append({"info": "Verarbeitung abgebrochen. Keine Änderungen gespeichert."})
                return ret
            if obj:
                ret.append({"info": str(adr), "objects": obj})

        ## Commit transactions
        try:
            book.save()
            ret.append({"info": "GnuCash Transaktionen GESPEICHERT!"})
            for s in new_shares:
                s.save()
            ret.append({"info": "Zins-Beteiligungen GESPEICHERT!"})
        except Exception:
            ret.append({"info": "FEHLER BEIM SPEICHERN: {e}"})
    return ret


def add_interest_transaction(
    book,
    book_date,
    adr,
    name,
    interest_rate,
    total,
    tax,
    pay,
    acc_zins,
    acc_pay,
    acc_tax,
):
    info = f"Zinsgutschrift {name}: {nformat(total)}"
    if tax > 0:
        info += " (VSt. %s -> Netto %s)" % (
            nformat(tax),
            nformat(pay),
        )
    description = f"Zins {nformat(interest_rate)}%% auf {name} {book_date.year} {adr}"
    splits = [
        {"account": acc_zins, "amount": total},
        {"account": acc_pay, "amount": -pay},
    ]
    if tax > 0:
        splits.append({"account": acc_tax, "amount": -tax})
    book.add_split_transaction(splits, book_date, description, autosave=False)
    return info


def share_get_donations(address, year, enddate=None):
    period_start = datetime.date(year, 1, 1)
    if enddate:
        period_end = enddate + datetime.timedelta(days=1)
    else:
        period_end = datetime.date(year + 1, 1, 1)
    stype_donation = ShareType.objects.filter(name="Entwicklungsbeitrag").first()
    total = 0
    for share in (
        Share.objects.filter(name=address)
        .filter(share_type=stype_donation)
        .filter(state="bezahlt")
        .filter(date__gte=period_start)
        .filter(date__lt=period_end)
    ):
        total += share.quantity * share.value
    return total


def check_rental_shares_report():
    stype_share = ShareType.objects.filter(name="Anteilschein").first()  ## type index 0
    stype_loan_noint = ShareType.objects.filter(name="Darlehen zinslos").first()  ## type index 1
    stype_loan_int = ShareType.objects.filter(name="Darlehen verzinst").first()  ## type index 2
    stype_deposit = ShareType.objects.filter(name="Depositenkasse").first()  ## type index 3
    stype_loan_special = ShareType.objects.filter(name="Darlehen spezial").first()  ## type index 4

    ## Get shares per person, excluding shares that are explicitly attached to a contract
    shares = {}
    shares_contract = {}
    stype_share = ShareType.objects.filter(name="Anteilschein").first()
    for share in (
        get_active_shares()
    ):  # .filter(attached_to_contract=None): #.filter(share_type=stype_share):
        amount = 0
        amount_loan = 0
        amount_loan_5yr = 0
        amount_deposit = 0
        amount_loan_special = 0
        amount_loan_special_5yr = 0

        duedate_cutoff_5yr = datetime.date(datetime.datetime.now().year + 4, 12, 31)
        if share.date_due:
            duedate = share.date_due
        elif share.duration:
            duedate = share.date + relativedelta(years=share.duration)
        else:
            duedate = None
            if (
                share.share_type == stype_loan_noint
                or share.share_type == stype_loan_int
                or share.share_type == stype_loan_special
            ) and not share.is_interest_credit:
                raise Exception("ERROR: Loan without due date: %s" % share)
        if duedate and duedate > duedate_cutoff_5yr:
            # print("%s > %s" % (duedate, duedate_cutoff_5yr))
            flag_5yr = False
        else:
            # print("%s <= %s" % (duedate, duedate_cutoff_5yr))
            flag_5yr = True

        if share.share_type == stype_share:
            amount = share.quantity * share.value
        elif share.share_type == stype_loan_noint or share.share_type == stype_loan_int:
            amount_loan = share.quantity * share.value
            if flag_5yr:
                amount_loan_5yr = share.quantity * share.value
        elif share.share_type == stype_deposit:
            amount_deposit = share.quantity * share.value
        elif share.share_type == stype_loan_special:
            amount_loan_special = share.quantity * share.value
            if flag_5yr:
                amount_loan_special_5yr = share.quantity * share.value
        if share.attached_to_contract:
            ## Shares that are directly assigned to contract
            if share.share_type != stype_share:
                raise RuntimeError("Unsupported directly assigned share_type in check_shares()!")
            if share.attached_to_contract.id in shares_contract:
                shares_contract[share.attached_to_contract.id]["amount"] += amount
                shares_contract[share.attached_to_contract.id]["names"].append(
                    "%s(%s)" % (share.name, amount)
                )
            else:
                shares_contract[share.attached_to_contract.id] = {
                    "amount": amount,
                    "names": ["%s(%s)" % (share.name, amount)],
                }
        else:
            ## Automatically assigned
            if share.name.id in shares:
                shares[share.name.id]["amount"] += amount
                shares[share.name.id]["amount_loan"] += amount_loan
                shares[share.name.id]["amount_loan_5yr"] += amount_loan_5yr
                shares[share.name.id]["amount_deposit"] += amount_deposit
                shares[share.name.id]["amount_loan_special"] += amount_loan_special
                shares[share.name.id]["amount_loan_special_5yr"] += amount_loan_special_5yr
                if share.is_pension_fund:
                    shares[share.name.id]["is_pension_fund"] = True
            else:
                shares[share.name.id] = {
                    "adr": share.name,
                    "amount": amount,
                    "amount_loan": amount_loan,
                    "amount_loan_5yr": amount_loan_5yr,
                    "amount_deposit": amount_deposit,
                    "amount_loan_special": amount_loan_special,
                    "amount_loan_special_5yr": amount_loan_special_5yr,
                    "is_pension_fund": share.is_pension_fund,
                    "is_business": share.is_business,
                    "is_member": is_member(share.name),
                    "has_rental": False,
                }

    ## Assign shares to mandatory shares per rental object
    totals = {
        "rental_share_assigned": 0,
        "rental_share_directly_assigned": 0,
        "==1": 0,
        "rental_share_total": 0,
        "rental_share_reduction": 0,
        #'rental_share_required': 0,
        "rental_share_paid": 0,
        "rental_share_remain": 0,
        "rental_share_nocontract": 0,
        "==2": 0,
        "unused_share_renters": 0,
        "unused_share_directly_assigned": 0,
        "unused_share_nonrent": 0,
        "unused_share_nonrent_small": 0,
        "==3": 0,
        "total_loan_renters": 0,
        "total_loan_5yr_renters": 0,
        "total_deposit_renters": 0,
        "total_loan_special_renters": 0,
        "total_loan_special_5yr_renters": 0,
        "==4": 0,
        "total_loan_nonrenters": 0,
        "total_loan_5yr_nonrenters": 0,
        "total_deposit_nonrenters": 0,
        "total_loan_special_nonrenters": 0,
        "total_loan_special_5yr_nonrenters": 0,
        "==5": 0,
        "total_loan_nonmembers": 0,
        "total_loan_5yr_nonmembers": 0,
        "total_deposit_nonmembers": 0,
        "total_loan_special_nonmembers": 0,
        "total_loan_special_5yr_nonmembers": 0,
        "==6": 0,
        "loan_5yr_cutoff_date": duedate_cutoff_5yr,
        "==7": 0,
        "total_min_occ": 0,
        "total_occ": 0,
        "total_occ_child": 0,
    }
    totals_name = {
        "rental_share_assigned": "AS an Mietobjekte zugewiesen",
        "rental_share_directly_assigned": "   davon fix zugewiesen",
        "rental_share_total": "Total AS Soll",
        "rental_share_reduction": "AS Reduktionen",
        "rental_share_required": "AS benötigt",
        "rental_share_paid": "AS bezahlt",
        "rental_share_remain": "AS ausstehend",
        "rental_share_nocontract": "AS Leerstand",
        "unused_share_renters": "Nicht zugewiesene überschüssige AS",
        "unused_share_directly_assigned": "Überschüssige fix zugewiesene AS",
        "unused_share_nonrent": "Nicht zugewiesesne AS von Nicht-Mieter:innen",
        "unused_share_nonrent_small": "   davon kleine Beträge",
        "total_loan_renters": "Darlehen von Mieter:innen",
        "total_loan_5yr_renters": "   davon > 5 Jahre Laufzeit verbleibend",
        "total_deposit_renters": "Depositenkassenguthaben von Mieter:innen",
        "total_loan_special_renters": "Spezialdarlehen von Mieter:innen",
        "total_loan_special_5yr_renters": "   davon >5 Jahre Laufzeit verbleibend",
        "total_loan_nonrenters": "Darlehen von Mitgliedern (ohne Mieter:innen)",
        "total_loan_5yr_nonrenters": "   davon >5 Jahre Laufzeit verbleibend",
        "total_deposit_nonrenters": "Depositenkassenguthaben von Mitgliedern (ohne Mieter:innen)",
        "total_loan_special_nonrenters": "Spezialdarlehen von Mitgliedern (ohne Mieter:innen)",
        "total_loan_special_5yr_nonrenters": "   davon > 5 Jahre Laufzeit verbleibend",
        "total_loan_nonmembers": "Darlehen von Nicht-Mitgliedern",
        "total_loan_5yr_nonmembers": "   davon >5 Jahre Laufzeit verbleibend",
        "total_deposit_nonmembers": "Depositenkassenguthaben von Nicht-Mitgliedern",
        "total_loan_special_nonmembers": "Spezialdarlehen von Nicht-Mitgliedern",
        "total_loan_special_5yr_nonmembers": "   davon >5 Jahre Laufzeit verbleibend",
        "loan_5yr_cutoff_date": "Stichdatum für >5 Jahre Laufzeit",
        "total_min_occ": "Total Personen gem. Mindestbelegung",
        "total_occ": "Personen effektive Belegung",
        "total_occ_child": "   davon Kinder",
    }
    report = []
    item = collections.namedtuple(
        "ReportItem",
        "name, share_total, share_reduction, share_req, share_paid, share_remain, "
        "share_nocontract, min_occ, occ, occ_diff, occ_child, details",
        defaults=("", "", "", "", "", "", "", "", "", "", "", ""),
    )
    persons_counted = []
    share_reduction_remains_from_contract = {}
    for ru in RentalUnit.objects.filter(active=True).order_by("name"):
        if not ru.share and not ru.min_occupancy:
            continue
        details = []
        occupancy = 0
        occupancy_child = 0
        share_total = 0
        share_reduction = 0
        share_required = 0
        share_remain = 0
        share_nocontract = 0
        min_occupancy = 0
        if ru.share:
            share_total = ru.share
            share_required = share_total
            share_remain = share_total
        if ru.min_occupancy:
            min_occupancy = ru.min_occupancy
        no_contract = True
        for contract in get_active_contracts().filter(rental_units__id=ru.id):
            # print(" - Contract: %s" % contract)
            no_contract = False

            ## Share reduction
            available_reduction = share_reduction_remains_from_contract.get(
                contract.id, contract.share_reduction
            )
            if available_reduction:
                if available_reduction > share_total:
                    share_reduction = share_total
                    share_reduction_remains_from_contract[contract.id] = (
                        available_reduction - share_total
                    )
                else:
                    share_reduction = available_reduction
                    share_reduction_remains_from_contract[contract.id] = 0
                share_required -= share_reduction
                share_remain -= share_reduction

            ## First use explicitly assigned shares
            if contract.id in shares_contract:
                amount = shares_contract[contract.id]["amount"]
                if share_remain > 0 and amount > 0:
                    if amount <= share_remain:
                        transaction = amount
                    else:
                        transaction = share_remain
                    shares_contract[contract.id]["amount"] -= transaction
                    totals["rental_share_assigned"] += transaction
                    totals["rental_share_directly_assigned"] += transaction
                    share_remain -= transaction
                    details.append(
                        "%s (FIX: %s)"
                        % ("/".join(shares_contract[contract.id]["names"]), transaction)
                    )

            ## Now assign shares automatically
            for adr in contract.contractors.all():
                if ru.min_occupancy and adr.id not in persons_counted:
                    occupancy += 1
                    persons_counted.append(adr.id)
                if ru.share:
                    if adr.id not in shares:
                        continue
                    shares[adr.id]["has_rental"] = True
                    amount = shares[adr.id]["amount"]
                    if share_remain > 0 and amount > 0:
                        if amount <= share_remain:
                            transaction = amount
                        else:
                            transaction = share_remain
                        shares[adr.id]["amount"] -= transaction
                        totals["rental_share_assigned"] += transaction
                        share_remain -= transaction
                        details.append("%s (%s)" % (adr, transaction))
            if ru.min_occupancy:
                for child in contract.children.all():
                    if child.name.id not in persons_counted:
                        occupancy += 1
                        occupancy_child += 1
                        persons_counted.append(child.name.id)
        if no_contract:
            share_nocontract = share_total
            share_required = 0
            share_remain = 0
        report.append(
            item(
                name=str(ru),
                share_total=share_total,
                share_reduction=share_reduction,
                share_req=share_required,
                share_paid=share_required - share_remain,
                share_remain=share_remain,
                share_nocontract=share_nocontract,
                details="/".join(details),
                min_occ=min_occupancy,
                occ=occupancy,
                occ_diff=occupancy - min_occupancy,
                occ_child=occupancy_child,
            )
        )
        totals["rental_share_total"] += share_total
        totals["rental_share_reduction"] += share_reduction
        # totals['rental_share_required'] += share_required
        totals["rental_share_paid"] += share_required - share_remain
        totals["rental_share_remain"] += share_remain
        totals["rental_share_nocontract"] += share_nocontract
        totals["total_min_occ"] += min_occupancy
        totals["total_occ"] += occupancy
        totals["total_occ_child"] += occupancy_child

    ## Remaining shares_contract
    for sid in shares_contract:
        if shares_contract[sid]["amount"] > 0:
            totals["unused_share_directly_assigned"] += shares_contract[sid]["amount"]

    ## Remaining shares: members with rentals, members without rentals >1000, <1000
    for sid in shares:
        if shares[sid]["amount"] > 0:
            if shares[sid]["has_rental"]:
                totals["unused_share_renters"] += shares[sid]["amount"]
            else:
                if shares[sid]["amount"] > 1000:
                    totals["unused_share_nonrent"] += shares[sid]["amount"]
                else:
                    totals["unused_share_nonrent_small"] += shares[sid]["amount"]
            shares[sid]["amount"] = 0
        if shares[sid]["has_rental"]:
            totals["total_loan_renters"] += shares[sid]["amount_loan"]
            totals["total_loan_5yr_renters"] += shares[sid]["amount_loan_5yr"]
            totals["total_deposit_renters"] += shares[sid]["amount_deposit"]
            totals["total_loan_special_renters"] += shares[sid]["amount_loan_special"]
            totals["total_loan_special_5yr_renters"] += shares[sid]["amount_loan_special_5yr"]
        elif shares[sid]["is_member"]:
            totals["total_loan_nonrenters"] += shares[sid]["amount_loan"]
            totals["total_loan_5yr_nonrenters"] += shares[sid]["amount_loan_5yr"]
            totals["total_deposit_nonrenters"] += shares[sid]["amount_deposit"]
            totals["total_loan_special_nonrenters"] += shares[sid]["amount_loan_special"]
            totals["total_loan_special_5yr_nonrenters"] += shares[sid]["amount_loan_special_5yr"]
        else:
            totals["total_loan_nonmembers"] += shares[sid]["amount_loan"]
            totals["total_loan_5yr_nonmembers"] += shares[sid]["amount_loan_5yr"]
            totals["total_deposit_nonmembers"] += shares[sid]["amount_deposit"]
            totals["total_loan_special_nonmembers"] += shares[sid]["amount_loan_special"]
            totals["total_loan_special_5yr_nonmembers"] += shares[sid]["amount_loan_special_5yr"]

    report.append(item(name="", share_total=""))
    report.append(item(name="", share_total=""))
    for name in totals:
        if name.startswith("=="):
            report.append(item(name="", share_total=""))
        else:
            report.append(item(name=totals_name[name], share_total=totals[name]))

    return report
