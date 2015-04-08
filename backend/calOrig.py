from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from oauth2client.file import Storage
from oauth2client.tools import run

import httplib2
import os
import sys
import gflags

#import datetime
#import time

FLAGS = gflags.FLAGS

APPLICATION_NAME = "Schedge/1.0"
CALENDAR_ID = "primary"
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
DEVELOPER_KEY = 'AIzaSyAIzvmGNCtZfy4RuTLTLvsY3tjE960MrMg'

flow = flow_from_clientsecrets(CLIENT_SECRETS,
                               scope='https://www.googleapis.com/auth/calendar')

storage = Storage('calendar.dat')
credentials = storage.get()
if credentials is None or credentials.invalid == True:
	credentials = run(flow, storage)

http = httplib2.Http()
http = credentials.authorize(http)


service = build(serviceName = 'calendar', version='v3', http=http,
				developerKey = DEVELOPER_KEY)

def create_new_event(event_name, start, end, location=None, description=None, organizer=None, calendar_id=None):
	if (calendar_id == None):
		calendar_id = CALENDAR_ID
	try:
		event = {
			'start': {
			'dateTime': start
			},
			'end': {
			'dateTime': end
			},
			"summary": event_name,
		}
		if (location != None):
			event['location'] = location
		if (description != None):
			event['description'] = description
		if (organizer != None):
			event['organizer'] = organizer

		result = service.events().insert(calendarId=calendar_id, body=event).execute()
		return result['id']
	except AccessTokenRefreshError:
		print ('Credentials have been revoked')

def update_event(event_id, event_name=None, start=None, end=None, location=None, description=None, organizer=None, calendar_id=None):
	if (calendar_id == None):
		calendar_id = CALENDAR_ID
	try:
		event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
		if (event_name != None):
			event['summary'] = event_name
		if (start != None):
			event['start']['dateTime'] = start
		if (end != None):
			event['end']['dateTime'] = end
		if (location != None):
			event['location'] = location
		if (description != None):
			event['description'] = description
		if (organizer != None):
			event['organizer'] = organizer

		result = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
		return result['id']
	except AccessTokenRefreshError:
		print ('Credentials have been revoked')

def get_event(event_id, calendar_id=None):
	if (calendar_id == None):
		calendar_id = CALENDAR_ID
	try:
		return service.events().get(calendarId=calendar_id, eventId=event_id).execute()
	except AccessTokenRefreshError:
		print('Credentials have been revoked')

def delete_event(event_id, calendar_id=None):
	if (calendar_id == None):
		calendar_id = CALENDAR_ID
	try:
		service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
	except AccessTokenRefreshError:
		print('Credentials have been revoked')

def main():
	if (sys.argv[0] == 'create'):
		result = create_new_event(event_name = sys.argv[1], 
	    					start = sys.argv[2], 
	    					end = sys.argv[3], 
	    					location = sys.argv[4],
	    					description = sys.argv[5],
	    					organizer = sys.argv[6])
		print json.dumps(result)

#    print create_new_event(event_name = 'Blehh', 
#    					start = '2014-07-29T13:00:00.000-07:00', 
#    					end = '2014-07-29T14:00:00.000-07:00', 
#    					location = 'Ichan 200',
#    					description = 'Karaoke night!',
#    					organizer = 'High Steppers')

#	print update_event(event_id = '3ql2ho2m62pnppan0rlui9nbt8', 
#				event_name='Karaoke!', end='2014-07-29T16:00:00.000-07:00', 
#				description='Sing, sing a song, sing out loud!')

#	delete_event(event_id = '3ql2ho2m62pnppan0rlui9nbt8')

#	event = get_event(event_id = '5nvc3a0t9hfsb575mc42npcv6s')
#	print str(event)
#	print str(event['id'])
#	print str(event['summary'])
#	print str(event['start']['dateTime'])
#	print str(event['end']['dateTime'])
#	print str(event['location'])
#	print (event['description'])
#	print event['organizer']
#			 str(event['id']), str(event['summary']), str(event['start']['dateTime']), \
#				str(event['end']['dateTime']), str(event['location']), str(event['description'])


if __name__ == "__main__":
    main()