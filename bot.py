# import things
import discord
from discord.ext import commands, tasks
import asyncio
import time
import datetime
import random
import json
from os import path
from sys import version_info
import googlemaps
from noaa_sdk import noaa

# helper function that prints a formatted message with the current time given a string
def printLogMessage(message: str):
    print((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S") + " " + message)

# starting bot
printLogMessage("Bot starting...")
global starttime 
starttime = datetime.datetime.now()

# file paths
directory = "" # modify as needed
jsonPath = directory + "reminders.json"
tokenPath = directory + "token.txt"
configPath = directory + "configu.txt"
mapsKeyPath = directory + "mapskey.txt"

# read bot token
with open(tokenPath, "r") as f:
    token = f.readlines()[0]

# read Google Maps key
with open(mapsKeyPath, "r") as j:
    mapsKey = j.readlines()[0]

# read from config file
with open(configPath, "r") as j:
    lines = j.readlines()
    prefix = (str((lines[0])[7:])).strip()
    playing = (str(lines[1])[8:]).strip()

# initialize variables
# https://discordpy.readthedocs.io/en/latest/api.html#discord.Intents
# TODO: make this more granular later
# ex discord.Intents(guilds = True, members = True)
botIntents = discord.Intents().all()
bot = commands.Bot(command_prefix=prefix, help_command=None, intents=botIntents)
botVersion = 2.00
embedColor = 0x71368a
game = discord.Game(playing)

# create objects for the api clients
n = noaa.NOAA()
m = googlemaps.Client(key=mapsKey)

# runs on bot ready
@bot.event
async def on_ready():
    starttime = datetime.datetime.now()
    game = discord.Game(playing)
    await bot.change_presence(activity=game)
    syncedCommands = await bot.tree.sync()
    printLogMessage("Synced " + str(len(syncedCommands)) + " slash commands")
    printLogMessage("Bot live!")

    # checking JSON for unsent reminders
    printLogMessage("Loading JSON data...")
    # checks if the JSON is greater than 2 bytes (ie has data other than an empty list)
    if path.getsize(jsonPath) > 2:
        with open(jsonPath) as j:
            waitBool = False
            reminderData = []
            reminderData = list(json.load(j))
            # printLogMessage(str(reminderData))
            waitForList = []

            for x in reminderData:
                if int(x['time']) <= int(time.time()): # if the JSON element's time is before or at the current time send the reminder now with a message at the beginning
                    channel = bot.get_channel(int(x["channel"]))
                    await channel.send("This reminder was sent late because of the bot being offline at the time of the original requested reminder time.\n" + str(x["author"]) + " " + str(x["reminder"]))
                    delete_JSON_Element(x)
                elif int(x["time"]) > int(time.time()): # if the JSON element's time is after the current time add it to a list to be run in the background task later
                    waitBool = True
                    waitForList.append(x)

        if(waitBool): # if there are any elements of the JSON whose time is after the current time
            # sorts the list of elements by time
            waitForList.sort(key=sortKey)
            # start background task that sends reminders later
            wait.start(waitForList)
        printLogMessage("JSON data successfully loaded")

    else: # otherwise don't try to open the file because it'll throw an error
        printLogMessage("No JSON data to load")

# resets time counter when bot reconnects
@bot.event
async def on_resumed():
    starttime = datetime.datetime.now()

# prints to console when an interaction takes place
@bot.event
async def on_interaction(interaction: discord.Interaction):
    printLogMessage("/" + interaction.command.name)

# helper function to delete a given JSON element
def delete_JSON_Element(element):
    with open(jsonPath, "r") as j:
        reminderData = list(json.load(j))
        newReminderData = []
        for x in reminderData:
            if x != element:
                newReminderData.append(x)
    with open(jsonPath, "w") as k:
        json.dump(list(newReminderData), k)
    printLogMessage("JSON element successfully deleted")

# background task that is only run once for the reminders that are backed up in the JSON but have not happened yet
@tasks.loop(count=1)
async def wait(remindList):
    for x in remindList:
        await asyncio.sleep(x["time"] - int(time.time()))
        channel = bot.get_channel(int(x["channel"]))
        await channel.send(str(x["author"]) + " " + str(x["reminder"]))
        delete_JSON_Element(x)

# helper function for sorting reminders list
def sortKey(x):
    return x["time"]

# help command
@bot.tree.command(description="Lists all of the available commands.")
async def help(interaction: discord.Interaction):
    commmandList = await bot.tree.fetch_commands()
    embed = discord.Embed(title="Commands", description="Must use a / before all commands", color=embedColor) 
    for command in commmandList:
        embed.add_field(name=command.name, value=command.description, inline=False)
    await interaction.response.send_message(content=None, embed=embed)

# info command
@bot.tree.command(description="Sends info about the bot.")
async def info(interaction: discord.Interaction):
    uptime = datetime.datetime.now() - starttime # timedelta object
    m, s = divmod(uptime.seconds, 60)
    h, m = divmod(m, 60)
    uptimeStr = str("%0d:%02d:%02d:%02d" % (uptime.days, h, m, s))
    embed = discord.Embed(title="Bot info", color=embedColor)
    embed.add_field(name="Ping", value=str(int(bot.latency * 1000)) + " ms", inline=False)
    embed.add_field(name="Uptime", value=uptimeStr, inline=False)
    embed.add_field(name="Version", value="Bot version: " + str(botVersion) + "\nDiscord.py version: " + str(discord.__version__) + " " + str(discord.version_info.releaselevel) + "\nPython version: " + str(version_info.major) + "." + str(version_info.minor) + "." + str(version_info.micro) + " " + str(version_info.releaselevel), inline=False)
    embed.add_field(name="View source code:", value="https://github.com/ripleya1/BigBoiBot", inline=False)
    await interaction.response.send_message(content=None, embed=embed)

# ping command
@bot.tree.command(description="Pings the user.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(str(interaction.user.mention) + " Pong!")

# command that flips a coin
@bot.tree.command(description="Flips a coin.")
async def coinflip(interaction: discord.Interaction):
    result = ["Heads", "Tails"]
    await interaction.response.send_message(random.choice(result) + "!")

# command that searches google
@bot.tree.command(description="Sends a Google search link.")
async def google(interaction: discord.Interaction, search: str):
    search = search.replace(" ", "+") # params are 1:1
    await interaction.response.send_message("https://google.com/search?q=" + search)

# remind command
@bot.tree.command(description="Sends a reminder after a specified amount of time.")
@discord.app_commands.choices(timeunits = [
    discord.app_commands.Choice(name="seconds", value = "s"), 
    discord.app_commands.Choice(name="minutes", value = "m"),
    discord.app_commands.Choice(name="hours", value = "h"),
    discord.app_commands.Choice(name="days", value = "d")
])
async def remind(interaction: discord.Interaction, details: str, timenum: str, timeunits: discord.app_commands.Choice[str]):
    ctime = int(time.time())
    timeunits = timeunits.value
    timenum = int(timenum)
    remindauthor = str(interaction.user.mention)
    remindchannel = interaction.channel.id
    reminder = details

    if (timeunits == "d"):
        finalremindtime = (timenum * 86400) + ctime
        remindtimelongstr = "day"
    elif (timeunits == "h"):
        finalremindtime = (timenum * 3600) + ctime
        remindtimelongstr = "hour"
    elif (timeunits == "m"):
        finalremindtime = (timenum * 60) + ctime
        remindtimelongstr = "minute"
    elif (timeunits == "s"):
        finalremindtime = timenum + ctime
        remindtimelongstr = "second"
    else:
        await interaction.response.send_message("Invalid time.")
        return

    if timenum == 1:
        await interaction.response.send_message("Okay " + remindauthor + ", I'll remind you in " + str(timenum) + " " + remindtimelongstr + ".")
    elif timenum > 1:
        await interaction.response.send_message("Okay " + remindauthor + ", I'll remind you in " + str(timenum) + " " + remindtimelongstr + "s.")
    else:
        await interaction.response.send_message("Invalid time.")
        return

    # TODO: fix this logic
    # add reminder info to JSON
    reminderList = []
    if path.getsize(jsonPath) > 2: # checks if the JSON is greater than 2 bytes (ie has data other than an empty list)
        with open(jsonPath, "r") as j:
            reminderList = list(json.load(j))
    reminderDict = {"reminder": reminder, "author": remindauthor, "time": finalremindtime, "channel": remindchannel}
    reminderList.append(reminderDict)
    with open(jsonPath, "w") as j:
        json.dump(reminderList, j)
    await asyncio.sleep(finalremindtime - ctime)
    await interaction.followup.send(remindauthor + " " + str(reminder))
    delete_JSON_Element(reminderDict)

# helper function for weather command that searches for latitude and longitude of the searched location using the Google Maps API
# returns nothing if invalid location
def search(searchStr):
    # searches for the location's coordinates using the google maps api
    geo = m.geocode(searchStr)
    lat = float(round(geo[0]['geometry']['location']['lat'], 4))
    lon = float(round(geo[0]['geometry']['location']['lng'], 4))
    locArray = [lat, lon]
    return locArray

# helper function for weather command that returns a string for the hourly forecast
def getHourly(lat, lon, len):
    hourlyForecasts = n.points_forecast(lat, lon, hourly=True)
    # datetime object of the current time in GMT
    currentTimeGMT = datetime.datetime.now(datetime.timezone.utc)

    i = 0
    for f in hourlyForecasts['properties']['periods']:
        # datetime object of the time of the object being iterated
        weatherTime = datetime.datetime.strptime(f['startTime'], "%Y-%m-%dT%H:%M:%S%z")
        if currentTimeGMT.strftime("%I %p") == (datetime.datetime.utcfromtimestamp(weatherTime.timestamp()).strftime("%I %p")): # checks if the string of current hour in gmt is equal to the string of the hour of the place in the forecast converted to gmt (so it'll work with any time zone)
            break
        else: # if it's not then add 1 to the index of hourly forecasts to use
            i += 1
    hourlyForecasts = hourlyForecasts['properties']['periods'][i:i + len]
    embedString = ""

    # adding the modified forecast array to the embed
    for f in hourlyForecasts:
        # start time of forecast in the format hour:min am/pm
        t = datetime.datetime.strptime((f['startTime']), "%Y-%m-%dT%H:%M:%S%z").strftime("%I:%M %p")
        embedString += (t + " - " + str(f['temperature']) + "°" + f['temperatureUnit'] + ", " + f['shortForecast'] + "\n")

    # embed string needs to be less than 1024 characters because of a limitation with the Discord API
    embedString = embedString[:1023]
    return embedString

# helper function for weather command that returns a string for the daily forecast
def getDaily(lat, lon, len):
    embedString = ""

    i = 0
    dailyForecasts = n.points_forecast(lat, lon, hourly=False)
    for f in dailyForecasts['properties']['periods']:
        # converting the datetime object we're iterating at to seconds since epoch
        endT = datetime.datetime.strptime(f['endTime'], "%Y-%m-%dT%H:%M:%S%z").timestamp()
        # seconds since epoch of current time
        currentT = datetime.datetime.now().timestamp()
        if endT <= currentT: # if the current time is after the end time of f in dailyForecasts
            # add 1 to the starting index of dailyForecasts
            i += 1
        else: # else stop checking
            break
    dailyForecasts = dailyForecasts['properties']['periods'][i:i + len]

    # adding the modified forecast array to the embed
    for f in dailyForecasts:
        embedString += (f['name'] + " - " + f['detailedForecast'] + "\n")

    # embed string needs to be less than 1024 characters because of a limitation with the Discord API
    embedString = embedString[:1023]
    return embedString

# helper function for weather that returns a string for alerts
def getAlerts(lat, lon, desc):
    embedString = ""
    pointStr = str(lat) + "," + str(lon)
    paramsDict = {'point': pointStr}
    alerts = n.alerts(active=1, **paramsDict)
    activeAlerts = False

    for f in alerts['features']:
        # this is a datetime object of the end time of the alert
        if(f['properties']['ends'] is not None): # checks to make sure that the ends field is not null
            endTObj = datetime.datetime.strptime(f['properties']['ends'], "%Y-%m-%dT%H:%M:%S%z")
        else: # if it is use expires instead
            endTObj = datetime.datetime.strptime(f['properties']['expires'], "%Y-%m-%dT%H:%M:%S%z")
        
        # these are ints of time since epoch
        if(f['properties']['effective'] is not None): # checks to make sure that the effective field is not null
            startT = datetime.datetime.strptime(f['properties']['effective'], "%Y-%m-%dT%H:%M:%S%z").timestamp()
        else: # if it is use onset instead
            startT = datetime.datetime.strptime(f['properties']['onset'], "%Y-%m-%dT%H:%M:%S%z").timestamp()
        
        endT = endTObj.timestamp()
        currentT = datetime.datetime.now().timestamp()
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

    # embed string needs to be less than 1024 characters because of a limitation with the Discord API
    embedString = embedString[:1023]
    return embedString

# command that gives the weather
@bot.tree.command(description="Checks the weather. By default, a forecast summary is sent if no forecasttype is selected.")
@discord.app_commands.choices(forecasttype = [
    discord.app_commands.Choice(name="summary", value = "s"), 
    discord.app_commands.Choice(name="hourly", value = "h"),
    discord.app_commands.Choice(name="daily", value = "d"),
    discord.app_commands.Choice(name="alerts", value = "a")
])
async def weather(interaction: discord.Interaction, location: str, forecasttype: discord.app_commands.Choice[str] = None):
    async with interaction.channel.typing():
        embedString = ""
        if(forecasttype):
            forecasttype = forecasttype.value
        try:
            locArray = search(location)
            lat = locArray[0]
            lon = locArray[1]
        except IndexError: # catch invalid location
            await interaction.response.send_message("Invalid location. Try again.")
            return
        
        if(forecasttype == "h"):
            embed = discord.Embed(title="Hourly forecast for " + location + ":", description="Weather provided by [the National Weather Service](https://www.weather.gov/).", color=0x3498db)
            embedString = getHourly(lat, lon, 13)
            # embed string needs to be less than 1024 characters because of a limitation with the Discord API
            embedString = embedString[:1023]
            embed.add_field(name="Next 12 hours:", value=embedString, inline=False)

        elif(forecasttype == "d"):
            embed = discord.Embed(title="Daily forecast for " + location + ":", description="Weather provided by [the National Weather Service](https://www.weather.gov/).", color=0x3498db)
            embedString = getDaily(lat, lon, 15)
            # embed string needs to be less than 1024 characters because of a limitation with the Discord API
            embedString = embedString[:1023]
            embed.add_field(name="Next 7 days:", value=embedString, inline=False)

        elif(forecasttype == "a"):
            embed = discord.Embed(title="Alerts for " + location + ":", description="Weather provided by [the National Weather Service](https://www.weather.gov/).", color=0x3498db)
            embedString = getAlerts(lat, lon, True)
            # embed string needs to be less than 1024 characters because of a limitation with the Discord API
            embedString = embedString[:1023]
            embed.add_field(name="Alerts:", value=embedString, inline=False)

        elif(forecasttype == "s" or not forecasttype): # summary is the default if type is not specified
            embed = discord.Embed(title="Weather for " + location + ":", description="Weather provided by [the National Weather Service](https://www.weather.gov/).", color=0x3498db)
            # hourly forecast
            embedString = getHourly(lat, lon, 6)
            embed.add_field(name="Next 6 hours:", value=embedString, inline=False)
            # daily forecast
            embedString = getDaily(lat, lon, 6)
            embed.add_field(name="Next 3 days:", value=embedString, inline=False)
            # alerts
            embedString = getAlerts(lat, lon, False)
            # embed string needs to be less than 1024 characters because of a limitation with the Discord API
            embedString = embedString[:1023]
            embed.add_field(name="Alerts:", value=embedString, inline=False)
        
        if(forecasttype not in ["h", "d", "a", "s"] and forecasttype):
            await interaction.response.send_message("Invalid type. Valid types include: hourly, daily, alerts, summary.") # TODO: make a more interesting error message
        else:
            embed.add_field(name="More weather information:", value="Visit [weather.gov](https://forecast.weather.gov/MapClick.php?lat=" + str(lat) + "&lon=" + str(lon) + ").", inline=False)
            await interaction.response.send_message(content=None, embed=embed)

# DEPRECATED
# on message sent
# @bot.event
# async def on_message(ctx):
#     #checking if the author is not the bot
#     if ctx.author != bot.user:
#         await bot.process_commands(ctx)
#         #check for twitter link somewhere in message
#         #replaces https://twitter.com with https://fxtwitter.com in a message
#         if "https://twitter.com" in ctx.content:
#             linkTemp = ctx.content
#             #takes off the front part of the message before the link
#             while linkTemp[:19] != "https://twitter.com":
#                 linkTemp = linkTemp[1:]
#             linkTemp2 = linkTemp
#             c = 0
#             #takes off the last part of the message after the link
#             while not linkTemp[c : c + 1].isspace() and not c == len(linkTemp):
#                 c += 1
#             linkTemp = linkTemp[:c]
#             #adds fx to the twitter url and takes off the space left at the end
#             linkTemp = linkTemp[:8] + "fx" + linkTemp[8:]
#             #sends modified link
#             await ctx.channel.send(linkTemp)

# run bot
bot.run(token)
