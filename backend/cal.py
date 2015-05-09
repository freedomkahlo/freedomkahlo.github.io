from backend.apiclient.discovery import build
from backend.oauth2client.client import flow_from_clientsecrets
from backend.oauth2client.client import AccessTokenRefreshError
from backend.oauth2client.client import AccessTokenCredentialsError
from backend.oauth2client.client import AccessTokenCredentials
from backend.oauth2client.tools import argparser

from backend import httplib2
from backend import gflags

import os
import sys
import json
import requests
from heapq import *
from datetime import datetime, timedelta
import pytz
import argparse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import dateparse

from skedg.models import UserProfile

authIDLength = 32
FLAGS = gflags.FLAGS
DEVELOPER_KEY = 'AIzaSyC_sCrieFSw6_KM9zZHKOTUrXmeEwqkR3o'
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
		if (tempStorageForChecking[i][2] > datetime.now(pytz.timezone('US/Eastern'))):
			break
		i = i + 1
	tempStorageForChecking = tempStorageForChecking[i:]

def validateToken(email, eventID=None):
	u = User.objects.get(username=email)
	refreshToken = u.UserProfile.refToken
	#print refreshToken
	if refreshToken == '':
		return getCredClient(email, eventID)
	else:
		if getCredFromRefToken(email, 'validate') == 'refTokenRevoked': #Just to check that their refresh token is good
			return getCredClient(email, eventID)
		return 'Already Has Token'

# given username, assume that the user has a refresh token and get the credentials
def getCredFromRefToken(username, context=None):

	u = User.objects.get(username=username)
	refreshToken = u.UserProfile.refToken
	post_data = {'refresh_token':refreshToken, 'client_id':CLIENT_SECRETS_JSON['client_id'], 'client_secret':CLIENT_SECRETS_JSON['client_secret'], 'grant_type':'refresh_token'}
	result = requests.post('https://www.googleapis.com/oauth2/v3/token', data=post_data).json()
	
	if 'access_token' not in result:
		return 'refTokenRevoked'

	accessToken = result['access_token']

	if accessToken in ['null', '']:
		return 'refTokenRevoked'

	try:
		credentials = AccessTokenCredentials(accessToken, 'Skedg/1.0')
		return credentials
	except AccessTokenCredentialsError:
		print ('Credentials have been revoked')

# send client to Google Authentication page
def getCredClient(username, eventID=None):
	global tempStorageForChecking

	tempCode = get_random_string(length=authIDLength) #random gen

	expirationTime = datetime.now(pytz.timezone('US/Eastern')) + timedelta(minutes=10)
	tempStore = (username, tempCode, expirationTime)
	tempStorageForChecking.append(tempStore)
	if len(tempStorageForChecking) > 333:
		tempStorageForChecking = tempStorageForChecking[-333:]
	FLOW = flow_from_clientsecrets(CLIENT_SECRETS, scope='https://www.googleapis.com/auth/calendar', redirect_uri='http://skedg.tk:82/auth/')
	FLOW.params['access_type'] = 'offline'
	FLOW.params['approval_prompt'] = 'force'
	if eventID == None:
		FLOW.params['state'] = tempCode + '%' + username
	else:
		FLOW.params['state'] = tempCode + '%' + username + '%' + eventID
	auth_uri = FLOW.step1_get_authorize_url()

	return redirect(auth_uri)

# Listens to Google's Authorization, and puts in a refresh token
def auth(request):
	def returnPage(eventID):
		if eventID != None and len(eventID) == authIDLength:
			return HttpResponseRedirect('/' + eventID)
		return HttpResponseRedirect('/')

	global tempStorageForChecking

	# First get the authentication pair
	state = request.GET['state']
	stateParted = state.split('%')
	tempCode = stateParted[0]
	username = stateParted[1]
	if len(stateParted) == 3:
		eventID = stateParted[2]
	else:
		eventID = None

	# Clean up the temp storage list
	clearTempStorageForChecking()

	# check that this authentication pair exists in the list
	i=0
	while i < len(tempStorageForChecking):
		if (tempStorageForChecking[i][0] == username and tempStorageForChecking[i][1] == tempCode):
			break
		i += 1

	# Not found
	if i == len(tempStorageForChecking):
		return returnPage(eventID)

	tempStorageForChecking.pop(i)

	# if getting the code failed...
	if request.GET.has_key('error'):
		return returnPage(eventID)

	# no error, so there must be an authentication code
	authcode = request.GET['code']

	post_data = {'code':authcode, 'client_id':CLIENT_SECRETS_JSON['client_id'], 'client_secret':CLIENT_SECRETS_JSON['client_secret'], 'redirect_uri':'http://skedg.tk:82/auth/', 'grant_type':'authorization_code'}
	result = requests.post('https://www.googleapis.com/oauth2/v3/token', data=post_data).json()
	
	if 'refresh_token' not in result:
		return returnPage(eventID)

	refreshToken = result['refresh_token']

	if refreshToken in ['null', '']:
		return returnPage(eventID)

	u = User.objects.get(username=username)
	u.UserProfile.refToken = refreshToken
	u.UserProfile.save()
	u.save()
	u.backend = 'django.contrib.auth.backends.ModelBackend'
	login(request, u)

	return returnPage(eventID)

def buildService(username):
	credentials = getCredFromRefToken(username)
	if credentials == 'refTokenRevoked':
		return 'refTokenRevoked'

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
			print calendar_id
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

#events is a list events. Events are a dictionary with fields string 'creator' and datetimes 'startTime', 'endTime'
#startTime, endTime are both datetimes, timeLength is a timedelta, people is a list of everyone attending
#Returns a list of dictionaries, each with the fields: integer 'numFree', list of strings 'participants', datetime 'start/endTime'
def findTimes(events, startTime, endTime, timeLength, people):
	eventList = []
	if (endTime - startTime < timeLength or timeLength == timedelta(0)): #search interval too short
		return eventList

	#populate the event list with the events
	for i in range(0, len(events)):
		try:
			eventList.append([dateparse.parse_datetime(events[i]['start']['dateTime']), True, events[i]['creator']])
			eventList.append([dateparse.parse_datetime(events[i]['end']['dateTime']), False, events[i]['creator']])
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
		if eventList[incr][1]: #If it is an event start time
			busyMeter[people.index(eventList[incr][2])] += 1
			if busyMeter[people.index(eventList[incr][2])] == 1: #If this participant was free before
				participants -= 2 ** people.index(eventList[incr][2])
		else: #If event was an end time
			busyMeter[people.index(eventList[incr][2])] -= 1
			if busyMeter[people.index(eventList[incr][2])] == 0: #If this participant is now free
				participants += 2 ** people.index(eventList[incr][2])
		incr += 1

	if incr == len(eventList): #If no events occur during the search time
		s = ''
		for x in people:
			s += x + ', '
		return [{'numFree':len(people), 'participants':s[:-2], 'startTime':startTime, 'endTime':endTime}]

	dateList = [[startTime, participants]] #Only save the unique start/end times along with who can make it starting at that time
	while incr < len(eventList) and eventList[incr][0] <= endTime:
		currTime = eventList[incr][0]
		while incr < len(eventList) and eventList[incr][0] == currTime: #Parse through all the events that start or end at the current time
			if eventList[incr][1]: #If it is an event start time
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
			if participants & dateList[j][1] == participants:
				continue
			participants &= dateList[j][1]
			interval = findInterval(dateList, i)
			if (dateList[interval[1]][0] - dateList[interval[0]][0] < timeLength):
				continue
			peeps = getPeople(people, dateList[i][1])
			needToContinue = False
			print 'Checking For:' + dateList[interval[0]][0].isoformat() + ' to ' + dateList[interval[1]][0].isoformat()
			print 'in:' + freeTime.__str__()
			for d in freeTime:
				if d['endTime'] == dateList[interval[1]][0] and d['startTime'] == dateList[interval[0]][0]:
					print 'Found'
					if len(d['participants']) < len(peeps):
						d['participants'] = peeps
						d['numFree'] = len(filter(None, peeps.split(', ')))
					needToContinue = True
					break
			if needToContinue:
				continue
			freeTime.append({'numFree':len(filter(None, peeps.split(', '))), 'participants':peeps, 'startTime':dateList[interval[0]][0], 'endTime':dateList[interval[1]][0]})

	return sorted(freeTime, key=lambda date:date['numFree'], reverse=True)

#Helper function for find Times2 which finds the time intervals for a given participant set
def findInterval(dateList, curr):
	start = curr
	while start > 0 and dateList[start - 1][1] & dateList[curr][1] == dateList[curr][1]:
		start -= 1
	end = curr
	while end + 1 < len(dateList) and dateList[end][1] & dateList[curr][1] == dateList[curr][1]:
		end += 1
	return [start, end]

#Helper function for findTimes2 which, given a participant list in bit form, returns the list of participants in string form
def getPeople(people, participants):
	s = ''
	for x in [people[i] for i in range(len(people)) if participants & 2 ** i > 0]:
		s += x + ', '
	return s[:-2]


# timeStart and timeEnd are strings formatted RFC3339
# duration is in seconds
def findTimeForMany(usernameList, startInDateTime, endInDateTime, finalEndDateTime, duration):
	events = []
	for username in usernameList:
		service = buildService(username)
		if service == 'refTokenRevoked':
			continue
		events += [x for x in (get_event_list(service=service, start=startInDateTime.isoformat('T'),
		end=finalEndDateTime.isoformat('T'))) if not x.update({'creator':username})]
	avail = []
	
	#Get times for each interval
	while (endInDateTime <= finalEndDateTime):
		avail = avail + findTimes(events, startInDateTime, endInDateTime, duration, usernameList)
		
		startInDateTime = startInDateTime + timedelta(minutes=60*24)
		endInDateTime = endInDateTime + timedelta(minutes=60*24)
	
	return avail

def putTimeForMany(usernameList, eventName, startInDateTime, endInDateTime, organizer=None, location=None,description=None):
	resultIDs = []
	for username in usernameList:
		service = buildService(username)
		resultID = create_new_event(service=service, event_name=eventName, start=startInDateTime.isoformat('T'), 
			end=endInDateTime.isoformat('T'), location=location, description=description, organizer=organizer)
		resultIDs.append(resultID)
	return resultIDs
