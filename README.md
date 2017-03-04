# AlbumFetchBot
A Reddit bot that automatically scans Discogs, iTunes, and Spotify for music and provides links to each if they exist

## Requirements

* [Python 3](https://www.python.org/downloads/)
 * Installing all modules through pip is recommended
 * [PRAW](http://praw.readthedocs.io)
 * [Discogs_Client](https://github.com/discogs/discogs_client)
 * [iTunesPy](https://github.com/spaceisstrange/itunespy)
 * [Spotipy](https://github.com/plamere/spotipy)

## Usage

Copy/save `AlbumFetchBot.py` to your server/computer, then run the script as normal for the operating system. On the initial boot, the script will explain how to obtain the necessary credentials needed for the bot to operate and then ask for them, namely:

* Reddit
 * username (separate bot account needed)
 * password
 * client ID
 * secret
 * subreddit
 * owner's username (used for Reddit's user-agent)
* Discogs
 * user token
* Misc
 * Refresh rate

Once all information has been obtained, it will be saved for future startups. If you wish to change any of this information, either delete the `credentials.ini` file, or edit it, then restart the bot.
