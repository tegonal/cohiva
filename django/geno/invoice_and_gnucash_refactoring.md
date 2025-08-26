# Intro

This files collects information regarding refactoring of invoicing and gnucash interface code.

# Inivoice creation

## Level 0: Direct Invoice() object creation

gnucash.py:

    add_invoice_obj() ==> Creates Invoice and GNC-transaction
    create_invoices() ==> Creates placeholder Invoices for linked billing contracts (no GNC-transaction)

## Level 1: Callers of `add_invoice_obj()`

gnucash.py:

    process_sepa_transactions()
    add_payment()
    add_invoice()

## Level 2a: Callers of `add_invoice()`

    api_views.py: QRBill => post() => do_accounting()  (NK Akonto QR-Bill)
    views.py:     invoice_manual()
    gnucash.py:   create_invoices()
    invoice.py:   InvoiceCreator => create_and_send() > create_invoice_object()

## Level 2b: Callers of `add_payment()`

    views.py: transaction_invoce() [TransactionFormInvoice]    => gnucash.py: pay_invoice()
	      transaction()        [TransactionForm]           => gnucash.py: process_transaction()
	      transaction_upload() [TransactionUploadFileForm] => gnucash.py: process_transaction()

## Level 2c: Callers of `process_sepa_transactions()`

    views.py: transaction_upload() [TransactionUploadFileForm]

## Level 3: Users of InvoiceCreator
 
    views.py: TODO???: invoice_manual()  ???
    
    Warmbächli website/views.py: holliger()  [Schlüssel-Formular]  
