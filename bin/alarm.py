#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Project: RPI4 Alarm
# Source : modem.py
# Date   : Tue Nov  8 09:59:30 AM CET 2022
# Author : Andrea Bravetti
# ---------------------------------------------------------------

import os
import time
import tempfile
from modem import *
import config

HELP_MSG="RPI4 Alarm available commands: SHUTDOWN, REBOOT, MOTION [ON|OFF], BATTERY, PHOTO, VIDEO [s], HELP"

def debug(msg):
    if config.DEBUG:
        print(msg)

# Create the log directory if it does not exists
os.makedirs(config.LOG_PATH, exist_ok=True)

# Initial starting message
debug("Starting RPI4 Alarm")
modem_list, modem_error = list_modem()
for modem in modem_list:
    debug("Found modem " + modem)
    sent, ret = send_sms(modem, "Starting RPI4 Alarm", config.TRUSTED_PHONE)
    debug("Sent initial message: %s, %s" % (sent, ret))

# Main loop
while True:
    modem_list, modem_error = list_modem()
    for modem in modem_list:
        sms_list, sms_error = list_sms(modem)
        for sms in sms_list:
            sms_body, read_error = read_sms(modem, sms)
            sms_sender = sms_body.get("content", {}).get("number", "")
            sms_text = sms_body.get("content", {}).get("text", "")
            debug("Message received from %s, text length %d" % (sms_sender, len(sms_text)))
            if sms_sender == config.TRUSTED_PHONE:
                sms_split = sms_text.split(" ")
                sms_split.append("")
                sms_command = sms_split[0].upper()
                match sms_command:
                    case "SHUTDOWN":
                        sent, ret = send_sms(modem, "Shutting down RPI4 Alarm", config.TRUSTED_PHONE)
                    case "REBOOT":
                        sent, ret = send_sms(modem, "Restarting RPI4 Alarm", config.TRUSTED_PHONE)
                    case "MOTION":
                        match sms_split[1].upper():
                            case "OFF":
                                sent, ret = send_sms(modem, "Stopping motion detection", config.TRUSTED_PHONE)
                            case "ON":
                                sent, ret = send_sms(modem, "Restarting motion detection", config.TRUSTED_PHONE)
                            case _:
                                sent, ret = send_sms(modem, "Invalid command: " + sms_text, config.TRUSTED_PHONE)
                    case "BATTERY":
                        sent, ret = send_sms(modem, "Battery status 99%, charging 1", config.TRUSTED_PHONE)
                    case "PHOTO":
                        sent, ret = send_sms(modem, "Photo taken", config.TRUSTED_PHONE)
                    case "VIDEO":
                        video_time = int(sms_split[1]) if sms_split[1] != "" and sms_split[1].isdigit() else 3
                        sent, ret = send_sms(modem, "Video recorded for %ds" % video_time, config.TRUSTED_PHONE)
                    case "HELP":
                        sent, ret = send_sms(modem, HELP_MSG, config.TRUSTED_PHONE)
                    case _:
                        sent, ret = send_sms(modem, "Invalid command: " + sms_text, config.TRUSTED_PHONE)
            else:
                log_fd, log_name = tempfile.mkstemp(suffix=".json", prefix="invalid-sms-", dir=config.LOG_PATH)
                err_msg = "Warning: Invalid from %s, text logged in %s!" % (sms_sender, log_name)
                sent, ret = send_sms(modem, err_msg, config.TRUSTED_PHONE)
                with os.fdopen(log_fd, 'w') as f:
                    f.write(json.dumps(sms_body, indent=4))
            # Remove the sms
            deleted, ret = delete_sms(modem, sms)
            debug("Deleted message %s: %s, %s" % (sms, sent, ret))
    # All done, sleep
    time.sleep(config.SLEEP_TIME)
