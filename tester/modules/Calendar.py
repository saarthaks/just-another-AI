from __future__ import print_function
import re
import httplib2
import os
import sys
sys.path.append('/Users/user/anaconda/bin')
from apiclient import discovery
import oauth2client
from oauth2client import client, tools

import datetime

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None


action = "fetch.events"

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'google_client_credentials.json'
APPLICATION_NAME = 'Alfred Email Fetching Module'


# The scope URL for read access to a user's calendar data
scope = 'https://www.googleapis.com/auth/calendar.readonly'

def get_credentials():
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

	store = oauth2client.file.Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)

	return credentials

def get_events(credentials, startDate=None):
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar', 'v3', http=http)
	if startDate is None:
		startDate = datetime.datetime.utcnow().isoformat() + 'Z'

	result = service.events().list(calendarId='primary', timeMin=startDate, maxResults=4, singleEvents=True,
								   orderBy='startTime').execute()
	events = result.get('items', [])
	return events

def format_event(event):
	title = str(event['summary'])
	raw_start = event['start']['datetime'].split("T")
	temp = raw_start[1]
	hr, minute, temp = temp.split(":", 2)
	hr = int(hr)
	m = "am." if hr < 12 else m = "pm."
	hr = hr % 12
	resp = title + " at " + str(hr) + ":" + str(minute) + " " + m

	return resp

def isValid(text):
	if text['result']['action'] == action:
		return True

	return False

def handle(text, speaker, profile):
	credentials = get_credentials()

	query = text['result']['resolvedQuery']
	if bool(re.search("tomorrow", query, re.IGNORECASE)):
		d = datetime.datetime.today() + datetime.timedelta(days=1)
		events = get_events(credentials, d)
	else:
		events = get_events(credentials)

	if not events:
		resp = "No upcoming events found."
		speaker.say(resp)
		return resp.split()

	resp = 'Here are the events you have. '
	for e in events:
		str = format_event(e)
		speaker.say(str)
		resp += str

	return resp.split()

