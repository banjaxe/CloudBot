# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
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

    r = http.get_json(api_url, method="artist.getInfo",
                             api_key=api_key, artist=inp,autocorrect=1,limit=1)

    if 'error' in r:
        return "Error: {}.".format(r["message"])
    out="No band named "+ inp
    tags=[]
    sims=[]

    if type(r) == dict:
        artist = r["artist"]
        if type(artist) ==dict:
            for tag in artist["tags"]["tag"]:
                tags.append(tag["name"])
            for sim in artist["similar"]["artist"]:
                sims.append(sim["name"])
            placeformed=" ("+artist["bio"]["placeformed"] +")" if "placeformed" in artist["bio"] else ""
            out = (artist["name"] + placeformed + " has "+ artist["stats"]["playcount"] + " plays by " + artist["stats"]["listeners"] + " listeners. Tags: " + ", ".join(tags) + ". Similar artists: " + ", ".join(sims) + ". More info on " + artist["url"]).encode("utf-8")
    return out

