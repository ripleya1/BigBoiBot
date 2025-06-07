from OSMPythonTools.nominatim import Nominatim
from noaa_sdk import noaa
from datetime import datetime, timezone, UTC

# create objects for the api clients
noaaClient = noaa.NOAA()
nominatim = Nominatim()

descriptionString = "Weather provided by [the National Weather Service](https://www.weather.gov/)."

# helper function to shorten the embed string
# the embed string needs to be less than 1024 characters because of a limitation with the Discord API
def shortenEmbedString(embedString):
    return embedString[:1023]

# helper function for weather command that searches for latitude and longitude of the searched location using the OpenStreetMap API
# returns nothing if invalid location
def search(searchStr):
    # searches for the location's coordinates using the OSM api
    location = nominatim.query(searchStr)
    locationObj = location.toJSON()[0]
    locArray = [locationObj['lat'], locationObj['lon']]
    return locArray

# helper function for weather command that returns a string for the hourly forecast
def getHourly(lat, lon, len):
    hourlyForecasts = noaaClient.points_forecast(lat, lon, hourly=True)
    # datetime object of the current time in GMT
    currentTimeGMT = datetime.now(timezone.utc)

    i = 0
    for f in hourlyForecasts['properties']['periods']:
        # datetime object of the time of the object being iterated
        weatherTime = datetime.strptime(f['startTime'], "%Y-%m-%dT%H:%M:%S%z")
        # checks if the string of current hour in gmt is equal to the string of the hour of the place in the forecast converted to gmt (so it'll work with any time zone)
        if currentTimeGMT.strftime("%I %p") == (datetime.fromtimestamp(weatherTime.timestamp(), UTC).strftime("%I %p")):
            break
        else: # if it's not then add 1 to the index of hourly forecasts to use
            i += 1
    hourlyForecasts = hourlyForecasts['properties']['periods'][i:i + len]
    embedString = ""

    # adding the modified forecast array to the embed
    for f in hourlyForecasts:
        # start time of forecast in the format hour:min am/pm
        t = datetime.strptime((f['startTime']), "%Y-%m-%dT%H:%M:%S%z").strftime("%I:%M %p")
        embedString += (t + " - " + str(f['temperature']) + "°" + f['temperatureUnit'] + ", " + f['shortForecast'] + "\n")

    embedString = shortenEmbedString(embedString)
    return embedString

# helper function for weather command that returns a string for the daily forecast
def getDaily(lat, lon, len):
    embedString = ""

    i = 0
    dailyForecasts = noaaClient.points_forecast(lat, lon, hourly=False)
    for f in dailyForecasts['properties']['periods']:
        # converting the datetime object we're iterating at to seconds since epoch
        endT = datetime.strptime(f['endTime'], "%Y-%m-%dT%H:%M:%S%z").timestamp()
        # seconds since epoch of current time
        currentT = datetime.now().timestamp()
        if endT <= currentT: # if the current time is after the end time of f in dailyForecasts
            # add 1 to the starting index of dailyForecasts
            i += 1
        else: # else stop checking
            break
    dailyForecasts = dailyForecasts['properties']['periods'][i:i + len]

    # adding the modified forecast array to the embed
    for f in dailyForecasts:
        embedString += (f['name'] + " - " + f['detailedForecast'] + "\n")

    embedString = shortenEmbedString(embedString)
    return embedString

# helper function for weather that returns a string for alerts
def getAlerts(lat, lon, desc):
    embedString = ""
    pointStr = str(lat) + "," + str(lon)
    paramsDict = {'point': pointStr}
    alerts = noaaClient.alerts(active=1, **paramsDict)
    activeAlerts = False

    for f in alerts['features']:
        # this is a datetime object of the end time of the alert
        if(f['properties']['ends'] is not None): # checks to make sure that the ends field is not null
            endTObj = datetime.strptime(f['properties']['ends'], "%Y-%m-%dT%H:%M:%S%z")
        else: # if it is use expires instead
            endTObj = datetime.strptime(f['properties']['expires'], "%Y-%m-%dT%H:%M:%S%z")
        
        # these are ints of time since epoch
        if(f['properties']['effective'] is not None): # checks to make sure that the effective field is not null
            startT = datetime.strptime(f['properties']['effective'], "%Y-%m-%dT%H:%M:%S%z").timestamp()
        else: # if it is use onset instead
            startT = datetime.strptime(f['properties']['onset'], "%Y-%m-%dT%H:%M:%S%z").timestamp()
        
        endT = endTObj.timestamp()
        currentT = datetime.now().timestamp()
        if(endT >= currentT and startT <= currentT): # if the current time is before the end time and after the start time of the alert
            activeAlerts = True
            # add the alert to the embed
            embedString += (f['properties']['event'] + " until " + endTObj.strftime("%B %d, %Y at %I:%M %p") + "\n")
            if(desc):
                embedString += (":" + f['properties']['description'] + "\n")

    if(not activeAlerts):
        embedString = "No active alerts."
    if(not desc):
        if(activeAlerts):
            embedString += ("Check your NWS website or local media for more information on these alerts.")

    embedString = shortenEmbedString(embedString)
    return embedString