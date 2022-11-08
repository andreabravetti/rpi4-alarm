#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Project: RPI4 Alarm
# Source : upsplus.py
# Date   : Tue Nov  8 09:59:30 AM CET 2022
# Author : Andrea Bravetti
# ---------------------------------------------------------------

import subprocess

def input_voltage():
    # i2cget -y 1 0x17 0x07 w
    result = subprocess.run(['i2cget', '-y', '1', '0x17', '0x07', 'w'], stdout=subprocess.PIPE)
    return int(result.stdout, 0) if result.returncode==0 else 0, result.returncode

def battery_percentage():
    # i2cget -y 1 0x17 0x13 w
    result = subprocess.run(['i2cget', '-y', '1', '0x17', '0x13', 'w'], stdout=subprocess.PIPE)
    return int(result.stdout, 0) if result.returncode==0 else 0, result.returncode
