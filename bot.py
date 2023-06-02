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

# starting bot
print(time.ctime() + " Bot starting...")
starttime = time.time()

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
    starttime = time.time()
    game = discord.Game(playing)
    await bot.change_presence(activity=game)
    syncedCommands = await bot.tree.sync()
    print(time.ctime() + " Synced " + str(len(syncedCommands)) + " slash commands.")
    print(time.ctime() + " Bot live!")

    # checking JSON for unsent reminders
    print("Loading JSON data...")
    # checks if the JSON is greater than 2 bytes (ie has data other than an empty list)
    if path.getsize(jsonPath) > 2:
        with open(jsonPath) as j:
            waitBool = False
            reminderData = []
            reminderData = list(json.load(j))
            print(reminderData)
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
        print("JSON data successfully loaded")

    else: # otherwise don't try to open the file because it'll throw an error
        print("No JSON data to load")

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
    print("Element successfully deleted")

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
@bot.tree.command()
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Commands", description="Must use prefix `" + prefix + "` before command", color=embedColor)
    embed.add_field(name="info", value="Sends bot info.", inline=False)
    embed.add_field(name="ping", value="Pings the user.", inline=False)
    embed.add_field(name="coinflip", value="Flips a coin.", inline=False)
    embed.add_field(name="remind or r", value="Sends a reminder after a user-specified amount of time.\nUsage: `" + prefix + "remind <time><units>; <reminder>`\nSupported units: seconds, minutes, hours, days", inline=False)
    embed.add_field(name="weather or w", value="Sends the weather. Type `" + prefix + "weather help` for usage help.", inline=False)
    embed.add_field(name="google or g", value="Sends Google search link.", inline=False)
    embed.add_field(name="duckduckgo or ddg", value="Sends DuckDuckGo search link.", inline=False)
    await interaction.response.send_message(content=None, embed=embed)

# info command
@bot.command()
async def info(ctx):
    uptimesecs = round(time.time() - starttime)
    m, s = divmod(uptimesecs, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    uptime = "%0d:%02d:%02d:%02d" % (d, h, m, s)
    embed = discord.Embed(title="Bot info", color=embedColor)
    embed.add_field(name="Ping", value=str(int(bot.latency * 1000)) + " ms", inline=False)
    embed.add_field(name="Uptime", value=str(uptime), inline=False)
    embed.add_field(name="Version", value="Bot version: " + str(botVersion) + "\nDiscord.py version: " + str(discord.__version__) + " " + str(discord.version_info.releaselevel) + "\nPython version: " + str(version_info.major) + "." + str(version_info.minor) + "." + str(version_info.micro) + " " + str(version_info.releaselevel), inline=False)
    embed.add_field(name="View source code:", value="https://github.com/TheGrimlessReaper/BigBoiBot", inline=False)
    await ctx.send(content=None, embed=embed)

# ping command
@bot.command()
async def ping(ctx):
    await ctx.send(str(ctx.author.mention) + " Pong!")

# command that flips a coin
@bot.command()
async def coinflip(ctx):
    result = ["Heads", "Tails"]
    await ctx.send(random.choice(result) + "!")

# command that searches google
@bot.command(aliases=["g"])
async def google(ctx, *args):
    search = "{}".format("+".join(args))
    await ctx.send("https://google.com/search?q=" + search)

# command that searches DuckDuckGo
@bot.command(aliases=["ddg"])
async def duckduckgo(ctx, *args):
    search = "{}".format("+".join(args))
    await ctx.send("https://duckduckgo.com/?q=" + search)

# remind command
@bot.command(aliases=["r"])
async def remind(ctx, *args):
    if (args[0] == "help"):
        embed = discord.Embed(title="Remind", description="Reminds users.", color=embedColor)
        embed.add_field(name="Usage:", value="`" + prefix + "remind <time><units>; <reminder>`\nSupported units: seconds, minutes, hours, days", inline=False)
        await ctx.send(content=None, embed=embed)
    else:
        reminder = "{}".format(" ".join(args))
        ctime = int(time.time())
        sep = ";"
        remindtime = str(reminder.split(sep, 2)[0])
        remindtimestr = ''.join([i for i in remindtime if not i.isdigit()])
        remindtimenum = ''.join([i for i in remindtime if i.isdigit()])
        remindtimestr = str(remindtimestr.strip())
        remindtimenum = int(remindtimenum)
        remindauthor = str(ctx.message.author.mention)
        remindchannel = ctx.message.channel.id
        reminder = str((reminder.split(sep, 2)[1]).strip())

        if (remindtimestr == "d" or remindtimestr == "day" or remindtimestr == "days" or remindtimestr == " d" or remindtimestr == " day" or remindtimestr == " days"):
            finalremindtime = (remindtimenum * 86400) + ctime
            remindtimelongstr = "day"
        elif (remindtimestr == "h" or remindtimestr == "hour" or remindtimestr == "hours" or remindtimestr == " h" or remindtimestr == " hour" or remindtimestr == " hours"):
            finalremindtime = (remindtimenum * 3600) + ctime
            remindtimelongstr = "hour"
        elif (remindtimestr == "m" or remindtimestr == "minute" or remindtimestr == "minutes" or remindtimestr == " m" or remindtimestr == " minute" or remindtimestr == " minutes"):
            finalremindtime = (remindtimenum * 60) + ctime
            remindtimelongstr = "minute"
        elif (remindtimestr == "s" or remindtimestr == "second" or remindtimestr == "seconds" or remindtimestr == " s" or remindtimestr == " second" or remindtimestr == " seconds"):
            finalremindtime = remindtimenum + ctime
            remindtimelongstr = "second"
        else:
            await ctx.send("Invalid time.")
            return

        if remindtimenum == 1:
            await ctx.send("Okay " + remindauthor + ", I'll remind you in " + str(remindtimenum) + " " + remindtimelongstr + ".")
        elif remindtimenum > 1:
            await ctx.send("Okay " + remindauthor + ", I'll remind you in " + str(remindtimenum) + " " + remindtimelongstr + "s.")
        else:
            await ctx.send("Invalid time.")
            return

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
        await ctx.send(remindauthor + " " + str(reminder))
        delete_JSON_Element(reminderDict)

# prints to console when the bot disconnects
@bot.event
async def on_disconnect():
    while(bot.is_closed()):
        print(time.ctime() + " Client disconnected")
        await asyncio.sleep(5)

# prints to console when bot reconnects
@bot.event
async def on_resumed():
    starttime = time.time()
    print(time.ctime() + " Client reconnected!")

# helper function for weather command that searches for latitude and longitude of the searched location using the Google Maps API
def search(searchArray):
    search = ""

    for x in searchArray:
        search += str(x) + " "

    # searches for the location's coordinates using the google maps api
    geo = m.geocode(search)
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
                print("desc")
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
@bot.command(aliases=["w"])
async def weather(ctx, *args):
    if args:
        async with ctx.channel.typing():
            embedString = ""
            temp = ""

            if(args[0].lower() == "hourly" or args[0].lower() == "hour" or args[0].lower() == "daily" or args[0].lower() == "day" or args[0].lower() == "weekly" or args[0].lower() == "alerts" or args[0].lower() == "alert" or args[0].lower() == "help"):
                temp = args[0].lower()
                args = args[1:]

            # there won't be anything in args if the user types help which will throw an error otherwise
            if(args):
                locArray = search(args)
                lat = locArray[0]
                lon = locArray[1]
                searchStr = ""
            for i in args:
                searchStr += i + " "

            if(temp == "hourly" or temp == "hour"):
                embed = discord.Embed(title="Hourly forecast for " + searchStr + ":", description="Weather provided by [the National Weather Service](https://www.weather.gov/).", color=0x3498db)
                embedString = getHourly(lat, lon, 13)
                # embed string needs to be less than 1024 characters because of a limitation with the Discord API
                embedString = embedString[:1023]
                embed.add_field(name="Next 12 hours:", value=embedString, inline=False)

            elif(temp == "daily" or temp == "day" or temp == "weekly"):
                embed = discord.Embed(title="Daily forecast for " + searchStr + ":", description="Weather provided by [the National Weather Service](https://www.weather.gov/).", color=0x3498db)
                embedString = getDaily(lat, lon, 15)
                # embed string needs to be less than 1024 characters because of a limitation with the Discord API
                embedString = embedString[:1023]
                embed.add_field(name="Next 7 days:", value=embedString, inline=False)

            elif(temp == "alerts" or temp == "alert"):
                embed = discord.Embed(title="Alerts for " + searchStr + ":", description="Weather provided by [the National Weather Service](https://www.weather.gov/).", color=0x3498db)
                embedString = getAlerts(lat, lon, True)
                # embed string needs to be less than 1024 characters because of a limitation with the Discord API
                embedString = embedString[:1023]
                embed.add_field(name="Alerts:", value=embedString, inline=False)

            elif(temp == "help"):
                embed = discord.Embed(title="Weather Help:", description="Usage for the Weather command.\nTyping weather [location] sends all commands listed at once (with more limited details).\nTyping weather [command] [location] sends that command (with more details).", color=0x3498db)
                embed.add_field(name="Hourly:", value="Sends the hourly forecast for up to 12 hours after the current time.", inline=False)
                embed.add_field(name="Daily:", value="Sends the daily forecast for up to 3 days after the current time.", inline=False)
                embed.add_field(name="Alerts:", value="Sends all currently active alerts.", inline=False)

            else: # forecast summary if no other args
                embed = discord.Embed(title="Weather for " + searchStr + ":", description="Weather provided by [the National Weather Service](https://www.weather.gov/).", color=0x3498db)
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
            if(temp != "help"):
                embed.add_field(name="More weather information:", value="Visit [weather.gov](https://forecast.weather.gov/MapClick.php?lat=" + str(lat) + "&lon=" + str(lon) + ").", inline=False)
            await ctx.send(content=None, embed=embed)

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
