from util import hook, http, timesince
from datetime import datetime
 
api_url = "http://ws.audioscrobbler.com/2.0/?format=json"
 
 
@hook.command('plays', autohelp=False)
@hook.command(autohelp=False)
def plays(band, nick='', db=None, bot=None, notice=None):
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"
 
    user = db.execute("select acc from lastfm where nick=lower(?)", (nick,)).fetchone()
       
    if not user:
        notice(lastfm.__doc__)
        return
               
    user = user[0]
 
    response = http.get_json(api_url, method="user.getartisttracks", api_key=api_key, user=user, artist=band)
    if 'error' in response:
        return "Error: {}.".format(response["message"])
 
    if not "@attr" in response["artisttracks"]:
        return '"{}" has never listened to that band. Poserfalse'.format(user)
 
    plays = response["artisttracks"]["@attr"]["items"]
    band = response["artisttracks"]["track"][0]["artist"]["#text"]
 
    out = '{} has {} plays'.format(user, plays)
    if band:
        out += " by \x02{}\x0f".format(band.encode("utf-8"))
 
 
    return out
