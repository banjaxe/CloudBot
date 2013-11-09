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

    user = db.execute("select acc from lastfm where nick=lower(?)", (inp,)).fetchone()

    if not user:
        user = inp
    else:
        user = user[0]


    response = http.get_json(api_url, method="tasteometer.compare",
                             api_key=api_key, type1="user", type2="user", value1=nick, value2=user, limit=5)

    if 'error' in response:
        return "Error: {}.".format(response["message"])

    score = round(float(response["comparison"]["result"]["score"]) * 100, 1)

    if score == 0:
        out = "You and {} have no artists in common".format(inp)
    else:
        out = "You and {} have {}% in common: artists(".format(inp, score)

        artists = []

        for item in response["comparison"]["result"]["artists"]["artist"]:
            artists.append(item["name"])

        lastArtist = artists.pop()

        for artist in artists:
            out += "{}, ".format(artist)
        else:
            out += "{})".format(lastArtist)


    return out.encode("utf-8")