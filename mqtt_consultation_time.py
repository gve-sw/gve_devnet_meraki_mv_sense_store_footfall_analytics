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

import json
import time
import paho.mqtt.client as mqtt
import requests
from requests.auth import HTTPBasicAuth
import time
import datetime
import logging
from dotenv import load_dotenv
import os
from subprocess import Popen


load_dotenv()

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

# Meraki Environment Variables
meraki_base_url = os.getenv("MERAKI_BASE_URL")
meraki_api_key = os.getenv("MERAKI_API_KEY")
meraki_org_id = os.getenv("MERAKI_ORG_ID")
meraki_network_id = os.getenv("MERAKI_NETWORK_ID")
meraki_device_serial = os.getenv("MERAKI_DEVICE_SERIAL")

# Zone IDs, defined as customer and employee zones
zone_id_full_frame = os.getenv("ZONE_ID_FULL_FRAME")
zone_id_consultation_cust = os.getenv("ZONE_ID_CONSULTATION_CUSTOMER")
zone_id_consultation_employee = os.getenv("ZONE_ID_CONSULTATION_EMPLOYEE")

# MQTT Credentials
MQTT_PORT = os.getenv("MQTT_PORT")
MQTT_SERVER = os.getenv("MQTT_SERVER")

# Track individuals within frame
consultation_duration_tracker = {}

# Consultation flag: A boolean flag to mark the beginning and end of a consultation
consultation_flag = 0

def current_milli_time():
    return round(time.time() * 1000)

# connection notification that the script is running
def on_connect(client, userdata, flags, rc):
    print(f"Connected with code: {rc}")
    client.subscribe(MQTT_TOPIC)

# The callback for when a PUBLISH message is received from the mqtt server
def on_message(client, userdata, msg):
    global consultation_duration_tracker
    global consultation_flag

    payload = json.loads(msg.payload.decode("utf-8", "ignore"))
    ts = payload["ts"]
    customers = payload["counts"]["person"]

    if not customers:
        logging.info("There are currently no tracked objects in the frame")
    else:
        logging.info("Detected objects:")
        logging.info(payload["objects"])

    # If customers are present in zone and the consultation_flag is 0, begin tracking consultation.
    if int(customers) > 0 and consultation_flag == 0:
        logging.info("Consultation has begun, tracking.")
        consultation_data = {}
        consultation_data["ts_start"] = ts
        consultation_data["age"] = current_milli_time() - ts
        consultation_duration_tracker["Consultation"] = consultation_data
        consultation_flag = 1
    # If customers present in zone == 0 and consultation flag == 1, i.e consultation already being tracked, 
    # then stop tracking and trigger logs with consultation duration.
    elif int(customers) == 0 and consultation_flag == 1:
        logging.info("Consultation has ended, tracking.")
        consultation_duration_tracker['Consultation']["age"] = current_milli_time() - consultation_duration_tracker['Consultation']["ts_start"]
        consultation_flag = 0
        logging.info(f"Consultation start time: {consultation_duration_tracker['ts_start']}")
        logging.info(f"Consultation duration: {consultation_duration_tracker['Consultation']['age']}")

        # reset consultation_duration_tracker to track a new consultation session.
        del consultation_duration_tracker["Consultation"]


    time.sleep(5)


if __name__ == "__main__":
    MQTT_TOPIC = f"/merakimv/{meraki_device_serial}/{zone_id_consultation_employee}"
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_SERVER, int(MQTT_PORT), 60)
        client.loop_forever()

    except Exception as ex:
        print("[MQTT]failed to connect or receive msg from mqtt, due to: \n {0}".format(ex))