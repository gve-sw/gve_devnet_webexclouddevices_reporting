#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Cisco and/or its affiliates.

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

This sample script leverages the Flask web service micro-framework
(see http://flask.pocoo.org/).  By default the web server will be reachable at
port 5000 you can change this default if desired (see `app.run(...)`).

"""


from dotenv import load_dotenv

__author__ = "Gerardo Chaves"
__author_email__ = "gchaves@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "Cisco"

from requests_oauthlib import OAuth2Session

from flask import Flask, request, redirect, session, url_for, render_template, make_response
import requests
import os
import time
import json

from webexteamssdk import WebexTeamsAPI, Webhook, AccessToken

# load all environment variables
load_dotenv()


AUTHORIZATION_BASE_URL = 'https://api.ciscospark.com/v1/authorize'
TOKEN_URL = 'https://api.ciscospark.com/v1/access_token'
SCOPE = ['spark-admin:devices_read', 'spark-admin:devices_write', 'spark:people_read','spark:xapi_commands','spark:xapi_statuses']

#initialize variabes for URLs
#REDIRECT_URL must match what is in the integration, but we will construct it below in __main__
#  as REDIRECT_URI = PUBLIC_URL + '/callback' so no need to hard code it here
PUBLIC_URL='http://0.0.0.0:5000'
REDIRECT_URI=""


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# Initialize the environment
# Create the web application instance
app = Flask(__name__)

app.secret_key = '123456789012345678901234'
#api = WebexTeamsAPI(access_token=TEST_TEAMS_ACCESS_TOKEN)
api = None

@app.route("/")
def login():
    """Step 1: User Authorization.
    Redirect the user/resource owner to the OAuth provider (i.e. Webex Teams)
    using a URL with a few key OAuth parameters.
    """
    global REDIRECT_URI
    global PUBLIC_URL

    if os.path.exists('tokens.json'):
        with open('tokens.json') as f:
            tokens = json.load(f)
    else:
        tokens = None

    if tokens == None or time.time()>(tokens['expires_at']+(tokens['refresh_token_expires_in']-tokens['expires_in'])):
        # We could not read the token from file or it is so old that even the refresh token is invalid, so we have to
        # trigger a full oAuth flow with user intervention
        REDIRECT_URI = PUBLIC_URL + '/callback'  # Copy your active  URI + /callback
        print("Using PUBLIC_URL: ",PUBLIC_URL)
        print("Using redirect URI: ",REDIRECT_URI)
        teams = OAuth2Session(os.getenv('CLIENT_ID'), scope=SCOPE, redirect_uri=REDIRECT_URI)
        authorization_url, state = teams.authorization_url(AUTHORIZATION_BASE_URL)

        # State is used to prevent CSRF, keep this for later.
        print("Storing state: ",state)
        session['oauth_state'] = state
        print("root route is re-directing to ",authorization_url," and had sent redirect uri: ",REDIRECT_URI)
        return redirect(authorization_url)
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

        session['oauth_token'] = tokens
        print("Using stored or refreshed token....")
        return redirect(url_for('.started'))

# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """
    Step 3: Retrieving an access token.
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    global REDIRECT_URI

    print("Came back to the redirect URI, trying to fetch token....")
    print("redirect URI should still be: ",REDIRECT_URI)
    print("Calling OAuth2SEssion with CLIENT_ID ",os.getenv('CLIENT_ID')," state ",session['oauth_state']," and REDIRECT_URI as above...")
    auth_code = OAuth2Session(os.getenv('CLIENT_ID'), state=session['oauth_state'], redirect_uri=REDIRECT_URI)
    print("Obtained auth_code: ",auth_code)
    print("fetching token with TOKEN_URL ",TOKEN_URL," and client secret ",os.getenv('CLIENT_SECRET')," and auth response ",request.url)
    token = auth_code.fetch_token(token_url=TOKEN_URL, client_secret=os.getenv('CLIENT_SECRET'),
                                  authorization_response=request.url)

    print("Token: ",token)
    print("should have grabbed the token by now!")
    session['oauth_token'] = token
    with open('tokens.json', 'w') as json_file:
        json.dump(token, json_file)
    return redirect(url_for('.started'))

@app.route("/started", methods=["GET"])
def started():

    # Use returned token to make Teams API calls for information on user, list of spaces and list of messages in spaces
    global api

    teams_token = session['oauth_token']
    api = WebexTeamsAPI(access_token=teams_token['access_token'])

    # first retrieve information about who is logged in
    theResult=api.people.me()
    print("TheResult calling api.people.me(): ",theResult)

    # generate a simple HTML page as a return that shows all the obtained information

    return ("""<!DOCTYPE html>
               <html lang="en">
                   <head>
                       <meta charset="UTF-8">
                       <title>Webex oAuth and refresh</title>
                   </head>
               <body>
               <p>
               <strong>Welcome """+theResult.displayName+""" , you have been propertly authenticated!</strong>
               </p>
               Your Webex Person ID is """+theResult.id+""" and the access token for you to use with your code derived from
               this sample is stored in the tokens.json file. It will now be used by the other scripts in this sample to be
               able to run un-attended. 
               <br>
               </body>
               </html>
            """)



#manual refresh of the token
@app.route('/refresh', methods=['GET'])
def webex_teams_webhook_refresh():

    global api

    teams_token = session['oauth_token']

    # use the refresh token to
    # generate and store a new one
    access_token_expires_at=teams_token['expires_at']

    print("Manual refresh invoked!")
    print("Current time: ",time.time()," Token expires at: ",access_token_expires_at)
    refresh_token=teams_token['refresh_token']
    #make the calls to get new token
    extra = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'refresh_token': refresh_token,
    }
    auth_code = OAuth2Session(os.getenv('CLIENT_ID'), token=teams_token)
    new_teams_token=auth_code.refresh_token(TOKEN_URL, **extra)
    print("Obtained new_teams_token: ", new_teams_token)
    #store new token

    teams_token=new_teams_token
    #TODO: validate if below is the right way to go about capturing new token.
    session['oauth_token'] = teams_token
    #store away the new token
    with open('tokens.json', 'w') as json_file:
        json.dump(teams_token, json_file)

    #test that we have a valid access token
    api = WebexTeamsAPI(access_token=teams_token['access_token'])

    return ("""<!DOCTYPE html>
                   <html lang="en">
                       <head>
                           <meta charset="UTF-8">
                           <title>Webex Teams Bot served via Flask</title>
                       </head>
                   <body>
                   <p>
                   <strong>The token has been refreshed!!</strong>
                   </p>
                   </body>
                   </html>
                """)


# Start the Flask web server
if __name__ == '__main__':

    print("Using PUBLIC_URL: ",PUBLIC_URL)
    print("Using redirect URI: ",REDIRECT_URI)
    app.run(host='0.0.0.0', port=5000, debug=True)