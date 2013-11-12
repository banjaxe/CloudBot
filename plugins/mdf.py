# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from util import hook, http, timesince
from datetime import datetime


@hook.command(autohelp=False)
def mdf(inp):
    """mdf -- Displays countdown before Maryland Death Fest 2014
    """

    delta = datetime(2014, 05, 22) - datetime.now()

    return "{} days before MDF 2014!".format(delta.days)
