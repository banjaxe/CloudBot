from util import hook

@hook.command('wow', autohelp=False)
@hook.command(autohelp=False)
def wow(inp, nick='', db=None, bot=None, notice=None):
    """wow"""

    with open("plugins/data/wow.txt") as f:
        wowList = [line.strip() for line in f.readlines()
              if not line.startswith("//")]

        print wowList

    return "bam"