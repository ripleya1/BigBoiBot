# BigBoiBot
Just a fun lil bot. Features include - sending reminders (which are backed up in a JSON file), sending the weather (in the US), "fixing" Twitter, Tiktok, and Instagram links to show embeds, and other dumb stuff.

### A Note
This is a v2 update to [the original BigBoiBot](https://github.com/TheGrimlessReaper/BigBoiBot), and is largely a rewrite.

## Run it yourself
For Big Boi Bot to run, you need to:
- Put the proper info into a [`configu.txt`](configu.txt) file, which is in the same directory as the Python script file:
    - Playing: The playing message that shows up on the bot's profile when it's running. Set to "" by default.
    - Fix twitter links: Whether or not twitter links get "fixed" by replacing the Twitter/X URL with a [BetterTwitFix](https://github.com/ripleya1/BigBoiBot/blob/main/README.md#bettertwitfix) URL (by default, can be configured using the Twitter fix url config option). Set to 1 by default.
    - Fix tiktok links: Whether or not tiktok links get "fixed" by replacing the Tiktok URL with a [vxtiktok](https://github.com/ripleya1/BigBoiBot/blob/main/README.md#vxtiktok) URL. Set to 1 by default.
    - Fix instagram links: Whether or not Instagram links get "fixed" by replacing the Instagram URL with an [InstaFix](https://github.com/ripleya1/BigBoiBot/blob/main/README.md#instafix) URL. Set to 1 by default.
    - Fix all twitter links: Whether all twitter links get "fixed" (1) or just the ones without embeds or with videos (0). If fix twitter links is set to 0, this does nothing. Set to 1 by default.
    - Twitter fix url: What `twitter` is replaced with in the Twitter url. If fix twitter links is set to 0, this does nothing. Set to `vxtwitter` by default. 
- Put your bot token in a `token.txt` file, which is in the same directory as the Python script file.
    - Do likewise with the Google Maps API Key in a `mapskey.txt` file.
- Optional: Replace the directory variable on [line 23](https://github.com/ripleya1/BigBoiBot/blob/main/bot.py#L23) where Python reads the .txt and .json files with your own.
    - This should not be necessary in most cases, but if Python for some reason is not reading your files, this is a good place to start troubleshooting.
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

## Roadmap
- [ ] Make URL replacements fully modular
- [ ] Make the project more Pythonic/modularized (ie make it so the script isn't just one file), and clean up a bit
- [ ] Replace Google Maps API with a new API since they're trying to charge me now ([OpenStreetMap](https://github.com/mocnik-science/osm-python-tools)?)
- [ ] Check perms on Discord dev website
- [ ] Bug Fix: Retry deleting embed if list index out of range