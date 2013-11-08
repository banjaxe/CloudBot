# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince

#
# Prints the date, venue, city and country of the given artist
#
#


api_url = "http://ws.audioscrobbler.com/2.0/?format=json"
maxgigs=5

@hook.command('g', autohelp=False)
@hook.command(autohelp=False)
def gigs(inp, nick=None, say=None, me=None, msg=None, bot=None):
    """gigs [band] -- Displays the band's gigs
     from lastfm db."""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    r = http.get_json(api_url, method="artist.getEvents",
                             api_key=api_key, artist=inp,autocorrect=1,limit=maxgigs)

    if 'error' in r:
        return "Error: {}.".format(r["message"])

    llimit=r["@attr"]["total"] if r["@attr"]["total"] < maxgigs else maxgigs

    if type(r) == dict and "event" in r["events"] and type(r["events"]["event"]) == list:
        me("will headbang at these "+ llimit + "gigs with "+ nick +":")
        for event in r["events"]["event"]:
            headliner = event["artists"]["headliner"] if "headliner" in event["artists"] else "TBA"
            say(event["startDate"] + ":\tat " + event["venue"]["name"] + " (" + event["venue"]["location"]["city"] + ", " + event["venue"]["location"]["country"] + "), headliner: " + headliner + ", artists: " + ", ".join(event["artists"]["artist"]))
    else:
        msg(nick,"No gigs for " + inp + " :(")
