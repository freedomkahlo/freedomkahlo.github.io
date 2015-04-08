from heapq import *
from datetime import *
import sys

def findTimes(events, startTime, endTime, timeLength):
    h = []
    if (endTime - startTime < timeLength or timeLength <= 0):
        return h
    for i in range(0, len(events)):
        heappush(h, [events[i]['startTime'], True])
        heappush(h, [events[i]['endTime'], False])
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
        return {'conflicts':0, 'startTime':startTime, 'endTime':endTime}
    while (len(h) != 0 and h[0][0] <= endTime):
        if (h[0][0] - currentStart >= timeLength):
            freeTime.append({'conflicts':currentConflicts, 'startTime':
                                 currentStart, 'endTime':h[0][0]})
        currentStart = h[0][0]
        while (len(h) != 0 and h[0][0] == currentStart):
            if (h[0][1]):
                currentConflicts += 1
            else:
                currentConflicts -= 1
            heappop(h)
    if (endTime - currentStart >= timeLength):
        freeTime.append({'conflicts':currentConflicts, 'startTime':
                             currentStart, 'endTime':endTime})
    return sorted(freeTime)

def main():
    epoch = datetime(1970, 1, 1)
    while (True):
        events = []
        while (True):
            print 'Enter an event of the form "d/m/y h:m:s d/m/y h:m:s"'
            print 'Enter 0 to stop. EST and 24 hour time assumed'
            resp = sys.stdin.readline().split()
            if (resp[0] == '0'):
                break
            a = resp[0].split('/')
            b = resp[1].split(':')
            a1 = resp[2].split('/')
            b1 = resp[3].split(':')
            for i in range(0, 3):
                a[i] = int(a[i])
                b[i] = int(b[i])
                a1[i] = int(a1[i])
                b1[i] = int(b1[i])
            t = datetime(a[2], a[1], a[0], b[0], b[1], b[2])
            t1 = datetime(a1[2], a1[1], a1[0], b1[0], b1[1], b1[2])
            t = (t - epoch)
            t = t.seconds + t.days * 24 * 3600
            t1 = (t1 - epoch)
            t1 = t1.seconds + t1.days * 24 * 3600
            events.append({'startTime':t, 'endTime':t1})
        print 'Enter "startTime endTime timeLength" of the form:'
        print 'd/m/y h:m:s d/m/y h:m:s h:m:s'
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

main()
