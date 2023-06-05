# BigBoiBot
Just a fun lil bot. Features include: sending reminders, which are backed up in a JSON file, sending the weather (in the US), and other dumb stuff.

This is a v2 update to [the original BigBoiBot](https://github.com/TheGrimlessReaper/BigBoiBot), and is mostly a rewrite. A list of future updates is included in the Roadmap section below.

## Run it yourself
For Big Boi Bot to run, you need to put the proper info into a configu.txt file in the same directory as the Python script file (sample file provided), put your bot token in a token.txt file in the same directory as the Python script file, and likewise with the Google Maps API Key in a mapskey.txt file. A reminders.json file with nothing inside of it except for a two closed brackets ([]). Replace the directory variable on line 19 where Python reads the txt and json files with your own. Dependencies are included in the requirements.txt file.

## Discord.py
Made using [Discord.py](https://discordpy.readthedocs.io/en/latest/index.html). ([Github](https://github.com/Rapptz/discord.py))

## Weather.gov API
Weather provided by the [weather.gov API](https://www.weather.gov/documentation/services-web-api).
Using [this wrapper](https://github.com/paulokuong/noaa).

## Google Maps API
Geocoding provided by [Google Maps API](https://cloud.google.com/maps-platform/#get-started).
Using [this wrapper](https://github.com/googlemaps/google-maps-services-python).

## TwitFix
Uses [BetterTwitFix](https://github.com/dylanpdx/BetterTwitFix) to fix Twitter URLs.

## Roadmap
- ✔ Migrate bot.py to v2.0 of discord.py. This includes converting all commands to be [slash commands](https://discordpy.readthedocs.io/en/latest/interactions/api.html#discord.app_commands.CommandTree.command).
- ✔ Add better logging to bot.py.
- ✔ Update dependencies.
- ❌ Update vxtwitter functionality.
    - New functionality: Messages can be edited iff the tweet contains a video
    - If detecting if the tweet contains a video is not feasible, edit all messages containing a tweet link.
    - If editing messages of other users is not feasible, send a message, similar to the previous implementation. Make this a [reply](https://discordpy.readthedocs.io/en/latest/api.html#discord.MessageType.reply).
- ❌ Add functionality for the [OWL API](https://develop.battle.net/documentation/owl/community-apis). 
    - If someone makes a Python wrapper for it before I get to it I'll probably use that.
