#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Project: RPI4 Alarm
# Source : modem.py
# Date   : Tue Nov  8 09:59:30 AM CET 2022
# Author : Andrea Bravetti
# ---------------------------------------------------------------

# ModemManager project:
# https://gitlab.freedesktop.org/mobile-broadband/ModemManager/

import subprocess
import json

from utility import *

def fix_text(string: str):
    if len(string) > 160:
        return (string[:157]+"...").replace("'", " ")
    return string.replace("'", " ")

def list_modem():
    # mmcli -J -L
    # {
    #     "modem-list": [
    #         "/org/freedesktop/ModemManager1/Modem/0"
    #     ]
    # }
    result = subprocess.run(['mmcli', '-J', '-L'], stdout=subprocess.PIPE)
    return json.loads(result.stdout)["modem-list"] if result.returncode==0 else [], result.returncode

def list_sms(modem: str):
    # mmcli -J -m /org/freedesktop/ModemManager1/Modem/0 --messaging-list-sms
    # {
    #     "modem.messaging.sms": [
    #         "/org/freedesktop/ModemManager1/SMS/7"
    #     ]
    # }
    result = subprocess.run(['mmcli', '-J', '-m', modem, '--messaging-list-sms'], stdout=subprocess.PIPE)
    return json.loads(result.stdout)["modem.messaging.sms"] if result.returncode==0 else [], result.returncode

def read_sms(modem: str, sms: str):
    # mmcli -J -m /org/freedesktop/ModemManager1/Modem/0 --sms /org/freedesktop/ModemManager1/SMS/7
    # {
    #     "sms": {
    #         "content": {
    #             "data": "--",
    #             "number": "+000000000000",
    #             "text": "Prova"
    #         },
    #         "dbus-path": "/org/freedesktop/ModemManager1/SMS/7",
    #         "properties": {
    #             "class": "--",
    #             "delivery-report": "--",
    #             "delivery-state": "--",
    #             "discharge-timestamp": "--",
    #             "message-reference": "--",
    #             "pdu-type": "deliver",
    #             "service-category": "--",
    #             "smsc": "+000000000000",
    #             "state": "received",
    #             "storage": "sm",
    #             "teleservice-id": "--",
    #             "timestamp": "2022-11-07T17:12:36+01:00",
    #             "validity": "--"
    #         }
    #     }
    # }
    result = subprocess.run(['mmcli', '-J', '-m', modem, '--sms', sms], stdout=subprocess.PIPE)
    return json.loads(result.stdout)["sms"] if result.returncode==0 else {}, result.returncode

def send_sms(modem: str, text: str, number: str):
    # mmcli -m /org/freedesktop/ModemManager1/Modem/0 --messaging-create-sms="text='Hello world',number='+0000000000000'"
    # Successfully created new SMS: /org/freedesktop/ModemManager1/SMS/9
    # mmcli -m /org/freedesktop/ModemManager1/Modem/0 -s /org/freedesktop/ModemManager1/SMS/9 --send
    # successfully sent the SMS
    # FIXME:
    # https://gitlab.freedesktop.org/mobile-broadband/ModemManager/-/issues/657
    result = subprocess.run(['mmcli', '-m', modem, '''--messaging-create-sms=text="%s",number="%s"''' % (fix_text(text), number)], stdout=subprocess.PIPE)
    debug("arg:\n", result.args, "out:\n", result.stdout, "err:\n", result.stderr)
    if result.returncode == 0:
        sms = result.stdout.decode("utf-8").split("\n")[0].split(" ")[4]
        result = subprocess.run(['mmcli', '-m', modem, '-s', sms], stdout=subprocess.PIPE)
        debug("arg:\n%s\nout:\n%s\nerr:\n%s\n" % (result.args, result.stdout, result.stderr))
        delete_sms(modem, sms)
    return result.returncode==0, result.returncode

def delete_sms(modem: str, sms: str):
    # mmcli -m 0 --messaging-delete-sms=7
    # successfully deleted SMS from modem
    result = subprocess.run(['mmcli', '-m', modem, '--messaging-delete-sms=%s' % sms], stdout=subprocess.PIPE)
    debug("arg:\n", result.args, "out:\n", result.stdout, "err:\n", result.stderr)
    return result.returncode==0, result.returncode
