import re

from util import hook

sedreg = (r's\/(.+)\/(.+)'
	'([-_a-zA-Z0-9]+)', re.I|re.S)

matchany = (r'.+'
	'.+', re.I|re.S)

history = ''

@hook.regex(*matchany)
def saveHistory(match):
	sedmatch = re.match(r's\/(.+)\/(.+)', match.group())
	if(sedmatch == None):
		global history
		history = match.group()

@hook.regex(*sedreg)
def doSed(match, db=None):
	#WHYYYYYYYYYYYYYYY FUCKING REGEX
	replaceString = "{}{}".format(match.group(2), match.group(3))
	return "You meant {}.".format(history.replace(match.group(1), replaceString))
