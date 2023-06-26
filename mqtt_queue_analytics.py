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
zone_id_queue = os.getenv("ZONE_ID_QUEUE")

# MQTT Credentials
MQTT_PORT = os.getenv("MQTT_PORT")
MQTT_SERVER = os.getenv("MQTT_SERVER")

# Track individuals within frame
obj_tracker = {}

def current_milli_time():
    return round(time.time() * 1000)

# connection notification that the script is running
def on_connect(client, userdata, flags, rc):
    print(f"Connected with code: {rc}")
    client.subscribe(MQTT_TOPIC)

# The callback for when a PUBLISH message is received from the mqtt server
def on_message(client, userdata, msg):
    global obj_tracker
    payload = json.loads(msg.payload.decode("utf-8", "ignore"))
    ts = payload["ts"]
    objects = payload["objects"]

    if not objects:
        logging.info("There are currently no tracked objects in the frame")
    else:
        logging.info("Detected objects:")
        logging.info(payload["objects"])

    obj_id_keys = []

    for obj in objects:
        # skip if object is not a person
        #if not obj["type"] == "person":
            #continue

        obj_id = obj["oid"]
        # add obj_id to obj_id_keys
        obj_id_keys.append(obj_id)

        # If object is not already in the object_tracker, add.
        if obj_id not in obj_tracker:
            obj_to_add = {}
            obj_to_add["ts_start"] = ts
            obj_to_add["age"] = current_milli_time() - ts
            obj_to_add["out_of_queue"] = 0
            obj_tracker[obj_id] = obj_to_add
        #if object is already present in the object_tracker
        else:
            obj_tracker[obj_id]["age"] = current_milli_time() - obj_tracker[obj_id]["ts_start"]
            logging.info(f"Object ID {obj_id}, age {obj_tracker[obj_id]['age']}")

    obj_queue_duration = {}
    key_to_remove = ""

    for key in obj_tracker:
        # if an oid is present in object tracker but not in updates oid list,
        # object has left the queue
        if key not in obj_id_keys:
            key_to_remove = key
            # set out_of_queue as true
            obj_tracker[key]["out_of_queue"] = 1
            # add details of out of queue object in obj_queue_duration
            obj_queue_duration[key] = obj_tracker[key]
            logging.info(f"Object ID {key} out of queue.")
            logging.info(f"Object ID {key}, time in queue: {obj_queue_duration[key]['age']}")
            # delete details of out of queue object from object tracker
            #del obj_tracker[key]

            # reset obj_queue_duration to track new objects
            #del obj_queue_duration[key]
    
    if key_to_remove != "":
        del obj_tracker[key_to_remove]
        del obj_queue_duration[key_to_remove]

    time.sleep(3)


if __name__ == "__main__":
    MQTT_TOPIC = f"/merakimv/{meraki_device_serial}/raw_detections"
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_SERVER, int(MQTT_PORT), 60)
        client.loop_forever()

    except Exception as ex:
        print("[MQTT]failed to connect or receive msg from mqtt, due to: \n {0}".format(ex))