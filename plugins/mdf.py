# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince
from datetime import datetime
import time

@hook.command(autohelp=False)
def mdf(inp, conn=None, bot=None,nick=None, chan=None):
    """mdf -- Displays countdown before Maryland Death Fest 2014
    """

    delta = datetime(2014, 05, 22) - datetime.now()

    # JOKE HUEHUEHUE
    # return "{} days before MDF 2014!".format(delta.days)
    conn.send(u"PRIVMSG {} :{}".format(chan, "MDF 2014 cancelled :("))
    time.sleep(10)
    conn.send(u"PRIVMSG {} :Just kidding {}. {} days before MDF 2014!".format(chan,nick,delta.days))
