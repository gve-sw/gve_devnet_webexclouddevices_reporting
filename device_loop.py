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

# Gets two lists: A personal Devices List and a place device list
import requests
from credentials import token


place_device_list = []
place_device_name = []

personal_device_list = []
personal_device_name = []
url = "https://webexapis.com/v1/devices"
params = {"max": 100}
payload={}

headers = {'Authorization': f'Bearer {token}'}
#response = requests.request("GET", url, headers=headers, data=payload).json()
# make the initial call for first page of results
response = requests.get(url, headers=headers, params=params)
#process first page of results
for item in response.json()['items']:
  for key, value in item.items():
    if key == 'placeId':
      place_device_list.append(item['id'])
      place_device_name.append(item['displayName'])
    elif key == 'personId':
      personal_device_list.append(item['ip'])
      personal_device_name.append(item['displayName'])
    else:
      pass

while response.headers.get('Link'):
    # Get the URL from the Link header
    next_url = response.links['next']['url']
    print(f"NEXT: {next_url}")
    # Request the next set of data
    response = requests.get(next_url, headers=headers)
    if response.headers.get('Link'):
        # process next page of results, if any
        for item in response.json()['items']:
            for key, value in item.items():
                if key == 'placeId':
                    place_device_list.append(item['id'])
                    place_device_name.append(item['displayName'])
                elif key == 'personId':
                    personal_device_list.append(item['ip'])
                    personal_device_name.append(item['displayName'])
                else:
                    pass
    else:
        print('No Link header, finished!')



# Test Lists
#print('place device list: ',place_device_list)
#print('place device name: ',place_device_name)
#print('personal device list: ',personal_device_list)
#print('personal device name: ',personal_device_name)

