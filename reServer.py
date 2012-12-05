from flask import Flask, Response
import recommendationEngine
import json

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def getAppRecommendations():
    recommendations = recommendationEngine.getRecommendations()
    recApps = {}
    for recommendation in recommendations:
        #print recommendation
        averageUserRating = 0
        if 'averageUserRating' in recommendation:
            averageUserRating = recommendation['averageUserRating']
        screenshotUrls = recommendation['screenshotUrls']
        if len(screenshotUrls) == 0 and 'ipadScreenshotUrls' in recommendation and len(recommendation['ipadScreenshotUrls']) > 0:
            screenshotUrls = recommendation['ipadScreenshotUrls']
        recApps[recommendation['trackId']] = {'trackName':recommendation['trackName'], 'description':recommendation['description'], 'sellerName':recommendation['sellerName'], 'artworkUrl60':recommendation['artworkUrl60'], 'artworkUrl100':recommendation['artworkUrl100'], 'artworkUrl512':recommendation['artworkUrl512'], 'formattedPrice':recommendation['formattedPrice'], 'screenshotUrls':screenshotUrls, 'recType':recommendation['recType'], 'averageUserRating':averageUserRating}
    js = json.dumps(recApps)
    resp = Response(js, status=200, mimetype='application/json')

    return resp

if __name__ == "__main__":
    app.run()
