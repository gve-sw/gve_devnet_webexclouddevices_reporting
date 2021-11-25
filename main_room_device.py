'''
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
'''
import requests
import json
import csv
from credentials import token
from device_loop import place_device_list, place_device_name

#### ROOM DEVICES ####
# To poll a room device, we require the Webex Control Hub Administrator token

# Verify that the lists of personal and place devices are correct
print(place_device_list)


# This function pulls the required information of a single device (device id) in the place_device_list
def get_place_device_info(_token, _counter):
    url = "https://webexapis.com/v1/xapi/command/CallHistory.Get"
    payload = json.dumps({
        "deviceId": f'{place_device_list[_counter]}',
        "arguments": {
            "DetailLevel": "Full",
            "Filter": "All"
        }
    })
    headers = {
        'Authorization': f'Bearer {_token}',
        'Content-Type': 'application/json'
    }
    device_info = requests.request("POST", url, headers=headers, data=payload).json()
    return device_info

# Tests that function is providing correct info
# print(get_place_device_info(token, 1))

# Generates the CVS file for all registered room devices, stored in Reports/ folder
with open('place_device_report.csv', 'w', newline='') as f:
    writer = csv.writer((f))
    writer.writerow(['Device Name','Duration (In Seconds)', 'StartTime', 'EndTime', 'PeopleCunt', 'Device Id'])
    for device in range(len(place_device_list)):
        # print(device)
        response = get_place_device_info(token, device)
        try:
            for entry in response['result']['Entry']:
                writer.writerow(([place_device_name[device], entry['Duration'], entry['StartTime'], entry['EndTime'],entry['RoomAnalytics']['PeopleCount'], response['deviceId']]))
        except KeyError:
            pass
        except IndexError:
            pass

