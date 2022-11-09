#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Project: Sendmail
# Source : sendmail.py
# Date   : Wed 01 Jan 2020 12:24:21 PM CET
# Author : Andrea Bravetti
# Contact: andreabravetti@gmail.com
# ---------------------------------------------------------------

'''
This is sendmail
'''

import os
import sys
import email, smtplib, ssl
import traceback

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime

import config

def send_mail_with_auth(subject: str, body: str, attachment: str = None):
    try:
        with open(os.path.join(config.LOG_PATH, "sendmail.log"), "a") as log:
            log.write("* SEND %s %s\n" % (subject, attachment))

        message = MIMEMultipart()
        message["From"] = config.EMAIL_SENDER
        message["To"] = config.EMAIL_ADDRESS
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        if attachment is not None:
            with open(attachment, "rb") as af:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(af.read())

            encoders.encode_base64(part)

            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(attachment)}",
            )
            message.attach(part)

        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_SENDER, config.EMAIL_ADDRESS, text)

        with open(os.path.join(config.LOG_PATH, "sendmail.log"), "a") as log:
            log.write("# SENT %s %s\n" % (subject, attachment))

    except Exception:
        with open(os.path.join(config.LOG_PATH, "sendmail.log"), "a") as log:
            log.write("Error while %s %s:\n\n%s\n\n" % (subject, attachment, traceback.format_exc()))

if __name__ == "__main__":
    match len(sys.argv):
        case 3:
            send_mail_with_auth(
                "Motion Alert (%s)" % sys.argv[1],
                "Motion Alert on %s" % str(datetime.now()),
                sys.argv[2]
            )
        case 2:
            send_mail_with_auth(
                "Motion Alert (%s)" % sys.argv[1],
                "Motion Alert on %s" % str(datetime.now())
            )
        case _:
            raise Exception("Invalid parameter in sendmail")
