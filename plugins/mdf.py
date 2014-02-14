# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince
from datetime import datetime
import time


@hook.command(autohelp=False)
def mdf(inp):
    """mdf -- Displays countdown before Maryland Death Fest 2014
    """

    delta = datetime(2014, 05, 22) - datetime.now()

    # JOKE HUEHUEHUE
    return "MDF 2014 cancelled :("
    time.sleep(3)
    return "Just kidding. {} days before MDF 2014!".format(delta.days)
