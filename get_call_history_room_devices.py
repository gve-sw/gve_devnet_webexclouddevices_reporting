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
import os
import time
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

# load all environment variables
load_dotenv()

AUTHORIZATION_BASE_URL = 'https://api.ciscospark.com/v1/authorize'
TOKEN_URL = 'https://api.ciscospark.com/v1/access_token'
SCOPE = 'spark:all'

if os.path.exists('tokens.json'):
    with open('tokens.json') as f:
        tokens = json.load(f)
else:
    tokens = None

#from credentials import token

if tokens == None or time.time()>(tokens['expires_at']+(tokens['refresh_token_expires_in']-tokens['expires_in'])):
    # We could not read the token from file or it is so old that even the refresh token is invalid, so we have to
    # trigger a full oAuth flow with user intervention
    print("Missing tokens.json file or token is too old to be refreshed.... please run login.py to capture admin token.")
    exit()
else:
    # We read a token from file that is at least younger than the expiration of the refresh token, so let's
    # check and see if it is still current or needs refreshing without user intervention
    print("Existing token on file, checking if expired....")
    access_token_expires_at = tokens['expires_at']
    if time.time() > access_token_expires_at:
        print("expired!")
        refresh_token = tokens['refresh_token']
        # make the calls to get new token
        extra = {
            'client_id': os.getenv('CLIENT_ID'),
            'client_secret': os.getenv('CLIENT_SECRET'),
            'refresh_token': refresh_token,
        }
        auth_code = OAuth2Session(os.getenv('CLIENT_ID'), token=tokens)
        new_teams_token = auth_code.refresh_token(TOKEN_URL, **extra)
        print("Obtained new_teams_token: ", new_teams_token)
        # assign new token
        tokens = new_teams_token
        # store away the new token
        with open('tokens.json', 'w') as json_file:
            json.dump(tokens, json_file)
    print("Using stored or refreshed token....")

# we now have a valid Webex Access token to be able to continue
token=tokens['access_token']


place_device_list = []
place_device_name = []

personal_device_list = []
personal_device_name = []
url = "https://webexapis.com/v1/devices"
params = {"max": 500}
payload={}

headers = {'Authorization': f'Bearer {token}'}
# make the initial call for first page of results
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
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
    response.raise_for_status()
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
# Verify that the lists of personal and place devices are correct
print("Device list for places: ",place_device_list)


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
    device_info_response=requests.request("POST", url, headers=headers, data=payload)
    device_info = device_info_response.json()
    return device_info


# Generates the CVS file for all registered room devices
with open('place_device_report.csv', 'w', newline='') as f:
    writer = csv.writer((f))
    writer.writerow(['Device Name','Duration (In Seconds)', 'StartTime', 'EndTime', 'PeopleCunt', 'Device Id'])
    for device in range(len(place_device_list)):
        response = get_place_device_info(token, device)
        print('Processing device ',place_device_name[device],end='')
        if 'errors' in response:
           print('   Error!: ',response['errors'][0]['description'],' , skipping....')
        else:
            print('   writing out history for device....')
            for entry in response['result']['Entry']:
                writer.writerow(([place_device_name[device], entry['Duration'], entry['StartTime'], entry['EndTime'],entry['RoomAnalytics']['PeopleCount'], response['deviceId']]))


