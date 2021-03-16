#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""


__author__ = "Josh Ingeniero <jingenie@cisco.com>"
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


from handler import *
import requests
import datetime
import logging
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)


def what_time_day():
    current = datetime.datetime.now()
    now = {}
    now['time'] = current.strftime("%H:%M")
    now['day'] = current.strftime("%A").lower()
    return now


def check_policy(umbrella):
    # Check time
    now = what_time_day()
    time = now['time']
    day = now['day']
    print('Time:', time)
    print('Day:', day)

    # check policies to be activated/deactivated
    starting = Policy.query.filter_by(day=day).filter_by(start=time).first()
    ending = Policy.query.filter_by(day=day).filter_by(end=time).first()

    if ending:
        try:
            targets = ending.target.split(",")
            for target in targets:
                response = umbrella.manage_identity(ending.policyId, target, "delete")
                if str(response) == "200":
                    logging.info(f"Successfully deactivated Umbrella policy {ending.name}")
                else:
                    logging.info(f"Failed to deactivate Umbrella policy {ending.name}")
        except Exception as e:
            logging.exception("Ending Error")

    if starting:
        try:
            targets = starting.target.split(",")
            for target in targets:
                response = umbrella.manage_identity(starting.policyId, target, "put")
                if str(response) == "200":
                    logging.info(f"Successfully activated Umbrella policy {starting.name}")
                else:
                    logging.info(f"Failed to activate Umbrella policy {starting.name}")
        except Exception as e:
            logging.exception("Starting Error")
