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

from base64 import b64encode
import sys
import requests
import urllib3
import pprint
from DETAILS import *

pp = pprint.PrettyPrinter(indent=4)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Umbrella:
    def __init__(self, mgtk, mgts, netk, nets, orgId):
        self.mgtk = mgtk
        self.mgts = mgts
        self.netk = netk
        self.nets = nets
        self.orgId = orgId
        if not (mgtk and mgts and netk and nets and orgId):
            raise ValueError("Check empty arguments")

    def call(self, endpoint, payload, headers, params, method):
        # Url
        base_url = 'https://management.api.umbrella.com/v1/'
        url = base_url + endpoint

        response = requests.request(method, url=url, params=params, headers=headers, data=payload)

        return response

    def get_policies(self, param):
        params = {}
        # Authentication
        base64string = b64encode(bytes(self.netk + ":" + self.nets, "utf-8")).decode("ascii")
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {base64string}'
        }
        endpoint = f"organizations/{self.orgId}/policies"
        payload = ''
        params['type'] = param
        response = self.call(endpoint, payload, headers, params, "get")
        return response.json()

    def get_targets(self):
        params = {}
        # Authentication
        base64string = b64encode(bytes(self.mgtk + ":" + self.mgts, "utf-8")).decode("ascii")
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {base64string}'
        }
        endpoint = f"organizations/{self.orgId}/networks"
        payload = ''
        response = self.call(endpoint, payload, headers, params, "get")
        return response.json()

    def manage_identity(self, policyId, originId, method):
        params = {}
        # Authentication
        base64string = b64encode(bytes(self.netk + ":" + self.nets, "utf-8")).decode("ascii")
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {base64string}'
        }
        endpoint = f"organizations/{self.orgId}/policies/{policyId}/identities/{originId}"
        payload = ''
        response = self.call(endpoint, payload, headers, params, method)
        return response.status_code
