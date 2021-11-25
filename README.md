# GVE Devnet WebexCloudDevices Reporting  

Set of Python scripts that pull call history information from cloud registered devices and create a .csv report

## Contacts
* Max Acquatella (macquate@cisco.com)
* Gerardo Chaves (gchaves@cisco.com)

## Solution Components
* Webex Control Hub
*  Webex Room Devices
*  RoomOS APIs


## Coding Guides used for oAuth implementation
 
Downgrading the requests-oauthlib library to version 0.0.0 to avoid the OAuth error:
https://github.com/requests/requests-oauthlib/issues/324

Example Oauth with Webex Teams:
https://github.com/CiscoDevNet/webex-teams-auth-sample

Walkthrough including how to refresh tokens:
https://developer.webex.com/blog/real-world-walkthrough-of-building-an-oauth-webex-integration

Refresh token example:
https://stackoverflow.com/questions/27771324/google-api-getting-credentials-from-refresh-token-with-oauth2client-client

## Installation/Configuration


- Install python 3.6 or later   

- Recommended: Setup a virtual environment (https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)  

- Register a Webex Teams OAuth integration per the steps described at https://developer.webex.com/docs/integrations  
       - Set the Redirect URL to: http://0.0.0.0:5000/callback  or to whatever matches what you inted to use below for the **PUBLIC_URL** parameter  plus '/callback'
       - IMPORTANT: Select the following scopes for the integration `spark-admin:devices_read` `spark-admin:devices_write` `spark:people_read` `spark:xapi_commands` `spark:xapi_statuses`   
       - Before closing the window, take note of the Client ID and Client Secret fields, you will need them below and you cannot retrieve the Client Secret later! (you can always re-generate it)  

- Once you clone the repository, edit the .env file to fill out the following configuration variables:  

**CLIENT_ID**     
Set this variable to the Client ID from your integration. See the [Webex Integrations](https://developer.webex.com/docs/integrations) documentation for more details.  
  
**CLIENT_SECRET**  
Set this variable to the Client Secret from your integration. See the [Webex Integrations](https://developer.webex.com/docs/integrations)  documentation for more details.  
  
Also, in the `login.py` file, configure the following variable:  
  
**PUBLIC_URL**  
Set PUBLIC_URL to the URL where your instance of this Flask application will run. If you do not change the parameters 
of app.run() at the end of the main.py file, this should be the same value of 'http://0.0.0.0:5000' that is set by default 
in the sample code. (the code will then append /callback to it before making the API call to initiate the oAuth flow)   
NOTE: This URL does not actually have to map to a public IP address out on the internet.  
  
If you wish to do some testing using the `main_personal_device.py` or `main_room_device.py` tests scripts, edit the `credentials.py` file and set the value of the 'token' variable to a temporary access token for the administrator 
of your organization that you can obtain at https://developer.webex.com/docs/getting-started (in the "Your Personal Access Token" section)  

## Usage

- The main sample script in this repository (`get_call_history_room_devices.py`) will look for a `tokens.json` file in the same directory to be able to extract the access token 
and, if needed, the refresh token. This file is generated by launching the `login.py` script:  

    $ python login.py  

This will start a small Flask web application and, if you kept the default values, you should be able to access it by pointing a browser on your machine to
http://0.0.0.0:5000  
  
Follow the on-screen instructions to log into Webex using the Admin account of your organization so that the appropriate token with limited scopes is generated and stored into `tokens.json`  

Make sure this file remains secured since it could be use by someone with malicious intents to send commands to the devices, although that is about as much as they could do with it because 
it does not have any other scopes to do things like read/write/delete messages nor to do any other admin functions besides devices administration. 

If you intend to run this on an un-attended server, you need to make sure you change the parameters to start the Flask application in `login.py` to use an address and port that is accessible to 
the administrator to be able to log in. Alternatively, you can just execute `login.py` on your local computer and copy the `tokens.json` file to the folder where you are installing the `get_call_history_room_devices.py` script on 
an un-attended server so it can retrieve the token. As long as the script is run at least once every 90 days, the tokens in `tokens.json` will stay "refreshed" by the code in `get_call_history_room_devices.py` since 
the refresh token is also contained there and every time it runs it checks for validity and, if expired (every 14 days) it will refresh and rewrite the token to file.  


To generate the `place_device_report.csv` file with all call history for all shared room devices, just execute the `get_call_history_room_devices.py` script: 

    $ python get_call_history_room_devices.py  
  
This should create the `place_device_report.csv` output file on the same directory where you downloaded the code or re-create it if it was already there.


If you would like to use the tests scripts, just run the one would like to test with:  
- For extracting call history from devices registered in personal mode using a temporary admin access token:  
    $ python main_personal_device.py  
NOTE: since the cloud REST API to send commands to devices is not supported for Personal Mode devices, this script will attempt to connect directly to the device over HTTP 
so the IP address of the device needs to be accesible directly over the network from your machine (i.e. on the same LAN/WAN)  
  
- For extracting call history from shared space devices using a temporary admin access token:  
       $ python main_room_device.py  

These test scripts will also use the `place_device_report.csv` output file on the same directory where you downloaded the code.

# Screenshots


### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.