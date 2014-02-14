# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince
from datetime import datetime


@hook.command(autohelp=False)
def mdf2(inp, conn=None, bot=None,nick=None, chan=None):
    """mdf2 -- Displays countdown before Maryland Death Fest 2014
    """

    delta = datetime(2014, 05, 22) - datetime.now()

    # JOKE HUEHUEHUE
    conn.send(u"PRIVMSG {} :{}), headliner: \x02{}\x0f{} ({})".format(chan, "MDF 2014 cancelled :("))
    time.sleep(3)
    return "{} days before MDF 2014!".format(delta.days)
    conn.send(u"PRIVMSG {} :Just kidding. {} days before MDF 2014!), headliner: \x02{}\x0f{} ({})".format(chan,delta.days)
