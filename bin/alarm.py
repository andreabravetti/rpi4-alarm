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
import traceback
import subprocess
from datetime import datetime

from modem import list_modem, list_sms, read_sms, send_sms, delete_sms
from utility import debug
from upsplus import input_voltage, battery_percentage
from sendmail import send_mail_with_auth

import config

HELP_MSG="RPI4 Alarm available commands: STOP, RESTART, POWEROFF, REBOOT, MOTION [STOP|START|RESTART], BATTERY, PHOTO, VIDEO [s], HELP"

# Create the log directory if it does not exists
os.makedirs(config.LOG_PATH, exist_ok=True)

# Initial starting message
debug("Starting RPI4 Alarm")
modem_list, modem_error = list_modem()
for modem in modem_list:
    debug("Found modem " + modem)
    sms_list, sms_error = list_sms(modem)
    if len(sms_list) > 0:
        debug("Found %s pending messages" % len(sms_list))
    sent, ret = send_sms(modem, "Starting RPI4 Alarm with %d pending commands" % len(sms_list), config.TRUSTED_PHONE)
    debug("Sent initial message: %s, %s" % (sent, ret))

# Main loop
while True:
    modem_list, modem_error = list_modem()
    for modem in modem_list:
        sms_list, sms_error = list_sms(modem)
        for sms in sms_list:
            try:
                sms_body, read_error = read_sms(modem, sms)
                sms_sender = sms_body.get("content", {}).get("number", "")
                sms_text = sms_body.get("content", {}).get("text", "")
                deferred = None
                debug("Message received from %s, text length %d" % (sms_sender, len(sms_text)))
                if sms_sender == config.TRUSTED_PHONE:
                    sms_split = sms_text.split(" ")
                    sms_split.append("")
                    sms_command = sms_split[0].upper()
                    debug("Command %s received from %s" % (sms_command, sms_sender))
                    match sms_command:
                        # case "STOP":
                        #     sent, ret = send_sms(modem, "Shutting down RPI4 Alarm service", config.TRUSTED_PHONE)
                        #     debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                        #     deferred = ['systemctl', 'stop', 'rpi4-alarm']
                        case "RESTART":
                            sent, ret = send_sms(modem, "Restarting RPI4 Alarm service", config.TRUSTED_PHONE)
                            debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                            deferred = ['systemctl', 'restart', 'rpi4-alarm']
                        # case "POWEROFF":
                        #     sent, ret = send_sms(modem, "Shutting down RPI4 Alarm host", config.TRUSTED_PHONE)
                        #     debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                        #     deferred = ['poweroff']
                        case "REBOOT":
                            sent, ret = send_sms(modem, "Restarting RPI4 Alarm host", config.TRUSTED_PHONE)
                            debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                            deferred = ['reboot']
                        case "MOTION":
                            match sms_split[1].upper():
                                case "STOP":
                                    sent, ret = send_sms(modem, "Stopping motion detection", config.TRUSTED_PHONE)
                                    debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                                    deferred = ['systemctl', 'stop', 'motion']
                                case "START":
                                    sent, ret = send_sms(modem, "Starting motion detection", config.TRUSTED_PHONE)
                                    debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                                    deferred = ['systemctl', 'start', 'motion']
                                case "RESTART":
                                    sent, ret = send_sms(modem, "Restarting motion detection", config.TRUSTED_PHONE)
                                    debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                                    deferred = ['systemctl', 'restart', 'motion']
                                case _:
                                    sent, ret = send_sms(modem, "Invalid command: " + sms_text, config.TRUSTED_PHONE)
                                    debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                        case "BATTERY":
                            bp, _ = battery_percentage()
                            iv, _ = input_voltage()
                            cc = ("charging voltage %.2fv" % (iv/1000)) if iv>3000 else "not charging"
                            sent, ret = send_sms(modem, "Battery status %d%%, %s" % (bp, cc), config.TRUSTED_PHONE)
                            debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                        case "PHOTO":
                            # apt install fswebcam
                            _, photo_name = tempfile.mkstemp(suffix=".jpg", prefix="photo-", dir=config.LOG_PATH)
                            subprocess.run(["fswebcam", "-r", "2592x1944", photo_name])
                            photo_sub = "Photo taken on %s saved in %s" % (datetime.now().strftime("%Y/%m/%d, %H:%M:%S"), photo_name)
                            send_mail_with_auth("Alarm photo", photo_sub, photo_name)
                            sent, ret = send_sms(modem, photo_sub, config.TRUSTED_PHONE)
                            debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                        case "VIDEO":
                            video_time = int(sms_split[1]) if sms_split[1] != "" and sms_split[1].isdigit() else 3
                            sent, ret = send_sms(modem, "Video recorded for %ds" % video_time, config.TRUSTED_PHONE)
                            debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                        case "HELP":
                            sent, ret = send_sms(modem, HELP_MSG, config.TRUSTED_PHONE)
                            debug("Reply to %s sent to %s: %s, %s" % (sms_command, config.TRUSTED_PHONE, sent, ret))
                        case _:
                            sent, ret = send_sms(modem, "Invalid command: " + sms_text, config.TRUSTED_PHONE)
                            debug("Reply to INVALID sent to %s: %s, %s" % (config.TRUSTED_PHONE, sent, ret))
                else:
                    log_fd, log_name = tempfile.mkstemp(suffix=".json", prefix="invalid-sms-", dir=config.LOG_PATH)
                    err_msg = "Warning: Invalid from %s, text logged in %s!" % (sms_sender, log_name)
                    sent, ret = send_sms(modem, err_msg, config.TRUSTED_PHONE)
                    with os.fdopen(log_fd, 'w') as f:
                        f.write(json.dumps(sms_body, indent=4))
            except:
                debug(traceback.format_exc())
            # Remove the sms
            deleted, ret = delete_sms(modem, sms)
            debug("Deleted message %s: %s, %s" % (sms, sent, ret))
            if not deleted:
                debug("Error deleting %s: deferred command \"%s\" not executed!" % (sms, " ".join(deferred)))
            elif deferred is not None:
                result = subprocess.run(deferred)
                debug("arg:\n%s\nout:\n%s\nerr:\n%s\n" % (result.args, result.stdout, result.stderr))
    # All done, sleep
    time.sleep(config.SLEEP_TIME)
