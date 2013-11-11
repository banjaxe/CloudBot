from util import hook, http, timesince
from datetime import datetime

api_url = "http://catfacts-api.appspot.com/api/facts"

@hook.command('catfacts', autohelp=False)
@hook.command(autohelp=False)
def catfacts(inp, nick='', db=None, bot=None, notice=None):

    response = http.get_json(api_url)

    fact = response["facts"][0]

    return u"{} Thank you for using catfacts. To stop this feature use the command 'catfacts -disable'.".format(fact)