"""
Copyright (c) 2023 Cisco and/or its affiliates.
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

__author__ = "Lakshya Tyagi <ltyagi@cisco.com>"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import os
import json
import requests
from dotenv import load_dotenv
from urllib.error import HTTPError
from flask import Flask, jsonify, request
import time
from datetime import datetime

load_dotenv()

# Meraki Environment Variables
meraki_base_url = os.getenv("MERAKI_BASE_URL")
meraki_api_key = os.getenv("MERAKI_API_KEY")
meraki_org_id = os.getenv("MERAKI_ORG_ID")
meraki_network_id = os.getenv("MERAKI_NETWORK_ID")
meraki_device_serial = os.getenv("MERAKI_DEVICE_SERIAL")

# Zone IDs, defined as customer and employee zones
zone_id_full_frame = os.getenv("ZONE_ID_FULL_FRAME")
zone_id_backroom = os.getenv("ZONE_ID_BACKROOM")
zone_id_employee_desk = os.getenv("ZONE_ID_EMPLOYEE_DESK")


# Meraki Payload and Headers
payload = {}
headers = {
  'X-Cisco-Meraki-API-Key': meraki_api_key
}

def backroom_zone_analytics(t0,t1):
    zone_endpoint = f'/devices/{meraki_device_serial}/camera/analytics/zones/{zone_id_full_frame}/history?t0={t0}&t1={t1}'
    try:
        backroom_zone_analytics_url = f"{meraki_base_url}{zone_endpoint}" 
        response = requests.request("GET", backroom_zone_analytics_url, headers=headers, data=payload)
        res = response.json()
        print(res)
        

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)

    return res

def employee_desk_analytics_zone(t0,t1):
    zone_endpoint = f'/devices/{meraki_device_serial}/camera/analytics/zones/{zone_id_full_frame}/history?t0={t0}&t1={t1}'
    try:
        employee_desk_zone_analytics_url = f"{meraki_base_url}{zone_endpoint}"
        response = requests.request("GET", employee_desk_zone_analytics_url, headers=headers, data=payload)
        res = response.json()
        print(res)
        

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)

    return res

#backroom_zone_analytics("2023-05-06T10:32:38.123Z", "2023-05-06T10:35:38.123Z")
#employee_desk_analytics_zone("2023-05-06T10:32:38.123Z", "2023-05-06T10:35:38.123Z")