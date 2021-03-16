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


import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template, redirect, url_for, request

from DETAILS import *
from app import app
from scheduler import *
from handler import *
from umbrella_connector import Umbrella
import json
import urllib3
import pprint

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
pp = pprint.PrettyPrinter(indent=2)
logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

sched = BackgroundScheduler()


# Login screen
@app.route('/', methods=['GET', 'POST'])
def index():
    global MGT_KEY
    global MGT_SECRET
    global NET_KEY
    global NET_SECRET
    global ORG_ID
    global connector
    logging.info(MGT_KEY)
    if request.method == 'GET':
        try:
            connector = Umbrella(MGT_KEY, MGT_SECRET, NET_KEY, NET_SECRET, ORG_ID)
            sched.add_job(check_policy, trigger='cron', minute='*', id='1', replace_existing=True,
                          args=[connector])
            logging.info("Scheduler Started")
            try:
                sched.start()
            except:
                pass
            return redirect(url_for('schedule'))
        except Exception as e:
            logging.exception('credentials not found, redirecting to log in')
            return render_template('login.html', title='Log In')

    elif request.method == 'POST':
        details = request.form
        logging.info(details)
        MGT_KEY = details['mgtk']
        MGT_SECRET = details['mgts']
        NET_KEY = details['netk']
        NET_SECRET = details['nets']
        ORG_ID = details['orgId']
        try:
            connector = Umbrella(MGT_KEY, MGT_SECRET, NET_KEY, NET_SECRET, ORG_ID)
            sched.add_job(check_policy, trigger='cron', minute='*', id='1', replace_existing=True,
                          args=[connector])
            logging.info("Scheduler Started")
            try:
                sched.start()
            except:
                pass
            return redirect(url_for('schedule'))
        except Exception as e:
            logging.exception('credentials not found, redirecting to log in')
            return render_template('login.html', title='Log In')


# Welcome screen
@app.route('/start', methods=['GET', 'POST'])
def schedule():
    global connector
    if request.method == 'GET':
        webPolicyList = connector.get_policies('web')
        dnsPolicyList = connector.get_policies('dns')
        return render_template('schedule.html', title='Umbrella Policy Scheduler', webPolicyList=webPolicyList,
                               dnsPolicyList=dnsPolicyList)
    elif request.method == 'POST':
        return redirect('schedule.html', code=302)


# Policy selected
@app.route('/policy/<policyId>', methods=['GET', 'POST'])
def scheduling(policyId):
    logging.info(policyId)
    targetlist = connector.get_targets()
    webPolicyList = connector.get_policies('web')
    dnsPolicyList = connector.get_policies('dns')
    policylist = webPolicyList + dnsPolicyList
    logging.info(policylist)

    selected_policy = next(item for item in policylist if str(item['policyId']) == str(policyId))

    if request.method == 'GET':
        return render_template('scheduling.html', title='Umbrella Policy Scheduler', webPolicyList=webPolicyList,
                               dnsPolicyList=dnsPolicyList, selected=selected_policy['name'],
                               policyId=selected_policy['policyId'], targetlist=targetlist)
    elif request.method == 'POST':
        data = request.form.to_dict()
        data['targets'] = ''
        targets = request.form.getlist('targets')
        for item in targets:
            data['targets'] += f",{item}"
        data['targets'] = data['targets'][1:]
        pp.pprint(f"COMMITTING")
        pp.pprint(data)
        status = commit(data, policyId, selected_policy['name'])
        if status:
            return render_template('scheduling.html', title='Umbrella Policy Scheduler', webPolicyList=webPolicyList,
                                   dnsPolicyList=dnsPolicyList, selected=selected_policy['name'],
                                   policyId=selected_policy['policyId'], targetlist=targetlist)


# Populate the list of schedules
@app.route('/parser', methods=['POST'])
def parser():
    if request.method == 'POST':
        policyList = {}
        policyId = request.json["policyId"]
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            entries = Policy.query.filter_by(policyId=policyId).filter_by(day=day).all()
            list = []
            for item in entries:
                list.append(item.serialize)
            policyList[day] = list
        return json.dumps(policyList)


# Validate the data
@app.route('/validator', methods=['POST'])
def validator():
    if request.method == 'POST':
        payload = {}
        data = request.json
        day = data['day']
        endTime = datetime.datetime.strptime(data['endTime'], '%H:%M')
        startTime = datetime.datetime.strptime(data['startTime'], '%H:%M')
        entries = Policy.query.filter_by(day=day).all()
        list = []
        if not data['targets']:
            payload['value'] = "target"
            return json.dumps(payload)
        for item in entries:
            list.append(item.serialize)
        pp.pprint(list)
        for item in list:
            if item['id'] == data['policyId']:
                continue
            cEndTime = datetime.datetime.strptime(item['end'], '%H:%M')
            cStartTime = datetime.datetime.strptime(item['start'], '%H:%M')
            DateRangesOverlap = max(startTime, cStartTime) < min(endTime, cEndTime)
            if DateRangesOverlap:
                payload['value'] = False
                payload['name'] = item['name']
                return json.dumps(payload)
            else:
                continue
        payload['value'] = True
        payload['name'] = 'good'
        return json.dumps(payload)
