# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince, web
from datetime import datetime
import time
import re
import logging

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
        status = u'is listening to'
        ending = '.'
    elif type(tracks) == dict:
        # otherwise, they aren't listening to anything right now, and
        # the tracks entry is a dict representing the most recent track
        track = tracks
        status = u'last listened to'
        # lets see how long ago they listened to it
        time_listened = datetime.fromtimestamp(int(track["date"]["uts"]))
        time_since = timesince.timesince(time_listened)
        ending = u' ({} ago)'.format(time_since)

    else:
        return "error: could not parse track listing"

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]
    link = track["url"]

    try:
        link = web.isgd(link)
    except:
        print "Error shortening link"

    title2 = unicode(title)
    artist2 = unicode(artist)

    response2 = http.get_json(api_url, method="track.getinfo",
                              api_key=api_key,track=title2, artist=artist2, username=user,  autocorrect=1)

    trackdetails = response2["track"]
    
    if type(trackdetails) == list:
        track2 = trackdetails[0]
    elif type(trackdetails) == dict:
        track2 = trackdetails

    if "userplaycount" in trackdetails:
        playcounts = trackdetails["userplaycount"]
    else:
        playcounts = 0

    toptags = http.get_json(api_url, method="artist.gettoptags",
                              api_key=api_key, artist=artist)
    genreList = []
    genres = "("

    if "tag" in toptags["toptags"]:
        for(i, tag) in enumerate(toptags["toptags"]["tag"]):
            genreList.append(tag["name"])
            if(i == 2):
                break
        for singleGenre in genreList:
            if(singleGenre == genreList[-1]):
                genres += u"{}".format(singleGenre)
            else:
		genres += u"{}, ".format(singleGenre)
    else:
        genres = "(No tags)"

    length1 = track2["duration"]
    lengthsec = float(length1) / 1000
    length = time.strftime('%M:%S', time.gmtime(lengthsec))
    length = length.lstrip("0")

    out = u'{} {} "{}"'.format(user, status, title)
    
    if artist:
        out += u' by \x02{}\x0f'.format(artist)
    if album:
        out += u' from the album \x02{}\x0f'.format(album)
    if length:
        out += u' [{}]'.format(length)
    if playcounts:
        out += u' [plays: {}]'.format(playcounts)
    if playcounts == 0:
        out += u' [plays: {}]'.format(playcounts)
    if genres:
        out += u' {}'.format(genres)

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
                             api_key=api_key, type1="user", type2="user", value1=nuser, value2=qUser, limit=10)

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
            if type(artist["tags"]) == dict:
                for tag in artist["tags"]["tag"]:
                    tags.append(tag["name"])
            else:
                tags.append(u"No tags available")

            if type(artist["similar"]) == dict:
                if type(artist["similar"]["artist"]) == list:
                    for sim in artist["similar"]["artist"]:
                        sims.append(sim["name"])
                elif type(artist["similar"]["artist"]) == dict:
                    sims.append(artist["similar"]["artist"]["name"])
                else:
                    sims.append(u"No similar artists found")
            else:
                sims.append(u"No similar artists found")

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
                             api_key=api_key, user=user, period = '7day', limit=10)

    if 'error' in response:
        return "Error: {}.".format(response["message"])

    topArtists = []
    lastArtist = ''

    out = u'Top 10 artists this week for {}: ('.format(user)

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


@hook.command('genre', autohelp=False)
@hook.command(autohelp=False)
def genre(inp, nick='', db=None, bot=None, notice=None):
    """genre -- Displays information for specified genre
    from last.fm db. """

    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    genretag = inp

    response = http.get_json(api_url, method="tag.search",
                             api_key=api_key, tag=genretag, limit=1)

    if 'error' in response:
        return "Error: {}.".format(response["message"])

    tagdetails = response["results"]["tagmatches"]

    
    try:
        if "url" in tagdetails["tag"]:
            link = tagdetails["tag"]["url"]

            try:
                link = web.isgd(link)
            except:
                print "Error shortening link"

            tagname = response["results"]["opensearch:Query"]["searchTerms"]
            tagname = tagname.title()
        else:
            return "Error: No such genre, check spelling."
    except TypeError:
        return "Error: No description found of this genre."
    responsesimilar = http.get_json(api_url, method="tag.getsimilar",
                                    api_key=api_key, tag=genretag)

    tagsimilar = responsesimilar["similartags"]["tag"]

    simgenstr = str(tagsimilar)
    
    if "name" in simgenstr:
        #First genre
        simgen1 = simgenstr.split("u'name': u'" ,1)[1]
        simgen2 = simgen1.split("'",1)[0]
        #Second genre
        simgen3 = simgen1.split("u'name': u'", 1)[1]
        simgen4 = simgen3.split("'",1)[0]
        #Third genre
        simgen5 = simgen3.split("u'name': u'", 1)[1]
        simgen6 = simgen5.split("'",1)[0]
        similartag = '{}, {}, {}'.format(simgen2, simgen4, simgen6)
    else: 
        return "Error: No such genre, check spelling."


    responsetop = http.get_json(api_url, method="tag.gettopartists",
                                api_key=api_key, tag=genretag)

    tagtopartist = responsetop["topartists"]["artist"]

    topartstr = str(tagtopartist)
    #First artist
    topart1 = topartstr.split("u'name': u'" ,1)[1]
    topart2 = topart1.split("'",1)[0]
    #Second artist
    topart3 = topart1.split("u'name': u'", 1)[1]
    topart4 = topart3.split("'",1)[0]
    #Third artist
    topart5 = topart3.split("u'name': u'", 1)[1]
    topart6 = topart5.split("'",1)[0]
    #Fourth artist
    topart7 = topart5.split("u'name': u'", 1)[1]
    topart8 = topart7.split("'",1)[0]
    #Fifth artist
    topart9 = topart7.split("u'name': u'", 1)[1]
    topart10 = topart9.split("'",1)[0]
    topartists = '{}, {}, {}, {}, {}'.format(topart2, topart4, topart6, topart8, topart10)


    responsedesc = http.get_json(api_url, method="tag.getInfo",
                                 api_key=api_key, tag=genretag)

    tagdesc = responsedesc["tag"]["wiki"]

    try:
        genredesc = tagdesc["summary"]
        genredesc = re.sub('<[^>]*>', '', genredesc)
        #genredesc = genredesc.split(".", 1)[0]
        genredesc = genredesc.replace("&quot;", "")
        genredesc = (genredesc[:225] + '...') if len(genredesc) > 225 else genredesc
    except TypeError:
        return "Error: No summary found for this genre, check spelling."

    out = ''

    if tagname:
        out += u'\x02{}\x0f: '.format(tagname)
    if genredesc:
        out += u'{}'.format(genredesc)
    if similartag:
        out += u' \x02Similar genres\x0f: ({})'.format(similartag)
    if topartists:
        out += u' \x02Top artists\x0f: ({})'.format(topartists)

    return out

    


@hook.command('gi', autohelp=False)
@hook.command(autohelp=False)
def gigs(inp, conn=None, bot=None,nick=None, chan=None):
    """gigs [band] -- Displays the band's gigs
     from lastfm db."""

    maxgigs=5
    gig_counter=0

    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    r = http.get_json(api_url, method="artist.getEvents",
                             api_key=api_key, artist=inp,autocorrect=1,limit=20)

    if 'error' in r:
        return "Error: {}.".format(r["message"])

    if type(r) == dict and "event" in r["events"] and type(r["events"]["event"]) == list:
        conn.send("PRIVMSG {} :\x01ACTION will headbang at these gigs with {}:\x01".format(chan,nick))
        for event in r["events"]["event"]:
            if gig_counter == maxgigs:
                break
            others=""
            cancelled="[CANCELLED] "  if event["cancelled"] == "1" else ""
            if "headliner" in event["artists"]:
                headliner = event["artists"]["headliner"]
                if type(event["artists"]["artist"]) == list:
                    event["artists"]["artist"].remove(headliner)
                    others=" with {}".format(", ".join(event["artists"]["artist"]))
            else:
                headliner="TBA"
            conn.send(u"PRIVMSG {} :{}: {}{} ({}, {}), headliner: \x02{}\x0f{}".format(chan,event["startDate"][:-9],cancelled,event["venue"]["name"],event["venue"]["location"]["city"],event["venue"]["location"]["country"],headliner,others))
            gig_counter=gig_counter+1
    else:
        conn.send(u"PRIVMSG {} :{}, No gigs for {} :(".format(chan,nick,inp).encode('utf-8'))

@hook.command(autohelp=False)
def geogigs(inp, conn=None, bot=None,nick=None, chan=None):
    """geogigs [location] -- Displays gigs in your area
     from lastfm db."""

    maxgigs=5
    style='metal'
    not_styles=['metalcore','nu metal','frenchcore']
    gig_counter=0

    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    r = http.get_json(api_url, method="geo.getEvents",
                             api_key=api_key, location=inp,tag=style,limit=20)

    if 'error' in r:
        return "Error: {}.".format(r["message"])

    if type(r) == dict and "event" in r["events"] and type(r["events"]["event"]) == list:
        conn.send("PRIVMSG {} :\x01ACTION will headbang at these gigs with {}:\x01".format(chan,nick))
        for event in r["events"]["event"]:
            if gig_counter == maxgigs:
                break
            others=""
            tags=""
            cancelled="[CANCELLED] "  if event["cancelled"] == "1" else ""
            if "headliner" in event["artists"]:
                headliner = event["artists"]["headliner"]
                if type(event["artists"]["artist"]) == list:
                    event["artists"]["artist"].remove(headliner)
                    others=" with {}".format(", ".join(event["artists"]["artist"]))
            else:
                headliner="TBA"
            if type(event["tags"]["tag"]) == list:
                # Get out if we meet a not_style tag
                not_this_one="false"
                for genre in not_styles:
                    if genre in event["tags"]["tag"]:
                        not_this_one="true"
                        break
                tags=", ".join(event["tags"]["tag"])
            else:
                tags=event["tags"]["tag"]

            if not_this_one=="false":
                conn.send(u"PRIVMSG {} :{}: {}{} ({}, {}), headliner: \x02{}\x0f{} ({})".format(chan,event["startDate"][:-9],cancelled,event["venue"]["name"],event["venue"]["location"]["city"],event["venue"]["location"]["country"],headliner,others,tags))
                gig_counter=gig_counter+1
    else:
        conn.send(u"PRIVMSG {} :{}, No gigs for {} :(".format(chan,nick,inp))
