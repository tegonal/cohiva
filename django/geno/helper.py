import re


def build_account(account, building=None, rental_units=None):
    if rental_units and rental_units > 0:
        building = rental_units.getFirst().building
    if building and building.postfix:
        postfix = "%03d" % building.accounting_postfix
        return re.sub(r"(\d+)$", r"\1%s" % building.postfix, account)
    else:
        return account
