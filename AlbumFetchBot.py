#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  AlbumFetchBot.py
#  
#  Copyright 2017 Keaton Brown <linux.keaton@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

########################################################################
#                                                                      #
#    Definitions                                                       #
#                                                                      #
########################################################################

def searchDiscogs(artist,song):
    """
    Return the url for what we assume is the album.
    Gets the CD from the title search, then attempts
    to see if the song is in the CD's tracklist.
    
    Should be used in a try statement, as an error
    will indicate that the song wasn't found on any
    album
    """
    print("Searching Discogs")
    search = D.search(artist+" "+song)
    i=0
    while True:
        bestGuess = search[i]
        if song.lower() in [ s.title.lower() for s in bestGuess.tracklist ]:
            break
        else:
            i += 1
    return bestGuess.data["uri"]

def makeUseable(v):
    """
    itunespy returns an unusable list, this fixes it.
    """
    d = {}
    broken = str(v[0]).splitlines()
    for result in broken:
        if result:
            index,value = result.split(":",1)
            d[index] = value
    return d

def searchITunes(artist,song):
    """
    Return the url for what we assume is the song.
    
    Should be used in a try statement, as an error
    will indicate that the song wasn't found on 
    iTunes
    """
    print("Searching iTunes")
    search = itunespy.search(artist+" "+song)
    parsed = makeUseable(search)
    return parsed["collection_view_url"]

def searchSpotify(artist,song):
    """
    Return the url for what we assume is the album.
    
    Should be used in a try statement, as an error
    will indicate that the song wasn't found on 
    Spotify
    """
    print("Searching Spotify")
    search = S.search(artist+" "+song)
    return search['tracks']['items'][0]['album']['external_urls']['spotify']

def createText(submission,artist,song):
    """
    Make the body of the message
    """
    comment = "**"+artist.title()+" - "+song.title()+"**\n\n"
    fails = 0
    try:
        comment += "* [View on Discogs]("+searchDiscogs(artist,song)+")\n"
    except:
        fails += 1
    try:
        comment += "* [Purchase on iTunes]("+searchITunes(artist,song)+")\n"
    except:
        fails += 1
    try:
        comment += "* [Stream on Spotify]("+searchSpotify(artist,song)+")\n"
    except:
        fails += 1
    if fails == 3: # Number of services to search - update this if more are added!
        raise Exception
    comment += botFlair
    return comment

def checkMessages():
    """
    Check inbox for Edit and Deletion requests.
    
    Automatically skips over user mentions and comment replies
    """
    for reply in R.inbox.comment_replies():
        reply.mark_read()
    for mention in R.inbox.mentions():
        mention.mark_read()
    
    for message in R.inbox.unread():
        try:
            postID = re.match("[a-z0-9]{7}$",message.body[:7]).group()
            post = R.comment(id=postID)
        except:
            print("Message from /u/"+message.author.name+" failed:\n\n"+message.body)
            message.mark_read()
            continue
        print("Got a message from /u/"+message.author.name)
        try:
            if post.author.name.lower() != creds["R"]["u"].lower():
                print("Not a comment I made. Skipping.")
                message.reply("You provided an invalid comment ID. Please do "
                              "not edit the ID when submitting a request.")
                message.mark_read()
                continue
        except:
            print("Not a comment I made. Skipping.")
            message.reply("You provided an invalid comment ID. Please do "
                          "not edit the ID when submitting a request.")
            message.mark_read()
            continue
        if message.author.name != R.submission(id=post.submission.id).author.name:
            print("Not OP. Skipping.")
            message.reply("You are not the OP of that post, so you cannot "
                          "request that action.")
            message.mark_read()
            continue
        if message.subject == "Edit autofetch":
            print("Edit requested.")
            parts = re.search("Artist: (.*?)\n\nSong: (.*)",message.body)
            try:
                if not (parts.group(1) or parts.group(2)):
                    message.reply("Please enter both an artist and a song name.")
                    message.mark_read()
                    print("Incorrect formatting. Skipping.")
                    continue
                newComment = createText(R.submission(id=post.submission.id),parts.group(1),parts.group(2)).replace("__POSTID__",postID)
                post.edit(newComment)
                print("Edit success")
                message.reply("Autofetch was successfully edited")
            except:
                print("Edit failed")
                message.reply("The post failed to be edited. Ensure the song "
                              "information was entered correctly, then check "
                              "if the song/album exists on Discogs, iTunes, "
                              "and/or Spotify. If problems persist, contact "
                              "the moderators.")
        elif message.subject == "Delete autofetch":
            print("Delete request.")
            post.delete()
            message.reply("Autofetch was successfully deleted.")
        print("Message reply sent.")
        message.mark_read()

def checkSubreddit(sub):
    """
    Check the new submissions to the subreddit, comment accordingly
    """
    for submission in R.subreddit(sub).new():
        # Ignore submissions older than one day
        # Since the bot hides posts as it completes them, it might
        # pull some really old posts as "new" after a while.
        if time.time() - submission.created_utc > 24*60*60:
            continue
        title = re.search("(.*?) - (.*)",submission.title)
        try:
            artist = title.group(1)
            song = title.group(2)
            print("Read '"+submission.title+"' with the following information:\n"
                  "  artist: "+artist+"\n"
                  "  song: "+song)
        except:
            print("Submission '"+submission.title+"' failed to match song title conventions. Skipping")
            continue
        try:
            comment = createText(submission,artist,song)
        except:
            comment =("Failed to find song information for:\n\n* Artist: "+artist+"\n* Song: "+song+"\n\n"+
                      "Use the links below to edit this post with the correct information or to delete this comment."+botFlair)
        C = submission.reply(comment)
        C.edit(C.body.replace("__POSTID__",C.id))
        submission.hide() # Prevents the bot from replying to posts it already replied to
        print("Replied with:\n"+comment)
        

########################################################################
#                                                                      #
#    Script Startup                                                    #
#                                                                      #
########################################################################

try:
    mods = ["praw","os","time","re","discogs_client","itunespy","spotipy"]
    for mod in mods:
        print("Importing "+mod)
        exec("import "+mod)
except:
    exit(mod+" was not found. Install "+mod+" with pip to continue.")

try:
    creds = {}
    ###############
    creds["R"] = {}
    creds["R"]["u"] = os.environ.get("RUSER")
    creds["R"]["p"] = os.environ.get("RPASS")
    creds["R"]["c"] = os.environ.get("RCLID")
    creds["R"]["s"] = os.environ.get("RSCRT")
    ###############
    creds["D"] = {}
    creds["D"]["token"] = os.environ.get("DTOKN")
    ###############
    creds["M"] = {}
    creds["M"]["mySub"] = os.environ.get("MYSUB")
    creds["M"]["botMaster"] = os.environ.get("MASTR")
    creds["M"]["sleepTime"] = os.environ.get("SLPTM")
except:
    exit("Environment variables not set. Variables are:\n"
         "Reddit:\n"
         "  RUSER - Bot's reddit username\n"
         "  RPASS - Bot's reddit password\n"
         "  RCLID - Bot's reddit client-id\n"
         "  RSCRT - Bot's reddit secret\n"
         "Discogs:\n"
         "  DTOKN - Bot's discogs user_token\n"
         "Misc:\n"
         "  MYSUB - Subreddit to monitor\n"
         "  MASTR - Your personal reddit account\n"
         "  SLPTM - Time to sleep between refreshes")

# Was for testing, keeping it as it's good feedback
print("Credentials read as:")
for thing in creds:
    for more in creds[thing]:
        print(" ",thing,"|",more,"|",creds[thing][more])

# Normalize the reddit credentials
for variable in creds["M"]:
    creds["M"][variable] = creds["M"][variable].replace("/r/","").replace("r/","").replace("/u/","").replace("u/","")
creds["R"]["u"].replace("/u/","").replace("u/","")

## Reddit authentication
R = praw.Reddit(client_id = creds["R"]["c"],
                client_secret = creds["R"]["s"],
                password = creds["R"]["p"],
                user_agent = "AlbumFetchBot, a bot for fetching music information for /r/"+creds["M"]["mySub"]+"; hosted by /u/"+creds["M"]["botMaster"],
                username = creds["R"]["u"])

# Discogs authentication
D = discogs_client.Client("AlbumFetchBot, finding music for /r/"+creds["M"]["mySub"]+"; hosted by /u/"+creds["M"]["botMaster"],
                user_token = creds["D"]["token"])

# Initialize Spotify instance
S = spotipy.Spotify()

# Define bot flair. This will need to be edited before/immediately after submitting to get the correct postID in the links.
botFlair =("\n****\n\n[^(Edit this)](https://www.reddit.com/message/compose/?to="+creds["R"]["u"]+"&subject=Edit%20autofetch&message=__POSTID__%0A%0AArtist%3A%20%0A%0ASong%3A%20) ^| "
           "[^(Delete this)](https://www.reddit.com/message/compose/?to="+creds["R"]["u"]+"&subject=Delete%20autofetch&message=__POSTID__) ^| "
           "[^(I am a bot)](https://github.com/WolfgangAxel/AlbumFetchBot) ^| ^(Bugs or features?) [^Github](https://github.com/WolfgangAxel/AlbumFetchBot/issues)")

print("Bot successfully loaded. Entering main loop.")

########################################################################
#                                                                      #
#    Script Actions                                                    #
#                                                                      #
########################################################################

while True:
    try:
        checkMessages()
        checkSubreddit(creds["M"]["mySub"])
        time.sleep(eval(creds["M"]["sleepTime"]))
    except Exception as e:
        print("Error!\n"+"*"*20+"\n"+str(e.args)+"\nTrying again in 30 seconds.")
        time.sleep(30)
        
