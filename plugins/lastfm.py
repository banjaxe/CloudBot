# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince
from datetime import datetime

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"


@hook.command('l', autohelp=False)
@hook.command(autohelp=False)
def lastfm(inp, nick='', db=None, bot=None, notice=None):
    """lastfm [user] [dontsave] -- Displays the now playing (or last played)
     track of LastFM user [user]."""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    # check if the user asked us not to save his details
    dontsave = inp.endswith(" dontsave")
    if dontsave:
        user = inp[:-9].strip().lower()
    else:
        user = inp

    db.execute("create table if not exists lastfm(nick primary key, acc)")

    if not user:
        user = db.execute("select acc from lastfm where nick=lower(?)",
                          (nick,)).fetchone()
        if not user:
            notice(lastfm.__doc__)
            return
        user = user[0]

    response = http.get_json(api_url, method="user.getrecenttracks",
                             api_key=api_key, user=user, limit=1)

    if 'error' in response:
        return "Error: {}.".format(response["message"])

    if not "track" in response["recenttracks"] or len(response["recenttracks"]["track"]) == 0:
        return 'No recent tracks for user "{}" found.'.format(user)

    tracks = response["recenttracks"]["track"]

    if type(tracks) == list:
        # if the user is listening to something, the tracks entry is a list
        # the first item is the current track
        track = tracks[0]
        status = 'is listening to'
        ending = '.'
    elif type(tracks) == dict:
        # otherwise, they aren't listening to anything right now, and
        # the tracks entry is a dict representing the most recent track
        track = tracks
        status = 'last listened to'
        # lets see how long ago they listened to it
        time_listened = datetime.fromtimestamp(int(track["date"]["uts"]))
        time_since = timesince.timesince(time_listened)
        ending = ' ({} ago)'.format(time_since)

    else:
        return "error: could not parse track listing"

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]

    out = '{} {} "{}"'.format(user, status, title)
    if artist:
        out += u' by \x02{}\x0f'.format(artist).encode('utf-8')
    if album:
        out += u' from the album \x02{}\x0f'.format(album).encode('utf-8')

    # append ending based on what type it was
    out += ending

    if inp and not dontsave:
        db.execute("insert or replace into lastfm(nick, acc) values (?,?)",
                     (nick.lower(), user))
        db.commit()

    return out


@hook.command('compare', autohelp=False)
@hook.command(autohelp=False)
def compare(inp, nick='', db=None, bot=None, notice=None):
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

    response = http.get_json(api_url, method="user.gettopartists",
                             api_key=api_key, user=user, period = '7day', limit=5)

    if 'error' in response:
        return "Error: {}.".format(response["message"])

    topArtists = []
    lastArtist = ''

    out = u'Top 5 artists this week for {}: ('.format(user)

    if len(response["topartists"]["artist"]) > 1:
        for artist in response["topartists"]["artist"]:
            topArtists.append(artist["name"])

        lastArtist = topArtists.pop()
    else:
        lastArtist = response["topartists"]["artist"]["name"]


    for artist in topArtists:
        out += u"{}, ".format(artist)
    else:
        out += u"{})".format(lastArtist)

    return out

@hook.command('gi', autohelp=False)
@hook.command(autohelp=False)
def gigs(inp, conn=None, bot=None,nick=None, chan=None):
    """gigs [band] -- Displays the band's gigs
     from lastfm db."""

    maxgigs=5

    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    r = http.get_json(api_url, method="artist.getEvents",
                             api_key=api_key, artist=inp,autocorrect=1,limit=maxgigs)

    if 'error' in r:
        return "Error: {}.".format(r["message"])

    llimit=str(r["events"]["@attr"]["total"] if r["events"]["@attr"]["total"] < maxgigs else maxgigs)

    if type(r) == dict and "event" in r["events"] and type(r["events"]["event"]) == list:
        conn.send("PRIVMSG {} :\x01ACTION will headbang at these {} gigs with {}:\x01".format(chan,llimit,nick))
        for event in r["events"]["event"]:
            cancelled="[CANCELLED] "  if event["cancelled"] == "1" else ""
            if "headliner" in event["artists"]:
                headliner = event["artists"]["headliner"]
                event["artists"]["artist"].remove(headliner)
            else:
                headliner="TBA"
            conn.send(u"PRIVMSG {} :{}: {}{} ({}, {}), headliner: \x02{}\x0f with {}".format(chan,event["startDate"],cancelled,event["venue"]["name"],event["venue"]["location"]["city"],event["venue"]["location"]["country"],headliner,", ".join(event["artists"]["artist"])))
    else:
        conn.send(u"PRIVMSG {} :{}, No gigs for {} :(".format(chan,nick,inp).encode('utf-8'))

@hook.command(autohelp=False)
def geogigs(inp, conn=None, bot=None,nick=None, chan=None):
    """geogigs [location] -- Displays gigs in your area
     from lastfm db."""

    maxgigs=5
    style='metal'
    not_style='metalcore'

    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    r = http.get_json(api_url, method="geo.getEvents",
                             api_key=api_key, location=inp,tag=style,limit=maxgigs)

    if 'error' in r:
        return "Error: {}.".format(r["message"])

    llimit=str(r["events"]["@attr"]["total"] if r["events"]["@attr"]["total"] < maxgigs else maxgigs)

    if type(r) == dict and "event" in r["events"] and type(r["events"]["event"]) == list:
        conn.send("PRIVMSG {} :\x01ACTION will headbang at these {} gigs with {}:\x01".format(chan,llimit,nick))
        for event in r["events"]["event"]:
            cancelled="[CANCELLED] "  if event["cancelled"] == "1" else ""
            if "headliner" in event["artists"]:
                headliner = event["artists"]["headliner"]
                event["artists"]["artist"].remove(headliner)
            else:
                headliner="TBA"
            # Pleease
            if not_style not in event["tags"]["tag"]:
                conn.send(u"PRIVMSG {} :{}: {}{} ({}, {}), headliner: \x02{}\x0f with {} ({})".format(chan,event["startDate"],cancelled,event["venue"]["name"],event["venue"]["location"]["city"],event["venue"]["location"]["country"],headliner,", ".join(event["artists"]["artist"]),", ".join(event["tagss"]["tag"])))
    else:
        conn.send(u"PRIVMSG {} :{}, No gigs for {} :(".format(chan,nick,inp))
