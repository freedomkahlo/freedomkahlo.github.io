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
import gflags_validators
import json
from heapq import *
from datetime import *

FLAGS = gflags.FLAGS
DEVELOPER_KEY = 'AIzaSyC_sCrieFSw6_KM9zZHKOTUrXmeEwqkR3o'
epoch = datetime(1970, 1, 1)


def getCred(username):
	userCredfile = "credentials/" + username + "_cred.dat"
	CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets_skedg.json')
	FLOW = flow_from_clientsecrets(CLIENT_SECRETS, scope='https://www.googleapis.com/auth/calendar')

	# If the Credentials don't exist or are invalid, run through the native client
	# flow. The Storage object will ensure that if successful the good
	# Credentials will get written back to a file.
	storage = Storage(userCredfile)
	credentials = storage.get()
	if credentials is None or credentials.invalid == True:
		credentials = run(FLOW, storage)
	if credentials is None or credentials.invalid == True:
		os.remove(userCredfile)
		storage = Storage(userCredfile)
		credentials = run(FLOW, storage)
	#response = google.get_raw_access_token(data={
	#	'refresh_token': credentials['refresh_token'],
	#	'grant_type': 'refresh_token',
	#})
	#print response.content

	return credentials

def buildService(username):
	credentials = getCred(username)

	# Create an httplib2.Http object to handle our HTTP requests and authorize it
	# with our good Credentials.
	http = httplib2.Http()
	http = credentials.authorize(http)
	service = build(serviceName = 'calendar', version='v3', http=http, developerKey = DEVELOPER_KEY)
	return service

def create_new_event(service, event_name, start, end, location=None, description=None, organizer=None, calendar_id=None):
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

def update_event(service, event_id, event_name=None, start=None, end=None, location=None, description=None, organizer=None, calendar_id=None):
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

def get_event_list(service, start, end, calendar_id=None):
	if (calendar_id == None):
		calendar_id = 'primary'
	try:
		return service.events().list(calendarId=calendar_id, timeMin=start, timeMax=end,
			singleEvents = True, orderBy="startTime", fields='items(end,location,start,summary)').execute()['items']

	except AccessTokenRefreshError:
		print('Credentials have been revoked')


def get_event(service, event_id, calendar_id=None):
	if (calendar_id == None):
		calendar_id = CALENDAR_ID
	try:
		return service.events().get(calendarId=calendar_id, eventId=event_id).execute()
	except AccessTokenRefreshError:
		print('Credentials have been revoked')

def delete_event(service, event_id, calendar_id=None):
	if (calendar_id == None):
		calendar_id = CALENDAR_ID
	try:
		service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
	except AccessTokenRefreshError:
		print('Credentials have been revoked')

def convertRFC3339toRoyTime(RFC3339):
	epoch = datetime(1970, 1, 1)
	noTimeZone = RFC3339[:-6]
	timeZone = RFC3339[-6:-3] + RFC3339[-2:]
	#print noTimeZone
	t = datetime.strptime(noTimeZone, '%Y-%m-%dT%H:%M:%S') - timedelta(hours=int(timeZone)/100)
	#print t
	t = (t - epoch)
	return t.seconds + t.days * 24 * 3600

def convertRoyTimeToDateTime(RoyTime):
	epoch = datetime(1970, 1, 1)
	td = timedelta(RoyTime / (24 * 3600), RoyTime % (24 * 3600))
	return epoch + td

#startTime and endTime are in RoyTime
#timeLength in seconds
def findTimes(events, startTime, endTime, timeLength):
    h = []
    #print convertRFC3339toRoyTime(events[1]['start']['dateTime'])
    if (endTime - startTime < timeLength or timeLength <= 0):
        return h
    for i in range(0, len(events)):
        heappush(h, [convertRFC3339toRoyTime(events[i]['start']['dateTime']), True])
        heappush(h, [convertRFC3339toRoyTime(events[i]['end']['dateTime']), False])
        #print events[i]['summary'], events[i]['start']['dateTime'], events[i]['end']['dateTime']
    freeTime = []
    currentConflicts = 0
    currentStart = startTime
    while (len(h) != 0 and h[0][0] <= startTime):
        if (h[0][1]):
            currentConflicts += 1
        else:
            currentConflicts -= 1
        heappop(h)
    if(len(h) == 0):
        return [{'conflicts':0, 'startTime':startTime, 'endTime':endTime}]
    while (len(h) != 0 and h[0][0] <= endTime):
        if (h[0][0] - currentStart >= timeLength):
            freeTime.append({'conflicts':currentConflicts, 'startTime':
                                 convertRoyTimeToDateTime(currentStart), 'endTime':convertRoyTimeToDateTime(h[0][0])})
        currentStart = h[0][0]
        while (len(h) != 0 and h[0][0] == currentStart):
            if (h[0][1]):
                currentConflicts += 1
            else:
                currentConflicts -= 1
            heappop(h)
    if (endTime - currentStart >= timeLength):
        freeTime.append({'conflicts':currentConflicts, 'startTime':
                             convertRoyTimeToDateTime(currentStart), 'endTime':convertRoyTimeToDateTime(endTime)})
    return sorted(freeTime)

# timeStart and timeEnd are strings formatted RFC3339
# duration is in seconds
def findTimeForMany(usernameList, timeStart, timeEnd, duration):
	events = []
	for username in usernameList:
		service = buildService(username)
		events = events + (get_event_list(service=service, start=timeStart, end=timeEnd))

	startRoy = convertRFC3339toRoyTime(timeStart)
	endRoy = convertRFC3339toRoyTime(timeEnd)
	avail = findTimes(events, startRoy, endRoy, duration)
	
	return avail

	'''print avail
	for i in range(0, len(avail)):
		a = avail[i]['startTime']
		td = timedelta(a / (24 * 3600), a % (24 * 3600))
		b = avail[i]['endTime']
		td2 = timedelta(b / (24 * 3600), b % (24 * 3600))
		print (epoch + td).strftime('%d/%m/%Y %H:%M:%S'), (epoch + td2).strftime('%d/%m/%Y %H:%M:%S'), avail[i]['conflicts']
'''

def printAvail(avail):
	for i in range(0, len(avail)):
		print avail[i]['startTime'].strftime('%Y/%m/%d %H:%M:%S'), avail[i]['endTime'].strftime('%Y/%m/%d %H:%M:%S'), avail[i]['conflicts']

def main():
	users = sys.argv[1:]
	avail = findTimeForMany(users, timeStart='2015-04-06T13:00:00-04:00', 
		timeEnd='2015-04-07T14:00:00-04:00', duration = 3600)
	printAvail(avail)

	#getCred(users[0])

	'''
	if (sys.argv[0] == 'create'):
		result = create_new_event(event_name = sys.argv[1], 
	    					start = sys.argv[2], 
	    					end = sys.argv[3], 
	    					location = sys.argv[4],
	    					description = sys.argv[5],
	    					organizer = sys.argv[6])
		print json.dumps(result)

	print create_new_event(event_name = 'ChillFest 2015', 
						start = '2015-04-05T13:00:00.000-04:00', 
						end = '2015-04-05T14:00:00.000-04:00', 
						location = 'Buyers 24',
						description = 'Str8 Chillin',
						organizer = 'Crystal Qian')

	events = get_event_list(calendar_id='primary', 
		start='2015-04-05T13:00:00.000-04:00', end='2015-04-07T14:00:00.000-04:00')
	#print events

	for 

	print 'Enter "startTime endTime timeLength" of the form:'
	print 'd/m/y h:m:s d/m/y h:m:s h:m:s'
	epoch = datetime(1970, 1, 1)
	resp = sys.stdin.readline().split()
	a = resp[0].split('/')
	b = resp[1].split(':')
	a1 = resp[2].split('/')
	b1 = resp[3].split(':')
	c = resp[4].split(':')
	for i in range(0, 3):
		a[i] = int(a[i])
		b[i] = int(b[i])
		a1[i] = int(a1[i])
		b1[i] = int(b1[i])
		c[i] = int(c[i])
	t = datetime(a[2], a[1], a[0], b[0], b[1], b[2])
	t1 = datetime(a1[2], a1[1], a1[0], b1[0], b1[1], b1[2])
	t = (t - epoch)
	t = t.seconds + t.days * 24 * 3600
	t1 = (t1 - epoch)
	t1 = t1.seconds + t1.days * 24 * 3600
	t2 = int(c[2]) + 60 * int(c[1]) + 3600 * int(c[0])
	avail = findTimes(events, t, t1, t2)

	for i in range(0, len(avail)):
		a = avail[i]['startTime']
		td = timedelta(a / (24 * 3600), a % (24 * 3600))
		b = avail[i]['endTime']
		td2 = timedelta(b / (24 * 3600), b % (24 * 3600))
		print (epoch + td).strftime('%d/%m/%Y %H:%M:%S'), (epoch + td2).strftime('%d/%m/%Y %H:%M:%S'), avail[i]['conflicts']
'''



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