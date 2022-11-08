#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Project: RPI4 Alarm
# Source : utility.py
# Date   : Tue Nov  8 09:59:30 AM CET 2022
# Author : Andrea Bravetti
# ---------------------------------------------------------------

import config

def debug(msg):
    if config.DEBUG:
        print(msg)
