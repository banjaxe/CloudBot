import re

from util import hook

sedreg = (r'^s\/(.+)\/(.+)'
	'([-_a-zA-Z0-9]+)', re.I|re.S)

matchany = (r'.+'
	'.+', re.I|re.S)

if 'history' not in globals():
	global history

history = []

@hook.regex(*matchany)
def saveHistory(match, nick=''):
	sedmatch = re.match(r's\/(.+)\/(.+)', match.group())
	if(sedmatch == None):
		history.insert(0, [nick, match.group()])
		if len(history) > 10:
			history.pop()

@hook.regex(*sedreg)
def doSed(match):
	for quote in history:
		if match.group(1) in quote[1]:
			replaceString = "{}{}".format(match.group(2), match.group(3))
			return "{} meant to say '{}'".format(quote[0], quote[1].replace(match.group(1), replaceString))
