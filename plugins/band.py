from util import hook, http, timesince
from datetime import datetime

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"


@hook.command('b', autohelp=False)
@hook.command(autohelp=False)
def band(inp, nick='', db=None, bot=None, notice=None):
    """band [band] -- Displays the band's informations
     from lastfm db."""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    response = http.get_json(api_url, method="artist.getInfo",
                             api_key=api_key, artist=inp,autocorrect=1)

    if 'error' in response:
        return "Error: {}.".format(response["message"])

    return response
