from util import hook, http, timesince
from datetime import datetime
import HTMLParser

api_url = "http://api.icndb.com/jokes/random"

@hook.command('bam', autohelp=False)
@hook.command(autohelp=False)
def bam(inp, nick='', db=None, bot=None, notice=None):

    response = []

    name = nick
    if inp:
        name = inp

    if inp:
        response = http.get_json(api_url, firstName=name, lastName="~")
    else:
        response = http.get_json(api_url, firstName=name, lastName="~")

    if response["type"] == "success":
        bam = response["value"]["joke"].replace(u"{} ~".format(name), u"{}".format(name))
        htmlParser = HTMLParser.HTMLParser()
        bam = htmlParser.unescape(bam)
        return bam
    else:
        return u"There was a problem, sorry {}".format(nick)
