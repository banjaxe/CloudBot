# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince
from datetime import datetime
import time

@hook.command(autohelp=False)
def cdf(inp, conn=None, bot=None,nick=None, chan=None):
    """cdf -- Displays countdown before California Death Fest 2015
    """

    delta = datetime(2015, 10,9) - datetime.now()

    # JOKE HUEHUEHUE
    return "{} days before CDF 2015!".format(delta.days)
    #conn.send(u"PRIVMSG {} :{}".format(chan, "CDF 2015 cancelled :("))
    #time.sleep(10)
    #conn.send(u"PRIVMSG {} :Just kidding {}. {} days before CDF 2015!".format(chan,nick,delta.days))
