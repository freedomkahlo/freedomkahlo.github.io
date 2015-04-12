import sys
from backend import cal

users = sys.argv[1:]
avail = cal.findTimeForMany(users, timeStart='2015-04-06T13:00:00-04:00', 
	timeEnd='2015-04-07T14:00:00-04:00', duration = 3600)
cal.printAvail(avail)
