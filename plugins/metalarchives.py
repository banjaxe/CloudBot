from util import hook, http, timesince
from datetime import datetime
from BeautifulSoup import BeautifulSoup

baseurl = "http://www.metal-archives.com/"

@hook.command('maband', autohelp=False)
@hook.command(autohelp=False)
def maband(inp, conn=None, bot=None,nick=None, chan=None):
    """maband [band] -- Displays band info
     from metal archives."""

    if not inp:
        return "You must specify a band"

    response = http.get_json(baseurl + "search/ajax-advanced/searching/bands",
                             bandName=inp, exactBandMatch=0, sEcho=1, iColumns=3,
                             sColumns='', iDisplayStart=0, iDisplayLength=200, sNames=',,')

    if response["error"] != "":
        return "Error: {}.".format(response["error"])

    if response["iTotalRecords"] == 0:
        return "No bands were found"

    bands = response["aaData"]
    totalBands = response["iTotalRecords"]
    bandCounter = 5
    if totalBands < bandCounter:
        bandCounter = totalBands

    out = ""

    for band in bands[:bandCounter]:
        soup = BeautifulSoup(band[0])
        links = soup.findAll('a')
        bandLink = links[0]["href"]
        bandName = links[0].contents[0]
        bandGenre = band[1]
        bandCountry = band[2]

        conn.send(u"PRIVMSG {} :\x02{}\x0f - {} from {} (More info: {})".format(chan, bandName, bandGenre, bandCountry, bandLink))

    return u"{} bands containing the name {}".format(len(bands), inp)