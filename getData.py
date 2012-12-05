#!/usr/bin/env python

import urllib2, json, threading, socket, sys, random, datetime

class LockedDiskWrite:
    def __init__(self):
        self.lock = threading.Lock()

    def saveData(self, dataList, savePath):
        if len(dataList) == 0:
            return True
        if not self.lock.acquire(False):
            return False
        try:
            f = open(savePath, 'a')
            for data in dataList:
                #if 'kind' in data: # and (data['kind'] == 'software' or data['kind'] == 'error'):
                    #f = open(savePath + data['kind'] + str(ID), 'a')
                f.write(json.dumps(data))
                f.write('\n')
            f.close()
        except:
            return False
        finally:
            self.lock.release()
        return True

class ThreadedQuery(threading.Thread):
    count = 0

    def __init__(self, ldw, instNum, tqid, total, url, startID, endID, savePath = ''):
        threading.Thread.__init__(self)
        self.ldw = ldw
        self.instNum = instNum
        self.tqid = tqid
        self.total = total
        self.url = url
        self.startID = startID
        self.endID = endID
        self.savePath = savePath
        self.dataList = []
        self.errorList = []
        self.maxSize = 250
        self.displayProgressRate = 0.0000005

    def run(self):
        self.queryURLWithIDs(self.url, self.startID, self.endID, self.savePath)

    def queryURLWithIDs(self, url, startID, endID, savePath):
        ID = startID
        jsonError = 0
        while ID <= endID:
            try:
                u = urllib2.urlopen(url + str(ID))
                urlData = u.read()
                try:
                    jsonData = json.loads(urlData)
                    if jsonData['resultCount'] > 0 and 'kind' in jsonData['results'][0] and jsonData['results'][0]['kind'] == 'software':
                        self.dataList.append(jsonData['results'][0])
                except ValueError:
                    if jsonError != ID:
                        jsonError = ID
                        ID -= 1
                        ThreadedQuery.count -= 1
                u.close()
            except:
                self.errorList.append({'kind':'error', 'trackId':ID})
            ID += 1
            ThreadedQuery.count += 1

            if len(self.dataList) >= self.maxSize:
                if self.ldw.saveData(self.dataList, savePath + "data" + str(self.instNum)):
                    self.dataList = []

            if len(self.errorList) >= self.maxSize:
                if self.ldw.saveData(self.errorList, savePath + "error" + str(self.instNum)):
                    self.errorList = []
            '''
                    #print 'Progress (' + str(datetime.datetime.time(datetime.datetime.now())) + '): ' + str(float(ThreadedQuery.count) / float(self.total))
            if random.random() < self.displayProgressRate:
                print 'Progress (' + str(datetime.datetime.time(datetime.datetime.now())) + '): ' + str(float(ThreadedQuery.count) / float(self.total))
            '''

        while not self.ldw.saveData(self.dataList, savePath + "data" + str(self.instNum)):
            pass
        while not self.ldw.saveData(self.errorList, savePath + "error" + str(self.instNum)):
            pass

        print 'Thread ' + str(self.tqid) + ' finished'

lockedDiskWrite = LockedDiskWrite()
iTunesURL = 'http://itunes.apple.com/lookup?media=software&entity=software&id='
savePath = './'

startID = int(sys.argv[1])
endID = int(sys.argv[2])
instances = int(sys.argv[3])
instance = int(sys.argv[4])
instance = instance if instance >= 0 and instance < instances else 0 if instance < 0 else instances - 1
perInstance = (endID - startID) / instances + 1
if instance != 0:
    startID += perInstance * instance
if instance != (instances - 1):
    endID = startID + perInstance

threads = range(int(sys.argv[5]))
perThread = (endID - startID) / len(threads) + 1
count = 0

socket.setdefaulttimeout(120)

for i in threads:
    count += 1
    start = startID + i * perThread
    end = endID if count == len(threads) else start + perThread - 1
    t = ThreadedQuery(lockedDiskWrite, instance, i, perInstance, iTunesURL, start, end, savePath)
    t.start()
