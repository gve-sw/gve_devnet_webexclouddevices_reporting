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
import csv
import xmltodict
import base64
from credentials import device_username, device_password
from device_loop import personal_device_list, personal_device_name

#### PERSONAL DEVICES ####
# To poll the personal device we require the IP address (from the list) and the device username and password

# Verify that personal room device IP list
print(personal_device_list)

# Function that gets information for a single device
def personal_mode_device(_ip_address, _device_username, _device_password):
    userpass = f'{_device_username}:{_device_password}'
    encoded = base64.b64encode(userpass.encode()).decode()
    url = f"http://{_ip_address}/putxml"
    payload = """
        <Command>
            <CallHistory>
                <Get>
                    <DetailLevel>Full</DetailLevel>
                </Get>
            </CallHistory>
        </Command>"""
    headers = {
        'Authorization': f'Basic {encoded}',
        'Content-Type': 'application/xml'}

    response3 = requests.request("POST", url, headers=headers, data=payload, verify=False)
    dictionary = xmltodict.parse(str(response3.text))
    return dictionary


# Test function to get personal device info
# print(personal_mode_device('10.0.2.2', 'user', 'Password1234'))


with open('Reports/personal_device_report.csv', 'w', newline='') as f:
    writer = csv.writer((f))
    writer.writerow(['Device Name','Duration (In Seconds)', 'StartTime', 'EndTime', 'PeopleCunt', 'Device Id'])
    for personal_device_counter in range(len(personal_device_list)):
        # print(personal_device_counter)
        device_ip_address = personal_device_list[personal_device_counter]
        # print(device_ip_address)
        d = personal_mode_device(device_ip_address, device_username, device_password)
        try:
            for item in d['Command']['CallHistoryGetResult']['Entry']:
                writer.writerow(([personal_device_name[personal_device_counter],item['Duration'], item['StartTime'], item['EndTime'],item['RoomAnalytics']['PeopleCount'], [f'{device_ip_address}']]))
        except KeyError:
            pass
        except IndexError:
            pass