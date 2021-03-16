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

from app import db
from app import app


class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), index=True)
    policyId = db.Column(db.String(50), index=True)
    name = db.Column(db.String(50), index=True)
    start = db.Column(db.String(10), index=True)
    end = db.Column(db.String(10), index=True)
    target = db.Column(db.String(128), index=True)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'start': self.start,
            'end': self.end,
            'name': self.name,
            'id': self.policyId,
            'targets': self.target
        }

    def __repr__(self):
        return f'{self.day}: {self.name} from {self.start} to {self.end}'
