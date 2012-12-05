from pymongo import Connection
import json, operator, os

def addDataToDB(data):
    #connection = Connection('localhost')
    apps = connection.appdb.apps
    a = apps.find_one({'trackId' : data['trackId']})

    if not a:
        apps.insert(data)
    else:
        for key in data.keys():
            a[key] = data[key]
        apps.save(a)

    #connection.disconnect()

def getDataFromFile(fileName):
    with open(fileName) as f:
        for data in f.readlines():
            dataJSON = json.loads(data)
            dataJSON['genres'].sort()
            addDataToDB(dataJSON)

def getFilesFromFolder(folder):
    for fileName in os.listdir(folder):
        getDataFromFile(folder + '/' + fileName)
        print "Finished " + fileName

connection = Connection('localhost')
getFilesFromFolder('./data1')
connection.disconnect()
