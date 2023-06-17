# BigBoiBot
Just a fun lil bot. Features include: sending reminders, which are backed up in a JSON file, sending the weather (in the US), and other dumb stuff.

This is a v2 update to [the original BigBoiBot](https://github.com/TheGrimlessReaper/BigBoiBot), and is mostly a rewrite. A list of future updates is included in the Roadmap section below.

## Run it yourself
For Big Boi Bot to run, you need to:
- put the proper info into a configu.txt file in the same directory as the Python script file (sample file provided)
    - Playing is the playing message that shows up on the bot's profile when it's running
    - Fix twitter links is whether or not twitter links with videos get "fixed" by replacing the Twitter URL with a vxtwitter URL, this is set to true by default
    - Fix tiktok links is whether or not tiktok links get "fixed" by replacing the Tiktok URL with a vxtiktok URL, this is set to true by default
    - Fix instagram links is whether or not instagram links get "fixed" by replacing the instagram URL with a ddinstagram URL, this is set to true by default
- put your bot token in a token.txt file in the same directory as the Python script file
- do likewise with the Google Maps API Key in a mapskey.txt file
- replace the directory variable on line 19 where Python reads the txt and json files with your own
- note that a reminders.json file will be created for you in the directory on the first run of the bot 
- note that dependencies are included in the requirements.txt file

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

## vxtiktok
Uses [vxtiktok](https://github.com/dylanpdx/vxtiktok) to fix Tiktok URLs.

## InstaFix
Uses [InstaFix](https://github.com/Wikidepia/InstaFix) to fix Instagram URLs.

## Roadmap
- ✔ Migrate bot.py to v2.0 of discord.py. This includes converting all commands to be [slash commands](https://discordpy.readthedocs.io/en/latest/interactions/api.html#discord.app_commands.CommandTree.command).
- ✔ Add better logging to bot.py.
- ✔ Update dependencies.
- ✔ Update vxtwitter functionality.
    - ~~New functionality: Messages can be edited~~ iff the tweet contains a video
    - ~~If detecting if the tweet contains a video is not feasible, edit all messages containing a tweet link.~~
    - If editing messages of other users is not feasible, send a message, similar to the previous implementation. Make this a [reply](https://discordpy.readthedocs.io/en/latest/api.html#discord.MessageType.reply).
- ❌ Add functionality for the [OWL API](https://develop.battle.net/documentation/owl/community-apis). 
    - If someone makes a Python wrapper for it before I get to it I'll probably use that.
