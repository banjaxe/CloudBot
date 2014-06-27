import json
from util import hook
from fnmatch import fnmatch


@hook.sieve
def ignore_sieve(bot, input, func, type, args):
    """ blocks input from isocube-contained channels/hosts """
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    mask = input.mask.lower()

    # don't block input to event hooks
    if type == "event":
        return input

    if ignorelist:
        for pattern in ignorelist:
            if pattern.startswith("#") and pattern in ignorelist:
                if input.command == "PRIVMSG" and input.lastparam[1:] == "unisocube":
                    return input
                else:
                    return None
            elif fnmatch(mask, pattern):
                if input.command == "PRIVMSG" and input.lastparam[1:] == "unisocubed":
                    return input
                else:
                    return None

    return input


@hook.command(autohelp=False)
def isocubed(inp, notice=None, bot=None):
    """isocubed -- Lists isocube-confined channels/users."""
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    if ignorelist:
        notice("Isocube-confined users are: {}".format(", ".join(ignorelist)))
    else:
        notice("No masks are currently in the isocubes.")
    return


@hook.command(permissions=["isocube"])
def isocube(inp, notice=None, bot=None, config=None):
    """isocube <channel|nick|host> -- Makes the bot detain <channel|user> in the isocubes."""
    target = inp.lower()
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    if target in ignorelist:
        notice("{} is already in the isocubes.".format(target))
    else:
        notice("{} has been detained in the isocubes.".format(target))
        ignorelist.append(target)
        ignorelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return


@hook.command(permissions=["isocube"])
def unisocube(inp, notice=None, bot=None, config=None):
    """unisocube <channel|user> -- removes
    <channel|user> from the isocubes."""
    target = inp.lower()
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    if target in ignorelist:
        notice("{} has been removed from the isocubes.".format(target))
        ignorelist.remove(target)
        ignorelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    else:
        notice("{} is not in isocube confinement.".format(target))
    return
