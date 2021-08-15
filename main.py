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
CACHELIMIT = 10000
TLVS = ["7629171", "7629169", "133773310"]
# TLVS_TO_EXTRACT = [["action", "boost"], ["podcast", "Analytical"]]
# TLVS_TO_EXTRACT = [["action", "boost"]]
TLVS_TO_EXTRACT = [["message", ""]]

# Pushover Notifications
PUSHOVER_ENABLE = 0
#PUSHOVER_USER_TOKEN = "<TOKEN HERE>"
#PUSHOVER_API_TOKEN = "<TOKEN HERE>"
PUSHOVER_USER_TOKEN = "<TOKEN HERE>"
PUSHOVER_API_TOKEN = "<TOKEN HERE>"


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
    request = ln.ListInvoiceRequest(
        pending_only=False,
        index_offset=0,
        num_max_invoices=10000,
        reversed=False,
    )

    # Retrieve and display the wallet balance
    invoice_list = stub.ListInvoices(request, metadata=[('macaroon', macaroon)])
    serialized_invoice_list = MessageToJson(invoice_list)
    dictionary_invoice_list = json.loads(serialized_invoice_list)
    invoice_database_index = 0

    for invoice in dictionary_invoice_list['invoices']:
        value_for_value = False
        creationDate = ""
#        if "creationDate" in invoice:
#            creationDate = invoice['creationDate']
        keysend = False
        if "isKeysend" in invoice:
            keysend = True
        if "htlcs" in invoice and keysend:
            for htlc in invoice['htlcs']:
                if "customRecords" in htlc:
                    for tlv_index, tlv_payload in htlc['customRecords'].items():
                        if tlv_index in TLVS:
                            tlv_payload_decoded = ''
                            tlv_payload_UTF8 = base64.b64decode(tlv_payload).decode('utf8')
                            try:
                                tlv_payload_decoded = json.loads(tlv_payload_UTF8)
                                for key, value in TLVS_TO_EXTRACT:
                                    if tlv_payload_decoded[key] in value:
                                        print(tlv_payload_decoded)
                                        if PUSHOVER_ENABLE:
                                            crl = pycurl.Curl()
                                            crl.setopt(crl.URL, 'https://api.pushover.net/1/messages.json')
                                            crl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json' , 'Accept: application/json'])
                                            data = json.dumps({"token": PUSHOVER_API_TOKEN, "user": PUSHOVER_USER_TOKEN, "title": "RSS Notifier", "message": thefeedentry.get("title", "") + " Now Live"})
                                            crl.setopt(pycurl.POST, 1)
                                            crl.setopt(pycurl.POSTFIELDS, data)
                                            crl.perform()
                                            crl.close()
 
                                   elif tlv_payload_decoded[key] and not value:
                                        print(tlv_payload_decoded)
                            except:
                                pass

        invoice_database_index += 1
# End For Loop

# Boilerplate for flagging current database index for reduce seek times in future TBD
    # Open and read in all previously found Invoices
    cachefile = os.path.expanduser('~/invoicelist.db')
    if os.path.exists(cachefile):
        with open(cachefile) as dbdsc:
            dbfromfile = dbdsc.readlines()
        dblist = [i.strip() for i in dbfromfile]
        dbfeed = deque(dblist, CACHELIMIT)
    else:
        dbfeed = deque([], CACHELIMIT)

    # Check for new Invoices

    # Write all previous and current Invoices
    with open(cachefile, 'w') as dbdsc:
        dbdsc.writelines((''.join([i, os.linesep]) for i in dbfeed))

# End

if __name__ == "__main__":
    main()
# End