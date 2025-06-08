# import things
import discord
from discord.ext import commands, tasks
import asyncio
from time import time
from datetime import datetime
from random import choice
from json import dump, load
from os import path
from sys import version_info
import lib.weather as weatherLib

# helper function that prints a formatted message with the current time given a string
def printLogMessage(message: str):
    print((datetime.now()).strftime("%Y-%m-%d %H:%M:%S") + " " + message)

# starting bot
printLogMessage("Bot starting...")
startTime = datetime.now()

# file paths
directory = "" # modify as needed
jsonPath = directory + "reminders.json"
tokenPath = directory + "token.txt"
configPath = directory + "configu.txt"

# read bot token
with open(tokenPath, "r") as f:
    token = f.readlines()[0]

# helper function to return the contents of a given line from the lines of the config file
def readConfigLines(lines: list[str], lineNum: int):
    return str(lines[lineNum].rsplit("=")[1]).strip() # return everything after the last = in the line

URLFixList = [{"URL": "", "FixURL": ""}]
# read from config file
with open(configPath, "r") as j:
    lines = j.readlines()
    playing = readConfigLines(lines, 0)
    lineNum = 1
    URLFixList.pop()
    while(lineNum <= len(lines) - 1): # add to URLFix list until we hit the end of the file
        # in the config file this looks like: URL;FixURL
        URLFixList.append({'URL': "https://" + str(lines[lineNum].rsplit(";")[0]).strip(), 'FixURL': "https://" + str(lines[lineNum].rsplit(";")[1]).strip()}) # add https:// to both URLs
        lineNum += 1

# initialize variables
botIntents = discord.Intents(messages = True, message_content = True, guilds = True) # https://discordpy.readthedocs.io/en/stable/api.html#discord.Intents
bot = commands.Bot(command_prefix=None, intents=botIntents)
botVersion = 2.50
defaultEmbedColor = 0x71368a
game = discord.Game(playing)

# runs on bot ready
# https://discordpy.readthedocs.io/en/stable/api.html#discord.on_ready
@bot.event
async def on_ready():
    startTime = datetime.now()
    game = discord.Game(playing)
    await bot.change_presence(activity=game)
    syncedCommands = await bot.tree.sync()
    printLogMessage("Synced " + str(len(syncedCommands)) + " slash commands")
    printLogMessage("Bot live!")
    for url in URLFixList:
        printLogMessage("Fixing " + url['URL'] + " links using " + url['FixURL'])
    try:
        await checkRemindersJson()
    except IOError: # if the file isn't there don't bother checking it and make one instead
        open("reminders.json", "x")
        printLogMessage("Created new reminders.json file")
        printLogMessage("No JSON data to load")

# resets time counter when bot reconnects
@bot.event
async def on_resumed():
    startTime = datetime.now()

# prints to console when an interaction takes place
@bot.event
async def on_interaction(interaction: discord.Interaction):
    printLogMessage("/" + interaction.command.name)

# help command
@bot.tree.command(description="Lists all of the available commands.")
async def help(interaction: discord.Interaction):
    commmandList = await bot.tree.fetch_commands()
    embed = discord.Embed(title="Commands", description="Must use a / before all commands", color=defaultEmbedColor) 
    for command in commmandList:
        embed.add_field(name=command.name, value=command.description, inline=False)
    await interaction.response.send_message(content=None, embed=embed)

# info command
@bot.tree.command(description="Sends info about the bot.")
async def info(interaction: discord.Interaction):
    uptime = datetime.now() - startTime # timedelta object
    m, s = divmod(uptime.seconds, 60)
    h, m = divmod(m, 60)
    uptimeStr = str("%0d:%02d:%02d:%02d" % (uptime.days, h, m, s))
    embed = discord.Embed(title="Bot info", color=defaultEmbedColor)
    embed.add_field(name="Ping", value=str(int(bot.latency * 1000)) + " ms", inline=False)
    embed.add_field(name="Uptime", value=uptimeStr, inline=False)
    embed.add_field(name="Version", 
                    value="Bot version: " + str(botVersion) 
                    + "\nDiscord.py version: " + str(discord.__version__) + " " + str(discord.version_info.releaselevel)
                    + "\nPython version: " + str(version_info.major) + "." + str(version_info.minor) + "." + str(version_info.micro)
                    + " " + str(version_info.releaselevel), inline=False)
    embed.add_field(name="View source code:", value="https://github.com/ripleya1/BigBoiBot", inline=False)
    await interaction.response.send_message(content=None, embed=embed)

# ping command
@bot.tree.command(description="Pings the user.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(str(interaction.user.mention) + " Pong!")

# coinflip command
@bot.tree.command(description="Flips a coin.")
async def coinflip(interaction: discord.Interaction):
    result = ["Heads", "Tails"]
    await interaction.response.send_message(choice(result) + "!")

# google command
@bot.tree.command(description="Sends a Google search link.")
@discord.app_commands.describe(search="What you want to search.")
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
@discord.app_commands.describe(
    details="The message sent when being reminded.",
    timenum="The number of the amount of time until the reminder is sent.",
    timeunits="The units of time of the amount of time until the reminder is sent.")
async def remind(interaction: discord.Interaction, details: str, timenum: str, timeunits: discord.app_commands.Choice[str]):
    cTime = int(time())
    timeUnitsVal = timeunits.value
    timeNumInt = int(timenum)
    remindAuthor = str(interaction.user.mention)
    remindChannel = interaction.channel.id
    reminder = details

    if (timeUnitsVal == "d"):
        finalRemindTime = (timeNumInt * 86400) + cTime
        remindTimeLongStr = "day"
    elif (timeUnitsVal == "h"):
        finalRemindTime = (timeNumInt * 3600) + cTime
        remindTimeLongStr = "hour"
    elif (timeUnitsVal == "m"):
        finalRemindTime = (timeNumInt * 60) + cTime
        remindTimeLongStr = "minute"
    elif (timeUnitsVal == "s"):
        finalRemindTime = timeNumInt + cTime
        remindTimeLongStr = "second"
    else:
        await interaction.response.send_message("Invalid time.")
        return

    if timeNumInt == 1:
        await interaction.response.send_message("Okay " + remindAuthor + ", I'll remind you in " + str(timeNumInt) + " " + remindTimeLongStr + ".")
    elif timeNumInt > 1:
        await interaction.response.send_message("Okay " + remindAuthor + ", I'll remind you in " + str(timeNumInt) + " " + remindTimeLongStr + "s.")
    else:
        await interaction.response.send_message("Invalid time.")
        return

    # add reminder info to JSON
    reminderList = []
    if jsonIsEmpty(jsonPath):
        with open(jsonPath, "r") as j:
            reminderList = list(load(j))
    reminderDict = {"reminder": reminder, "author": remindAuthor, "time": finalRemindTime, "channel": remindChannel}
    reminderList.append(reminderDict)
    with open(jsonPath, "w") as j:
        dump(reminderList, j)
    await asyncio.sleep(finalRemindTime - cTime)
    await interaction.followup.send(remindAuthor + " " + str(reminder))
    delete_JSON_Element(reminderDict)

# helper function for on_ready that checks the reminders json for any remaining reminders,
# sends the reminder if the time for it has passed,
# and waits to send the reminder until the time for it happens if it has not
# note that if the bot is stopped and then restarted in quick succession and there are reminders in the json
# on_ready will halt for a bit and this function will take longer to start running
async def checkRemindersJson():
    # checking JSON for unsent reminders
    printLogMessage("Loading JSON data...")
    # checks if the JSON is greater than 2 bytes (ie has data other than an empty list)
    if path.getsize(jsonPath) > 2:
        with open(jsonPath) as j:
            waitFlag = False
            reminderData = []
            reminderData = list(load(j))
            waitForList = []

            for reminder in reminderData:
                if int(reminder['time']) < int(time()): # if the JSON element's time is before the current time send the reminder now with a message at the beginning
                    channel = bot.get_channel(int(reminder["channel"]))
                    await channel.send(str(reminder["author"]) + " " + str(reminder["reminder"])
                                        + "\n\nNote that this reminder was sent late because of the bot being offline at the time of the original requested reminder time.")
                    delete_JSON_Element(reminder)
                elif int(reminder["time"]) > int(time()): # if the JSON element's time is after the current time add it to a list to be run in the background task later
                    waitFlag = True
                    waitForList.append(reminder)

        if(waitFlag): # if there are any elements of the JSON whose time is after the current time
            # sorts the list of elements by time
            waitForList.sort(key=sortKey)
            # start background task that sends reminders later
            wait.start(waitForList)
        printLogMessage("JSON data successfully loaded")

    else: # otherwise don't try to open the file because it'll throw an error
        printLogMessage("No JSON data to load")

# background task that is only run once for the reminders that are backed up in the JSON but have not happened yet
@tasks.loop(count=1)
async def wait(remindList):
    for x in remindList:
        await asyncio.sleep(x["time"] - int(time()))
        channel = bot.get_channel(int(x["channel"]))
        await channel.send(str(x["author"]) + " " + str(x["reminder"]))
        delete_JSON_Element(x)

# helper function that checks if the JSON is greater than 2 bytes (ie has data other than an empty list)
def jsonIsEmpty(jsonPath):
    return path.getsize(jsonPath) > 2

# helper function to delete a given JSON element
def delete_JSON_Element(element):
    with open(jsonPath, "r") as j:
        reminderData = list(load(j))
        newReminderData = []
        for x in reminderData:
            if x != element:
                newReminderData.append(x)
    with open(jsonPath, "w") as k:
        dump(list(newReminderData), k)
    printLogMessage("JSON element successfully deleted")

# helper function that sorts the reminders list by time
def sortKey(x):
    return x["time"]

# command that gives the weather
@bot.tree.command(description="Checks the weather. By default, a forecast summary is sent if no forecasttype is selected.")
@discord.app_commands.choices(forecasttype = [
    discord.app_commands.Choice(name="summary", value = "s"), 
    discord.app_commands.Choice(name="hourly", value = "h"),
    discord.app_commands.Choice(name="daily", value = "d"),
    discord.app_commands.Choice(name="alerts", value = "a")])
@discord.app_commands.describe(
    location = "The location that the forecast is for.", 
    forecasttype = "The type of forecast.")
async def weather(interaction: discord.Interaction, location: str, forecasttype: discord.app_commands.Choice[str] = None):
    async with interaction.channel.typing():
        embed = discord.Embed()
        embedString = ""
        forecastTypeVal = ""
        if(forecasttype):
            forecastTypeVal = forecasttype.value
        try:
            locArray = weatherLib.search(location)
            lat = locArray[0]
            lon = locArray[1]
        except IndexError: # catch invalid location
            await interaction.response.send_message("Invalid location. Try again.")
            return
        
        if(not forecastTypeVal == "s" or not forecasttype): # note that this is the default
            embed = discord.Embed(title="Weather for " + location + ":", description=weatherLib.descriptionString, color=weatherLib.weatherEmbedColor)
            # hourly forecast
            embedString = weatherLib.getHourly(lat, lon, 6)
            embed.add_field(name="Next 6 hours:", value=embedString, inline=False)
            # daily forecast
            embedString = weatherLib.getDaily(lat, lon, 6)
            embed.add_field(name="Next 3 days:", value=embedString, inline=False)
            # alerts
            embedString = weatherLib.getAlerts(lat, lon, False)
            embedString = weatherLib.shortenEmbedString(embedString)
            embed.add_field(name="Alerts:", value=embedString, inline=False)

        elif(forecastTypeVal == "h"):
            embed = discord.Embed(title="Hourly forecast for " + location + ":", description=weatherLib.descriptionString, color=weatherLib.weatherEmbedColor)
            embedString = weatherLib.getHourly(lat, lon, 13)
            embedString = weatherLib.shortenEmbedString(embedString)
            embed.add_field(name="Next 12 hours:", value=embedString, inline=False)

        elif(forecastTypeVal == "d"):
            embed = discord.Embed(title="Daily forecast for " + location + ":", description=weatherLib.descriptionString, color=weatherLib.weatherEmbedColor)
            embedString = weatherLib.getDaily(lat, lon, 15)
            embedString = weatherLib.shortenEmbedString(embedString)
            embed.add_field(name="Next 7 days:", value=embedString, inline=False)

        elif(forecastTypeVal == "a"):
            embed = discord.Embed(title="Alerts for " + location + ":", description=weatherLib.descriptionString, color=weatherLib.weatherEmbedColor)
            embedString = weatherLib.getAlerts(lat, lon, True)
            embedString = weatherLib.shortenEmbedString(embedString)
            embed.add_field(name="Alerts:", value=embedString, inline=False)
        
        embed.add_field(name="More weather information:", value="Visit [weather.gov](https://forecast.weather.gov/MapClick.php?lat=" + str(lat) + "&lon=" + str(lon) + ").", inline=False)
        await interaction.response.send_message(content=None, embed=embed)

# on message sent, tries to find a URL from the fix list, 
# and if found, replaces that URL with the corresponding one in the list
# https://discordpy.readthedocs.io/en/stable/api.html#discord.on_message
@bot.event
async def on_message(message: discord.Message):
    if message.author != bot.user: # make sure that the author is not the bot itself
        i, urlIndex = -1, -1
        for url in URLFixList:
            i += 1
            urlIndex = message.content.find(url['URL'])
            if(urlIndex > -1):
                print(message.content, url['URL'], urlIndex)
                break
        if(urlIndex > -1):
            await extractAndReplaceURL(message, URLFixList[i]['URL'], URLFixList[i]['FixURL'], urlIndex)
            printLogMessage("Fixed a " + URLFixList[i]['URL'] + " link")

# helper function for on_message that extracts a URL from a message, replaces it with another URL, 
# cuts off the rest of the message, and sends the extracted URL as a silent reply to the original
async def extractAndReplaceURL(message: discord.Message, oldURL: str, replacementURL: str, strIndex: int):
    # take off the front part of the message before the link    
    linkTemp = message.content[strIndex:]
    linkTemp = linkTemp.replace(oldURL, replacementURL)
    # take off the last part of the message after the link
    strIndex = linkTemp.find(" ")
    if(strIndex != -1):
        linkTemp = linkTemp[:strIndex]
    else:
        linkTemp = linkTemp
    newMsg = await message.reply(content = linkTemp, silent = True, mention_author = False) # send a silent message with the fixed link
    await asyncio.sleep(1) # wait for the embed to load
    await message.edit(suppress=True) # remove the embed of the previous message
    return newMsg

# run bot
bot.run(token)
