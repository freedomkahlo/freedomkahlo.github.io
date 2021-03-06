from backend.apiclient.discovery import build
from backend.oauth2client.client import OAuth2WebServerFlow
from backend.oauth2client.client import flow_from_clientsecrets
from backend.oauth2client.client import AccessTokenRefreshError
from backend.oauth2client.client import AccessTokenCredentialsError
from backend.oauth2client.client import AccessTokenCredentials
from backend.oauth2client.file import Storage
from backend.oauth2client.tools import argparser
from backend.oauth2client.tools import run
from backend.oauth2client.tools import run_flow

from backend import httplib2
from backend import gflags
from backend import gflags_validators

import os
import sys
import json
import urllib
import urllib2
import requests
import string
import random
from heapq import *
import datetime
import argparse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from events.models import UserProfile

FLAGS = gflags.FLAGS
DEVELOPER_KEY = 'AIzaSyC_sCrieFSw6_KM9zZHKOTUrXmeEwqkR3o'
epoch = datetime.datetime(1970, 1, 1)
parser = argparse.ArgumentParser(parents=[argparser])
flowflags = parser.parse_args(args=[])
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secret_skedg.json')
CLIENT_SECRETS_JSON_FILE = open(CLIENT_SECRETS)
CLIENT_SECRETS_JSON = json.load(CLIENT_SECRETS_JSON_FILE)['web']
CLIENT_SECRETS_JSON_FILE.close()

# holds temporary user/random code information for users being authenticated through Google
tempStorageForChecking = [] #stores tuples of type (username, tempcode)

# run through the tempStorageForChecking list and delete things that are too old
def clearTempStorageForChecking():
	global tempStorageForChecking
	i=0
	while i < len(tempStorageForChecking):
		if (tempStorageForChecking[i][2] > datetime.datetime.now()):
			break
		i = i + 1
	tempStorageForChecking = tempStorageForChecking[i:]

def validateToken(username):
	u = User.objects.get(username=username)
	refreshToken = u.UserProfile.refToken
	#print refreshToken
	if refreshToken == '':
		return getCredClient(username)
	else:
		getCredFromRefToken(username) #Just to check that their refresh token is good
		return HttpResponseRedirect('/events/')

# given username, assume that the user has a refresh token and get the credentials
def getCredFromRefToken(username):
	def token_refresh_error():
		getCredClient(username)
		return HttpResponseRedirect('/')

	u = User.objects.get(username=username)
	refreshToken = u.UserProfile.refToken
	post_data = {'refresh_token':refreshToken, 'client_id':CLIENT_SECRETS_JSON['client_id'], 'client_secret':CLIENT_SECRETS_JSON['client_secret'], 'grant_type':'refresh_token'}
	result = requests.post('https://www.googleapis.com/oauth2/v3/token', data=post_data).json()
	
	if 'access_token' not in result:
		return token_refresh_error()

	accessToken = result['access_token']

	if accessToken in ['null', '']:
		return token_refresh_error()
	try:
		credentials = AccessTokenCredentials(accessToken, 'Skedg/1.0')
		return credentials
	except AccessTokenCredentialsError:
		print ('Credentials have been revoked')

# send client to Google Authentication page
def getCredClient(username):
	global tempStorageForChecking

	tempCode = get_random_string(length=32) #random gen
	expirationTime = datetime.datetime.now() + datetime.timedelta(minutes=10)
	tempStore = (username, tempCode, expirationTime)
	tempStorageForChecking.append(tempStore)
	FLOW = flow_from_clientsecrets(CLIENT_SECRETS, scope='https://www.googleapis.com/auth/calendar', redirect_uri='http://skedg.tk/auth/')
	FLOW.params['access_type'] = 'offline'
	FLOW.params['approval_prompt'] = 'force'
	FLOW.params['state'] = tempCode + '%' + username
	auth_uri = FLOW.step1_get_authorize_url()
	#print(auth_uri+'&approval_prompt=force')
	#return redirect(auth_uri+'&approval_prompt=force')
	return redirect(auth_uri)

# Listens to Google's Authorization, and puts in a refresh token
def auth(request):
	def authentication_error():
		return HttpResponseRedirect('/')

	global tempStorageForChecking

	# First get the authentication pair
	state = request.GET['state']
	tempCode = state.partition('%')[0]
	username = state.partition('%')[2]

	# Clean up the temp storage list
	clearTempStorageForChecking()

	# check that this authentication pair exists in the list
	i=0
	while i < len(tempStorageForChecking):
		if (tempStorageForChecking[i][0] == username and tempStorageForChecking[i][1] == tempCode):
			break
		i = i + 1

	# Not found
	if i == len(tempStorageForChecking):
		return authentication_error()

	tempStorageForChecking.pop(i)

	# if getting the code failed...
	if request.GET.has_key('error'):
		return authentication_error()

	# no error, so there must be an authentication code
	authcode = request.GET['code']

	post_data = {'code':authcode, 'client_id':CLIENT_SECRETS_JSON['client_id'], 'client_secret':CLIENT_SECRETS_JSON['client_secret'], 'redirect_uri':'http://skedg.tk/auth/', 'grant_type':'authorization_code'}
	result = requests.post('https://www.googleapis.com/oauth2/v3/token', data=post_data).json()
	
	if 'refresh_token' not in result:
		return authentication_error()

	refreshToken = result['refresh_token']

	if refreshToken in ['null', '']:
		return authentication_error()

	u = User.objects.get(username=username)
	u.UserProfile.refToken = refreshToken
	u.UserProfile.save()
	u.save()

	return HttpResponseRedirect('/events/')

def buildService(username):
	credentials = getCredFromRefToken(username)

	# Create an httplib2.Http object to handle our HTTP requests and authorize it
	# with our good Credentials.
	http = httplib2.Http()
	http = credentials.authorize(http)
	service = build(serviceName = 'calendar', version='v3', http=http, developerKey = DEVELOPER_KEY)
	return service

def create_new_event(service, event_name, start, end, location=None, description=None, organizer=None, calendar_id=None):
	if (calendar_id == None):
		calendar_id = 'primary'
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
		calendar_id = 'primary'
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

def get_event_list(service, start, end):
	try:
		# first grab list of calendar names
		calendar_list = service.calendarList().list(fields='items(id,summary)').execute()
		calIDlist = [calendar_list_entry['id'] for calendar_list_entry in calendar_list['items']]

		##### Check if 'items exists'
		events = []
		for calendar_id in calIDlist:
			events += service.events().list(calendarId=calendar_id, timeMin=start, timeMax=end,
				singleEvents = True, orderBy="startTime", fields='items(end,location,start,summary)').execute()['items']

		return events

	except AccessTokenRefreshError:
		print('Credentials have been revoked')


def get_event(service, event_id, calendar_id=None):
	if (calendar_id == None):
		calendar_id = 'primary'
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
	epoch = datetime.datetime(1970, 1, 1)
	noTimeZone = RFC3339[:-6]
	timeZone = RFC3339[-6:-3] + RFC3339[-2:]
	#print noTimeZone
	t = datetime.datetime.strptime(noTimeZone, '%Y-%m-%dT%H:%M:%S') - datetime.timedelta(hours=int(timeZone)/100)
	#print t
	t = (t - epoch)
	return t.seconds + t.days * 24 * 3600

def convertRoyTimeToDateTime(RoyTime):
	epoch = datetime.datetime(1970, 1, 1)
	td = datetime.timedelta(RoyTime / (24 * 3600), RoyTime % (24 * 3600))
	return epoch + td

#startTime and endTime are in RoyTime
#timeLength in seconds
def findTimes(events, startTime, endTime, timeLength):
	h = []
	#print convertRFC3339toRoyTime(events[1]['start']['dateTime'])
	if (endTime - startTime < timeLength or timeLength <= 0):
		return h
	for i in range(0, len(events)):
		try:
			heappush(h, [convertRFC3339toRoyTime(events[i]['start']['dateTime']), True])
			heappush(h, [convertRFC3339toRoyTime(events[i]['end']['dateTime']), False])
			#print events[i]['summary'], events[i]['start']['dateTime'], events[i]['end']['dateTime']
		except:
			pass
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
		return [{'conflicts':0, 'startTime':convertRoyTimeToDateTime(startTime), 'endTime':convertRoyTimeToDateTime(endTime)}]
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

#events is a list events. Events are a dictionary with fields string 'creator' and datetimes 'startTime', 'endTime'
#startTime, endTime are both datetimes, timeLength is a timedelta
#Returns a list of dictionaries, each with the fields: integer 'numFree', list of strings 'participants', datetime 'start/endTime'
def findTimes2(events, startTime, endTime, timeLength):
	eventList = []
	if (endTime - startTime < timeLength or timeLength == timedelta(0)): #search interval too short
		return eventList

	#List of people who have events
	people = []
	#populate the event list with the events
	for i in range(0, len(events)):
		try:
			eventList.append([events[i]['start']['dateTime'], True, events[i]['creator']])
			eventList.append([events[i]['end']['dateTime'], False, events[i]['creator']])
			people.append(events[i]['creator'])
		except:
			#Ignore events without a dateTime (all day events)
			pass

	eventList = sorted(eventList, key=lambda event:event[0]) #Sort events by the datetime
	#List of dictionaries
	freeTime = []
	participants = 2 ** len(people) - 1 #The people who can attend, stored as bits
	incr = 0 #current position in the eventList
	busyMeter = [0 for x in range(len(people))] #Lists how many events each participant is in at a time

	while incr < len(eventList) and eventList[incr][0] <= startTime: #Parse through all the events that start before the starttime
		if eventList[incr][0]: #If it is an event start time
			busyMeter[people.index(eventList[incr][2])] += 1
			if busyMeter[people.index(eventList[incr][2])] == 1: #If this participant was free before
				participants -= 2 ** people.index(eventList[incr][2])
		else: #If event was an end time
			busyMeter[people.index(eventList[incr][2])] -= 1
			if busyMeter[people.index(eventList[incr][2])] == 0: #If this participant is now free
				participants += 2 ** people.index(eventList[incr][2])
		incr += 1

	if incr == len(eventList): #If no events occur during the search time
		return [{'numFree':len(people), 'participants':people, 'startTime':startTime, 'endTime':endTime}]

	dateList = [[startTime, participants]] #Only save the unique start/end times along with who can make it starting at that time
	while incr < len(eventList) and eventList[incr][0] <= endTime:
		currTime = eventList[incr][0]
		while incr < len(eventList) and eventList[incr][0] == currTime: #Parse through all the events that start or end at the current time
			if eventList[incr][0]: #If it is an event start time
				busyMeter[people.index(eventList[incr][2])] += 1
				if busyMeter[people.index(eventList[incr][2])] == 1: #If this participant was free before
					participants -= 2 ** people.index(eventList[incr][2])
			else: #If event was an end time
				busyMeter[people.index(eventList[incr][2])] -= 1
				if busyMeter[people.index(eventList[incr][2])] == 0: #If this participant is now free
					participants += 2 ** people.index(eventList[incr][2])
			incr += 1
		dateList.append([currTime, participants])
	if dateList[-1][0] < endTime:
		dateList.append([endTime, participants])

	#Find the time intervals now
	for i in range(len(dateList)):
		participants = -1
		for j in range(i, len(dateList)):
			if participants & dateList[i][1] == participants:
				pass
			participants &= dateList[i][1]
			interval = findInterval(dateList, i)
			if (dateList[interval[1]][0] - dateList[interval[0]][0] < timeLength):
				pass
			peeps = getPeople(people, dateList[i][1])
			freeTime.append({'numFree':len(peeps), 'participants':peeps, 'startTime':dateList[interval[0]][0], 'endTime':dateList[interval[1]][0]})

	return sorted(freeTime, key=lambda date:date['numFree'], reverse=True)

#Helper function for find Times2 which finds the time intervals for a given participant set
def findInterval(dateList, curr):
	start = curr
	while start > 0 and dateList[start][1] & dateList[curr][1] == dateList[curr][1]:
		start -= 1
	end = curr
	while end + 1 < len(dateList) and dateList[end][1] & dateList[curr][1] == dateList[curr][1]:
		end += 1
	return [start, end]

#Helper function for findTimes2 which, given a participant list in bit form, returns the list of participants in string form
def getPeople(people, participants):
	return [people[i] for i in range(len(people)) if participants & 2 ** i > 0]


# timeStart and timeEnd are strings formatted RFC3339
# duration is in seconds
######!!!!! When we implement having multiple time ranges, we will have to 
########### do the timeStart and timeEnd as a list of tuple(timeStart, timeEnd)
def findTimeForMany(usernameList, startInDateTime, endInDateTime, finalEndDateTime, duration):
	events = []
	for username in usernameList:
		service = buildService(username)
		events = events + [x for x in (get_event_list(service=service, start=startInDateTime.strftime('%Y-%m-%dT%H:%M:00-04:00'),
		 end=finalEndDateTime.strftime('%Y-%m-%dT%H:%M:00-04:00'))) if x.update({'creator':username})]
	avail = []
	
	#Get times for each interval
	while (endInDateTime <= finalEndDateTime):
		avail = avail + findTimes2(events, startInDateTime, endInDateTime, duration)
		
		startInDateTime = startInDateTime + datetime.timedelta(1, 0, 0)
		endInDateTime = endInDateTime + datetime.timedelta(1, 0, 0)
	
	return avail

def putTimeForMany(usernameList, eventName, startInDateTime, endInDateTime, organizer=None, location=None,description=None):
	resultIDs = []
	for username in usernameList:
		service = buildService(username)
		resultID = create_new_event(service=service, event_name=eventName, start=startInDateTime.strftime('%Y-%m-%dT%H:%M:00-00:00'), 
			end=endInDateTime.strftime('%Y-%m-%dT%H:%M:00-00:00'), location=location, description=description, organizer=organizer)
		resultIDs.append(resultID)
	return resultIDs
	

def printAvail(avail):
	for i in range(0, len(avail)):
		print (avail[i]['startTime'].strftime('%Y/%m/%d %H:%M:%S'), avail[i]['endTime'].strftime('%Y/%m/%d %H:%M:%S'), avail[i]['conflicts'])

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