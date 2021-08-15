#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from google.protobuf.json_format import MessageToJson
import lightning_pb2 as ln
import lightning_pb2_grpc as lnrpc
import grpc
import codecs
import binascii
import os
import logging
import subprocess
import json
import base64
import pycurl

# Definitions
TLVS = ["7629171", "7629169", "133773310"]
# TLVS_TO_EXTRACT = [["action", "boost"], ["podcast", "Analytical"]]
# TLVS_TO_EXTRACT = [["action", "boost"]]
TLVS_TO_EXTRACT = [["message", ""]]
DEFAULT_NUM_MAX_INVOICES = 10000
DEFAULT_INDEX_OFFSET = 0
REMEMBER_LAST_INDEX = True
BOOSTAGRAM_FIELDS_TO_PUSH = ["app_name", "podcast", "episode", "message", "sender_name"]

# Pushover Notifications
PUSHOVER_ENABLE = True
PUSHOVER_USER_TOKEN = "<TOKEN HERE>"
PUSHOVER_API_TOKEN = "<TOKEN HERE>"

def JSONtoString(JSONObject):
    message_string = 'Boost-A-Gram recieved, '
    for key, value in JSONObject.items():
        if key in BOOSTAGRAM_FIELDS_TO_PUSH:
            message_string += (key + ' = ' + str(value) + ', ')
    message_string = message_string[:-2]
    return message_string

# End JSONtoString

def main():
    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

    # Lnd admin macaroon is at ~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon on Linux
    with open(os.path.expanduser('~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon'), 'rb') as f:
        macaroon_bytes = f.read()
        macaroon = codecs.encode(macaroon_bytes, 'hex')

    # Lnd cert is at ~/.lnd/tls.cert on Linux
    cert = open(os.path.expanduser('~/.lnd/tls.cert'), 'rb').read()
    creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel('localhost:10009', creds)
    stub = lnrpc.LightningStub(channel)

    if REMEMBER_LAST_INDEX:
        # Open and read in previous index position
        invoicefile = os.path.expanduser('lastinvoice.db')
        if os.path.exists(invoicefile):
            with open(invoicefile) as invoicefiledata:
                invoicedataraw = invoicefiledata.readlines()
                indexarray = [i.strip() for i in invoicedataraw]
                indexoffset = int(indexarray[0])

        request = ln.ListInvoiceRequest(
            pending_only=False,
            index_offset=indexoffset,
            num_max_invoices=DEFAULT_NUM_MAX_INVOICES,
            reversed=False,
        )
        invoice_database_index = indexoffset
    else:
        request = ln.ListInvoiceRequest(
            pending_only=False,
            index_offset=DEFAULT_INDEX_OFFSET,
            num_max_invoices=DEFAULT_NUM_MAX_INVOICES,
            reversed=False,
        )
        invoice_database_index = DEFAULT_INDEX_OFFSET

    # Retrieve and display the wallet balance
    invoice_list = stub.ListInvoices(request, metadata=[('macaroon', macaroon)])
    serialized_invoice_list = MessageToJson(invoice_list)
    dictionary_invoice_list = json.loads(serialized_invoice_list)
    if len(dictionary_invoice_list):
        for invoice in dictionary_invoice_list['invoices']:
            if "htlcs" in invoice and "isKeysend" in invoice:
                for htlc in invoice['htlcs']:
                    if "customRecords" in htlc:
                        for tlv_index, tlv_payload in htlc['customRecords'].items():
                            if tlv_index in TLVS:
                                tlv_payload_UTF8 = base64.b64decode(tlv_payload).decode('utf8')
                                pushover_message = ''
                                try:
                                    tlv_payload_decoded = json.loads(tlv_payload_UTF8)
                                    for key, value in TLVS_TO_EXTRACT:
                                        if tlv_payload_decoded[key] in value:
                                            pushover_message = JSONtoString(tlv_payload_decoded)
                                        elif tlv_payload_decoded[key] and not value:
                                            pushover_message = JSONtoString(tlv_payload_decoded)
                                except:
                                    pass

                                if PUSHOVER_ENABLE and pushover_message:
                                    crl = pycurl.Curl()
                                    crl.setopt(crl.URL, 'https://api.pushover.net/1/messages.json')
                                    crl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json' , 'Accept: application/json'])
                                    data = json.dumps({"token": PUSHOVER_API_TOKEN, "user": PUSHOVER_USER_TOKEN, "title": "RSS Notifier", "message": pushover_message })
                                    crl.setopt(pycurl.POST, 1)
                                    crl.setopt(pycurl.POSTFIELDS, data)
                                    crl.perform()
                                    crl.close()

            invoice_database_index += 1
# End For Loop

# Boilerplate for flagging current database index for reduce seek times in future TBD
    # Check for new Invoices

        # Write all previous and current Invoices
        # Open and read in previous index position
        invoicefile = os.path.expanduser('lastinvoice.db')
        if os.path.exists(invoicefile):
            with open(invoicefile, 'w') as invoicefiledata:
                invoicefiledata.write(str(invoice_database_index))

# End

if __name__ == "__main__":
    main()
# End
