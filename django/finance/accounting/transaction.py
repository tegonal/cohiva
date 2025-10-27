class Transaction:
    def __init__(self, amount, date, description, debit_account, credit_account):
        self.amount = amount
        self.date = date
        self.description = description
        self.debit_account = debit_account
        self.credit_account = credit_account

    def __repr__(self):
        return f"Transaction(amount={self.amount}, date={self.date}, description='{self.description}')"
