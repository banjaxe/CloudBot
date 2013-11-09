from util import hook, http, timesince
from datetime import datetime
#import time

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"

@hook.command('top', autohelp=False)
@hook.command(autohelp=False)
def top(inp, nick='', db=None, bot=None, notice=None):
    """top -- Displays the top bands for [nick]
     from lastfm db."""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    if inp:
        user = db.execute("select acc from lastfm where nick=lower(?)", (inp,)).fetchone()
    else:
        user = db.execute("select acc from lastfm where nick=lower(?)", (nick,)).fetchone()

    if not user:
        if not inp:
            user = nick
        else:
            user = inp
    else:
        user = user[0]

    #print time.time()

    response = http.get_json(api_url, method="user.getweeklyartistchart",
                             api_key=api_key, user=user, {"from": ''}, to='', limit=5)

    if 'error' in response:
        return "Error: {}.".format(response["message"])

    topArtists = []
    lastArtist = ''

    out = u'Top 5 artists this week for {}: ('.format(user)

    mylen = len(response["weeklyartistchart"]["artist"])

    if mylen > 1:
        for artist in response["weeklyartistchart"]["artist"]:
            topArtists.append(artist["name"])

        lastArtist = topArtists.pop()
    else:
        lastArtist = response["topartists"]["artist"]["name"]


    for artist in topArtists:
        out += u"{}, ".format(artist)
    else:
        out += u"{})".format(lastArtist)

    return out