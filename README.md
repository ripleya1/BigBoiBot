# BigBoiBot
Just a fun lil bot. Features include: sending reminders, which are backed up in a JSON file, sending the weather (in the US), "fixing" Twitter, Tiktok, and Instagram links to show embeds, and other dumb stuff.

### A Note
This is a v2 update to [the original BigBoiBot](https://github.com/TheGrimlessReaper/BigBoiBot), and is largely a rewrite. For posterity, the [Roadmap section](https://github.com/ripleya1/BigBoiBot/blob/main/README.md#v2-roadmap) includes some of the changes I planned to make.

## Run it yourself
For Big Boi Bot to run, you need to:
- Put the proper info into a [`configu.txt`](configu.txt) file in the same directory as the Python script file.
    - Playing: the playing message that shows up on the bot's profile when it's running.
    - Fix twitter links: whether or not twitter links with videos get "fixed" by replacing the Twitter/X URL with a BetterTwitFix URL. Set to true by default.
    - Fix tiktok links: whether or not tiktok links get "fixed" by replacing the Tiktok URL with a vxtiktok URL. Set to true by default.
    - Fix instagram links is whether or not Instagram links get "fixed" by replacing the Instagram URL with a InstaFix URL. Set to true by default.
- Put your bot token in a `token.txt` file in the same directory as the Python script file.
    - Do likewise with the Google Maps API Key in a `mapskey.txt` file.
- Optional: Replace the directory variable on [line 23](https://github.com/ripleya1/BigBoiBot/blob/main/bot.py#L23) where Python reads the .txt and .json files with your own.
    - This should not be necessary in most cases, but if Python for some reason is not reading the your files, this is a good place to start troubleshooting.
- Note that a `reminders.json` file will be created for you in the directory on the first run of the bot.
- Note that dependencies are included in the [`requirements.txt`](requirements.txt) file.
    - You can install these automatically by running `pip install -r requirements.txt` when in the directory.

## Libraries
### Discord.py
Made using [Discord.py](https://discordpy.readthedocs.io/en/latest/index.html). ([Github](https://github.com/Rapptz/discord.py))

### Weather.gov API
Weather provided by the [weather.gov API](https://www.weather.gov/documentation/services-web-api).
Using [this wrapper](https://github.com/paulokuong/noaa).

### Google Maps API
Geocoding provided by [Google Maps API](https://cloud.google.com/maps-platform/#get-started).
Using [this wrapper](https://github.com/googlemaps/google-maps-services-python).

### BetterTwitFix
Uses [BetterTwitFix](https://github.com/dylanpdx/BetterTwitFix) to fix Twitter/X URLs.

### vxtiktok
Uses [vxtiktok](https://github.com/dylanpdx/vxtiktok) to fix Tiktok URLs.

### InstaFix
Uses [InstaFix](https://github.com/Wikidepia/InstaFix) to fix Instagram URLs.

## v2 Roadmap
- ✔ Migrate bot.py to v2.0 of discord.py. This includes converting all commands to be [slash commands](https://discordpy.readthedocs.io/en/latest/interactions/api.html#discord.app_commands.CommandTree.command).
- ✔ Add better logging to bot.py.
- ✔ Update dependencies.
- ✔ Update vxtwitter functionality.
    - ~~New functionality: Messages can be edited~~ iff the tweet contains a video
    - ~~If detecting if the tweet contains a video is not feasible, edit all messages containing a tweet link.~~
    - If editing messages of other users is not feasible, send a message, similar to the previous implementation. Make this a [reply](https://discordpy.readthedocs.io/en/latest/api.html#discord.MessageType.reply).
