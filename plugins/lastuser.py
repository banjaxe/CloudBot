# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince
import re

#
# Add or delete a lastfm account in the db
#
#
#

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"


@hook.command('lu', autohelp=False)
@hook.command(autohelp=False)
def lastuser(inp, nick=None db=None, bot=None):
    """lastuser [lastfm account] -- Saves the nick's lastfm account
     """
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    acc = inp

    # Search for some piratery
    p = re.compile(acc)
    if p.match(";")
        return "You filthy pirate, you should be banned."

    db.execute("create table if not exists lastfm(nick primary key, acc)")

    if acc:
        db.execute("insert or replace into lastfm(nick, acc) values (?,?)",
                     (nick.lower(), acc))
        db.commit()
        return nick + " registered as " + acc + "."
    else:
        db.execute("delete from lastfm where lower(nick) = ?",
                     (nick.lower(),))
        db.commit()
        return nick + " unregistered."
