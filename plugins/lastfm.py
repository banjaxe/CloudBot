# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince, web
from datetime import datetime
import time

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"

@hook.command('l', autohelp=False)
@hook.command('np', autohelp=False)
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
    linkshort = web.isgd(link)

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


    if "tag" in track2["toptags"]:
        genres1 = track2["toptags"]["tag"][:]
        genresstr = str(genres1)
        #First genre
        genres3 = genresstr.split("u'name': u'" ,1)[1]
        genres4 = genres3.split("'",1)[0]
        #Second genre
        genres5 = genres3.split("u'name': u'", 1)[1]
        genres6 = genres5.split("'",1)[0]
        #Third genre
        genres7 = genres5.split("u'name': u'", 1)[1]
        genres8 = genres7.split("'",1)[0]
        genres = '({}, {}, {})'.format(genres4, genres6, genres8)
    else:
        genres = "(No tags found)"

        
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
    if linkshort:
        out += u' ({})'.format(linkshort)

    # append ending based on what type it was
    out += ending

    if inp and not dontsave:
        db.execute("insert or replace into lastfm(nick, acc) values (?,?)",
                     (nick.lower(), user))
        db.commit()

    return out
