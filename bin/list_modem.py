#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Project: RPI4 Alarm
# Source : list_modem.py
# Date   : Tue Nov  8 09:59:30 AM CET 2022
# Author : Andrea Bravetti
# ---------------------------------------------------------------

import os
import time
import json
import tempfile
import traceback
import subprocess
from datetime import datetime

from modem import list_modem, list_sms, read_sms, send_sms, delete_sms
from utility import debug
from upsplus import input_voltage, battery_percentage
from sendmail import send_mail_with_auth

import config

HELP_MSG="RPI4 Alarm available commands: STOP, RESTART, POWEROFF, REBOOT, MOTION [STOP|START|RESTART], BATTERY, PHOTO, VIDEO [s], HELP"

# Patch tempfile:
class _HexRandomNameSequence(tempfile._RandomNameSequence):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

tempfile._name_sequence = _HexRandomNameSequence()

# Create the log directory if it does not exists
os.makedirs(config.LOG_PATH, exist_ok=True)

# Initial starting message
debug("Starting RPI4 Alarm")
modem_list, modem_error = list_modem()
for modem in modem_list:
    print("Found modem " + modem)
    sms_list, sms_error = list_sms(modem)
    if len(sms_list) > 0:
        print("Found %s pending messages" % len(sms_list))

