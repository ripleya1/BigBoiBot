# BigBoiBot
Just a fun lil bot. Features include - sending reminders (which are backed up in a JSON file), sending the weather (in the US), fixing embeds, and other dumb stuff.

### A Note
This is a v2 update to [the original BigBoiBot](https://github.com/TheGrimlessReaper/BigBoiBot), and is largely a rewrite.

## Run it yourself
For Big Boi Bot to run, you need to:
- Put the proper info into a [`configu.txt`](configu.txt) file, which is in the same directory as the Python script file:
    - Playing: The playing message that shows up on the bot's profile when it's running. Set to "" by default.
    - Fixing links: The syntax for link fixes is `Original URL;New URL`. For example - `twitter.com;vxtwitter.com`. If the url has `www.` at the beginning, that must be specified, but `https://` should not be, as it is added to all of the URLs after the fact.
- Put your bot token in a `token.txt` file, which is in the same directory as the Python script file.
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

### OpenStreetMap API
Geocoding for weather provided by the [OpenStreetMap API](https://wiki.openstreetmap.org/wiki/API) and [Nominatim](https://nominatim.openstreetmap.org/ui/search.html).
Using [this wrapper](https://github.com/mocnik-science/osm-python-tools).

### BetterTwitFix
Uses [BetterTwitFix](https://github.com/dylanpdx/BetterTwitFix) by default to fix Twitter/X URLs.

### VixBluesky
Uses [VixBluesky](https://github.com/Lexedia/VixBluesky) by default to fix Bluesky URLs.

### vxtiktok
Uses [vxtiktok](https://github.com/dylanpdx/vxtiktok) by default to fix TikTok URLs.

### InstaFix
Uses [InstaFix](https://github.com/Wikidepia/InstaFix) by default to fix Instagram URLs.

### fxreddit
Uses [fxreddit](https://github.com/MinnDevelopment/fxreddit) by default to fix Reddit URLs.

## Roadmap/Todo
- [x] Make URL replacements fully modular
- [ ] Make the project more Pythonic/modularized (ie make it so the script isn't just one file), and clean up a bit
- [x] Replace Google Maps API with a new API since they're trying to charge me now ([OpenStreetMap](https://github.com/mocnik-science/osm-python-tools))
- [ ] Check perms on Discord dev website
- [ ] Bug Fix: Retry deleting embed if list index out of range