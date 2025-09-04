#!/usr/bin/env python3

import email
import fcntl
import json
import logging
import os
import random
import smtplib
import socket
import sys
from datetime import datetime
from signal import SIGINT, signal

import PySimpleGUI as sg
import requests
import settings
from depot8_migration import import_accounts

PRODUCTION = False

if PRODUCTION:
    SETTINGS_KEY = "PRODUCTION"
else:
    SETTINGS_KEY = "TEST"

print(f"Running in {SETTINGS_KEY} mode.")
logging.basicConfig(
    filename=settings.POS_SETTINGS[SETTINGS_KEY]["LOGFILE"],
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(module)s/%(funcName)s:%(lineno)d] %(message)s",
)


def check_age(ts, max_age):
    if not ts:
        return True
    age = datetime.now() - ts
    return age.total_seconds() >= max_age


class PosTerminal:
    cachefilename = settings.POS_SETTINGS[SETTINGS_KEY]["CACHEFILE"]
    api_base_url = settings.POS_SETTINGS[SETTINGS_KEY]["API_BASE_URL"]
    api_secret = settings.POS_SETTINGS[SETTINGS_KEY]["API_SECRET"]
    BAR_MAX = 200
    maxminus = 100
    local_cache_max_age = (
        10 * 60
    )  ## Time in seconds after which a sync with the remote datasource is forced.
    sync_error_notify_after = (
        0.5 * 60
    )  ## Time in seconds after which a persistent remote sync error is reported.
    sync_error_notify_period = (
        2 * 60
    )  ## Time in seconds after which a persistent remote sync error is reported again.
    # timezone = pytz.timezone('Europe/Zurich')
    lock_file = "/tmp/instance_depot8_posterminal.lock"
    vendor = "Depot8"

    def __init__(self):
        self.ensure_unique_instance()
        logging.info("PosTerminal starting up.")
        signal(SIGINT, self.signal_handler)
        self.hostname = socket.gethostname()
        self.boot_time = datetime.now().astimezone()
        self.transaction_id_prefix = (
            f"{self.hostname}_{self.boot_time.strftime('%Y%m%d%H%M%S%f%z')}"
        )
        self.transaction_id_counter = 0
        self.last_sync_ts = datetime(1970, 1, 1)
        self.sync_error_ts = None
        self.last_sync_error_notify_ts = None
        self.sync_error = None
        self.load_local_cache()
        self.init_ui()
        self.sync_remote_data()

    def signal_handler(self, signal_received, frame):
        self.admin_notify("Depot8 POS exited. (SIGINT or CTRL-C)")
        self.window.close()
        sys.exit(0)

    def ensure_unique_instance(self):
        self.lock_file_pointer = os.open(self.lock_file, os.O_WRONLY | os.O_CREAT)
        try:
            fcntl.lockf(self.lock_file_pointer, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            sg.theme("DarkBlue13")
            font = ("Helvetia", 20)
            layout = [
                [
                    sg.Text(
                        "Es läuft bereits eine andere Instanz des Programms.",
                        font=font,
                        justification="c",
                    )
                ],
                [sg.Button("OK")],
            ]
            window = sg.Window("Fehler", layout)
            event, values = window.read()
            window.close()
            sys.exit()

    def load_local_cache(self):
        try:
            with open(self.cachefilename) as input_file:
                logging.info("Reading local cache from %s" % self.cachefilename)
                self.data = json.load(input_file)
        except FileNotFoundError:
            logging.warning(
                "Local cache file %s not found. Starting with no data." % self.cachefilename
            )
            self.data = {
                "accounts": {
                    "011": {"balance": 150.0},
                },
                "transactions": [],
            }

    def save_local_cache(self):
        logging.debug("Saving local cache to %s" % self.cachefilename)
        json_object = json.dumps(self.data)
        with open(self.cachefilename, "w") as outfile:
            outfile.write(json_object)

    def admin_notify(self, text):
        msg = email.message.EmailMessage()
        msg.set_content(text)
        msg["Subject"] = f"Depot8 POS notification [{self.hostname}]"
        msg["From"] = "admin@warmbaechli.ch"
        msg["To"] = "admin@warmbaechli.ch"
        msg["Date"] = email.utils.formatdate(localtime=True)
        s = smtplib.SMTP("mail.websource.ch")
        s.send_message(msg)
        s.quit()

    def sync_remote_data(self):
        logging.info("Sync with remote database.")
        self.sync_error = None
        self.push_transactions()
        self.get_remote_accounts()
        self.save_local_cache()
        if self.sync_error:
            if self.sync_error_ts:
                if check_age(self.sync_error_ts, self.sync_error_notify_after) and check_age(
                    self.last_sync_error_notify_ts, self.sync_error_notify_period
                ):
                    self.admin_notify(f"Persistent sync error: {self.sync_error}")
                    self.last_sync_error_notify_ts = datetime.now()
            else:
                self.sync_error_ts = datetime.now()
        else:
            ## Clear error ts
            self.sync_error_ts = None
            self.last_sync_ts = datetime.now()

    def api_request(self, url_path, data=None, method="get", timeout=2):
        if data is None:
            data = {}
        request_data = data.copy()
        request_data["vendor"] = self.vendor
        request_data["secret"] = self.api_secret
        url = f"{self.api_base_url}{url_path}"
        if method == "get":
            response = requests.get(url, json=request_data, timeout=timeout)
        elif method == "post":
            response = requests.post(url, json=request_data, timeout=timeout)
        else:
            raise Exception(f"Invalid method: {method}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Invalid status code: %s" % response.status_code)

    def get_remote_accounts(self):
        try:
            api_path = "/credit_accounting/pos/accounts/"
            response = self.api_request(api_path)
            if response.get("status") != "OK":
                raise Exception(
                    f"API call not OK: {response.get('status')} "
                    f"({response.get('error', 'unknown error')})"
                )
            self.data["accounts"] = response.get("accounts")
        except Exception as e:
            if not self.sync_error:
                self.sync_error = "Could not get remote account information: %s" % e
            logging.warning("Could not get remote account information: %s" % e)

    def push_transactions(self):
        api_path = "/credit_accounting/pos/transaction/"
        failed_transactions = []
        skip_remaining = False
        notification = []
        for transaction in self.data["transactions"]:
            try:
                if skip_remaining:
                    raise Exception("Skipped because of too many errors.")
                response = self.api_request(api_path, data=transaction, method="post")
                if response.get("status") == "Duplicate":
                    logging.warning(
                        f"Ignoring transaction: Transaction with ID {transaction['id']} exists "
                        f"already. [{transaction['account']}/{transaction['amount']}/"
                        f"{transaction['date']} - {transaction['note']}]"
                    )
                    notification.append(
                        f"Ignoring transaction: Transaction with ID {transaction['id']} exists "
                        f"already. [{transaction['account']}/{transaction['amount']}/"
                        f"{transaction['date']} - {transaction['note']}]"
                    )
                elif response.get("status") != "OK":
                    raise Exception(
                        f"API call not OK: {response.get('status')} "
                        f"({response.get('error', 'unknown error')})"
                    )
            except Exception as e:
                skip_remaining = True
                if not self.sync_error:
                    self.sync_error = "Could not push transation %s/%s [%s] to remote db: %s" % (
                        transaction["account"],
                        transaction["amount"],
                        transaction["date"],
                        e,
                    )
                logging.warning(
                    "Could not push transation %s/%s [%s] to remote db: %s"
                    % (transaction["account"], transaction["amount"], transaction["date"], e)
                )
                notification.append(
                    "Could not push transation %s/%s [%s] to remote db: %s"
                    % (transaction["account"], transaction["amount"], transaction["date"], e)
                )
                failed_transactions.append(transaction)
        self.data["transactions"] = failed_transactions
        if notification:
            self.admin_notify("\n".join(notification))

    def is_valid_username(self, username):
        return username in self.data["accounts"]

    def get_balance(self, username):
        if self.is_valid_username(username):
            return self.data["accounts"][username]["balance"]
        else:
            return None

    def add_transaction(self, name, username, betrag, kommentar, transaction_id=None):
        if not transaction_id:
            self.transaction_id_counter += 1
            random_nr = int(random.random() * 1000000)
            transaction_id = (
                f"{self.transaction_id_prefix}_{self.transaction_id_counter}_{random_nr}"
            )
        logging.debug(
            "Adding transaction %s for user %s CHF %s (Note: %s) [%s]",
            name,
            username,
            betrag,
            kommentar,
            transaction_id,
        )
        self.data["transactions"].append(
            {
                "name": name,
                "account": username,
                "amount": betrag,
                "note": kommentar,
                "date": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S.%f%z"),
                "id": transaction_id,
            }
        )
        self.data["accounts"][username]["balance"] += betrag
        self.sync_remote_data()

    def create_account(self, name, pin, transactions=None):
        if transactions is None:
            transactions = []
        api_path = "/credit_accounting/pos/account/"
        try:
            response = self.api_request(
                api_path,
                data={"name": name, "pin": pin, "transactions": transactions},
                method="post",
                timeout=180,
            )
            if response.get("status") == "Duplicate":
                logging.warning(f"Account exists already: {name}/{pin}.")
            elif response.get("status") != "OK":
                raise Exception(
                    f"API call not OK: {response.get('status')} "
                    f"({response.get('error', 'unknown error')})"
                )
            logging.info(
                f"Created account {name}/{pin} (ID {response.get('account_id')}) with "
                f"transaction counts: {response.get('transaction_count')}."
            )
            return response.get("account_id")
        except Exception as e:
            logging.error(f"Could not create account {name}/{pin}: {e}")
        return None

    def migrate_data(self):
        for account in import_accounts():
            import_transactions = []
            for deposit in account.deposits:
                import_transactions.append(
                    {
                        "name": f"Einzahlung {self.vendor}",
                        "account": account.pin,
                        "amount": deposit.amount,
                        "note": f"Import {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "date": deposit.date.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
                        "id": deposit.id,
                    }
                )
            for purchase in account.purchases:
                import_transactions.append(
                    {
                        "name": f"Einkauf {self.vendor}",
                        "account": account.pin,
                        "amount": purchase.amount,
                        "note": f"Import {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "date": purchase.date.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
                        "id": purchase.id,
                    }
                )
            account.id = self.create_account(
                name=account.name, pin=account.pin, transactions=import_transactions
            )
            if account.id:
                print(
                    f" - Imported account {account.name} with "
                    f"{len(import_transactions)} transactions."
                )
            else:
                print(
                    f" - Error while importing account {account.name} with "
                    f"{len(import_transactions)} transactions."
                )
                logging.error(f"Could not migrate account {account.name}.")

    def init_ui(self):
        sg.theme("DarkBlue13")
        font = ("Helvetia", 20)

        col1 = [
            [sg.Text("Wohnungsnummer/PIN", font=font)],
            [sg.Text("Guthaben", font=font)],
            [sg.Text("Betrag", font=font)],
            [sg.Text("Notiz (optional)", font=font)],
            [sg.Text("Neues Guthaben", font=font, key="-neuesguthaben-", visible=False)],
        ]

        col2 = [
            [sg.Input(key="-NR-", enable_events=True, font=font, size=10)],
            [sg.Text("--", key="-Saldo-", font=font, justification="r", size=10)],
            [sg.Input(key="-BETRAG-", enable_events=True, font=font, size=10, justification="r")],
            [sg.Input(key="-KOMMENTAR-", enable_events=True, font=font, size=10)],
            [
                sg.Text(
                    "--", key="-SaldoNeu-", font=font, justification="r", size=10, visible=False
                )
            ],
        ]

        layout = [
            [sg.Column(col1), sg.Column(col2)],
            [
                sg.Column(
                    [[sg.Button("Zurueck", visible=False, font=font, bind_return_key=False)]]
                ),
                sg.Column(
                    [[sg.Button("Einkaufen", disabled=True, font=font, bind_return_key=False)]],
                    justification="c",
                    pad=(50, 50),
                ),
            ],
            [
                sg.ProgressBar(
                    self.BAR_MAX, visible=False, orientation="h", size=(40, 20), key="-PROG-"
                )
            ],
            [sg.Text("", key="-Message-", font=font)],
        ]

        if PRODUCTION:
            self.window = sg.Window(
                title="depot 8",
                layout=layout,
                size=(1280, 1040),
                margins=(300, 300),
                element_justification="c",
            )
            self.window.Finalize()
            self.window.Maximize()
        else:
            self.window = sg.Window(
                title="depot 8 TEST",
                layout=layout,
                size=(1800, 1200),
                margins=(300, 300),
                element_justification="c",
            )
            self.window.Finalize()

    def print_workbook(self):
        for row in self.datawb.active.rows:
            print([c.value for c in row])

    def run(self):
        self.admin_notify("Depot8 POS started.")
        # self.migrate_data()
        while True:
            event, values = self.window.read(timeout=10 * 1000)
            # print(event, values)

            if event == sg.WIN_CLOSED:
                break

            if event == sg.TIMEOUT_KEY:
                if self.sync_error or check_age(self.last_sync_ts, self.local_cache_max_age):
                    self.sync_remote_data()
                continue

            self.window["-Message-"].update(value="")

            uname = str(values["-NR-"])
            if event == "-NR-":
                if self.is_valid_username(uname):
                    self.window["-Saldo-"].update(value=f"{self.get_balance(uname):.2f}")
                else:
                    self.window["-Saldo-"].update(value="--")

            if (
                event == "-BETRAG-"
                and values["-BETRAG-"]
                and values["-BETRAG-"][-1] not in ("0123456789.")
            ):
                self.window["-BETRAG-"].update(values["-BETRAG-"][:-1])

            if (
                event == "-BETRAG-"
                and len(values["-BETRAG-"]) > 3
                and values["-BETRAG-"][-4] == "."
            ):
                self.window["-BETRAG-"].update(values["-BETRAG-"][:-1])

            try:
                betrag = float(values["-BETRAG-"])
            except ValueError:
                betrag = 0
            kommentar = str(values["-KOMMENTAR-"])

            # only activate the Einkaufen button for valid usernames and balances
            if (
                self.is_valid_username(uname)
                and betrag <= self.get_balance(uname) + self.maxminus
                and betrag > 0
            ):
                self.window["Einkaufen"].update(disabled=False)
            else:
                self.window["Einkaufen"].update(disabled=True)

            if event == "Einkaufen":
                self.window["-NR-"].update(disabled=True)
                self.window["-BETRAG-"].update(disabled=True)
                self.window["-KOMMENTAR-"].update(disabled=True)
                self.window["Einkaufen"].update(disabled=True)
                self.window["Zurueck"].update(visible=True)
                self.window["-PROG-"].update(0, visible=True)
                self.window["-neuesguthaben-"].update(visible=True)
                self.window["-SaldoNeu-"].update(
                    f"{self.get_balance(uname) - betrag:.2f}", visible=True
                )

                success = True
                for i in range(self.BAR_MAX):
                    # check to see if the cancel button was clicked and exit loop if clicked
                    event, values = self.window.read(timeout=10)
                    self.window["-PROG-"].update(i + 1)
                    if event == "Zurueck" or event == sg.WIN_CLOSED:
                        success = False
                        break
                if success:
                    self.add_transaction(
                        name=f"Einkauf {self.vendor}",
                        username=uname,
                        betrag=-1 * betrag,
                        kommentar=kommentar,
                    )
                    self.window["-Message-"].update(value="Merci vielmals!")

                self.window["-PROG-"].update(0, visible=False)
                self.window["Zurueck"].update(visible=False)
                self.window["-BETRAG-"].update(value="", disabled=False)
                self.window["-KOMMENTAR-"].update(value="", disabled=False)
                self.window["-NR-"].update(value="", disabled=False)
                self.window["Einkaufen"].update(disabled=True)
                self.window["-Saldo-"].update(value="--")
                self.window["-neuesguthaben-"].update(visible=False)
                self.window["-SaldoNeu-"].update(visible=False)

                self.window["-NR-"].set_focus()

        self.admin_notify("Depot8 POS exited.")
        self.window.close()


if __name__ == "__main__":
    pos = PosTerminal()
    if len(sys.argv) > 1 and sys.argv[1] == "import":
        ## Import data
        print("Importing data.")
        pos.migrate_data()
        pos.sync_remote_data()
    else:
        ## Start terminal
        pos.run()

# EOF
