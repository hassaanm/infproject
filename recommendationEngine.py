import pymongo
import json
import random

def getRandomApps(avoidApps):
    connection = pymongo.Connection('localhost')
    apps = connection.appdb.apps
    randomAppList = []
    count = apps.count()
    while len(randomAppList) < 5:
        offset = random.randrange(1, count)
        for app in  apps.find({'trackId':{'$nin':avoidApps}, 'languageCodesISO2A':{'$in':['EN']}}).skip(offset).limit(1):
            app['recType'] = 'fake'
            randomAppList += [app]
            avoidApps += [app['trackId']]
    connection.disconnect()

    return randomAppList

def getTopApps(avoidApps):
    filters = {'trackId':{'$nin':avoidApps}, 'averageUserRating':{'$gte':4}, 'userRatingCount':{'$gte':50000}, 'languageCodesISO2A':{'$in':['EN']}}
    sorts = [['userRatingCount', pymongo.DESCENDING]]

    connection = pymongo.Connection('localhost')
    apps = connection.appdb.apps
    topAppList = []
    topRec = apps.find(filters).sort(sorts)
    for app in topRec:
        app['recType'] = 'fake'
        topAppList += [app]
    connection.disconnect()

    return random.sample(topAppList, 5)

def getApps(filters, sorts):
    connection = pymongo.Connection('localhost')
    apps = connection.appdb.apps
    recommendations = apps.find(filters).sort(sorts)
    connection.disconnect()

    return recommendations

def mergeRandom(list1, list2):
    merged = []

    while len(list1) > 0 and len(list2) > 0:
        if random.random() > 0.5:
            randRange = int(random.random() * len(list1)) + 1
            merged += list1[:randRange]
            list1 = list1[randRange:]
        else:
            randRange = int(random.random() * len(list2))
            merged += list2[:randRange]
            list2 = list2[randRange:]
    merged += (list1 + list2)

    return merged

def getRecommendations(ratings = {}):
    filters = {'averageUserRating':{'$gte':4}, 'userRatingCount':{'$gte':50000}, 'languageCodesISO2A':{'$in':['EN']}}
    sorts = [['userRatingCount', pymongo.DESCENDING]]

    ratedApps = []
    connection = pymongo.Connection('localhost')
    apps = connection.appdb.apps
    for appId in ratings:
        ratedApps += [apps.find_one({'trackId':appId})]
    connection.disconnect()

    # update filters based on rated apps
    if len(ratedApps) > 0:
        # remove already rated apps
        filters['trackId'] = {'$nin':ratings.keys()}

        # get more recommendations of categories from liked apps
        categories = {}
        for app in ratedApps:
            for category in app['genres']:
                if ratings[app['trackId']] > 3:
                    categories[category] = categories.get(category, 0) + 1
                elif ratings[app['trackId']] > 0:
                    categories[category] = categories.get(category, 0) - 1
        favCategories = []
        for category in categories:
            if categories[category] > 0:
                favCategories += [category]
        if len(favCategories) > 0:
            filters['genres'] = {'$in':favCategories}

        # check if price is an issue
        onlyFree = True
        for app in ratedApps:
            if ratings[app['trackId']] > 0 and app['price'] > 0:
                onlyFree = False
        if onlyFree:
            filters['price'] = 0

        # update popularity
        minRatingCount = 50000
        for app in ratedApps:
            if ratings[app['trackId']] > 0 and app['userRatingCount'] < minRatingCount:
                minRatingCount = app['userRatingCount'] * 0.5
        if minRatingCount < 50000:
            filters['userRatingCount'] = {'$gte':minRatingCount}

    apps = getApps(filters, sorts)
    appsList = []
    for app in apps:
        app['recType'] = 'real'
        appsList += [app]
    newRecommendations = random.sample(appsList, 5)

    avoidAppIds = ratings.keys()
    for app in newRecommendations:
        avoidAppIds += [app['trackId']]
    #randomRecommendations = getRandomApps(avoidAppIds)
    topRecommendations = getTopApps(avoidAppIds)

    mergedRecommendations = ratedApps + mergeRandom(newRecommendations, topRecommendations)
    return mergedRecommendations

recEval = {'real':{'none':0, 'bad':0, 'good':0, 'neutral':0}, 'fake':{'none':0, 'bad':0, 'good':0, 'neutral':0}}
for i in range(5):
    ratings = {}
    recommendations = getRecommendations(ratings)
    for recommendation in recommendations:
        print recommendation['trackName'], recommendation['trackId'], recommendation['recType']
        rating = ''
        while rating == '' or rating == '\n':
            rating = raw_input('rating: ')
        rating = float(rating)
        ratings[recommendation['trackId']] = rating
        ratEval = 'none'
        if rating > 3:
            ratEval = 'good'
        elif rating == 3:
            ratEval = 'neutral'
        elif rating > 0:
            ratEval = 'bad'
        recEval[recommendation['recType']][ratEval] += 1
        print '{'
        for key in recommendation.keys():
            print key + ': ',
            print recommendation[key]
        print '}'
