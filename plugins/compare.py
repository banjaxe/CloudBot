from util import hook, http, timesince
from datetime import datetime

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"

@hook.command('compare', autohelp=False)
@hook.command(autohelp=False)
def band(inp, nick='', db=None, bot=None, notice=None):
    """compare [nick] -- Displays the comparison between users
     from lastfm db."""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    qUser = db.execute("select acc from lastfm where nick=lower(?)", (inp,)).fetchone()

    if not qUser:
        qUser = inp
    else:
        qUser = qUser[0]

    nUser = db.execute("select acc from lastfm where nick=lower(?)", (nick,)).fetchone()

    if not nUser:
        nUser = nick
    else:
        nuser = nUser[0]


    response = http.get_json(api_url, method="tasteometer.compare",
                             api_key=api_key, type1="user", type2="user", value1=nuser, value2=qUser, limit=5)

    if 'error' in response:
        return "Error: {}.".format(response["message"])

    score = round(float(response["comparison"]["result"]["score"]) * 100, 1)

    if score == 0:
        out = u"You and {} have no artists in common".format(inp)
    else:
        out = u"You and {} have {}% in common: artists(".format(qUser, score)

        artists = []

        for item in response["comparison"]["result"]["artists"]["artist"]:
            artists.append(item["name"])

        lastArtist = artists.pop()

        for artist in artists:
            out += u"{}, ".format(artist)
        else:
            out += u"{})".format(lastArtist)


    return out