import random
import re
import time

from util import hook


def format_sprite(q, num, n_sprites):
    """Returns a formatted string of a quote"""
    ctime, name, msg = q
    return "[{}/{}] <{}> {}".format(num, n_sprites,
                                name, msg)


def create_table_if_not_exists(db):
    """Creates an empty sprite table if one does not already exist"""
    db.execute("create table if not exists sprite"
               "(chan, name, add_name, msg, time real, deleted default 0, "
               "primary key (chan, name, msg))")
    db.commit()


def add_sprite(db, chan, name, add_name, msg):
    """Adds a sprite to a sprite name, returns message string"""
    try:
        db.execute('''INSERT OR FAIL INTO sprite
                      (chan, name, add_name, msg, time)
                      VALUES(?,?,?,?,?)''',
                   (chan, name, add_name, msg, time.time()))
        db.commit()
    except db.IntegrityError:
        return "Message already stored, doing nothing."
    return "Sprite added."


def del_sprite(db, chan, name, add_name, msg):
    """Deletes a sprite from a sprite name"""
    db.execute('''UPDATE sprite SET deleted = 1 WHERE
                  chan=? AND lower(name)=lower(?) AND msg=msg''')
    db.commit()


def get_sprite_num(num, count, name):
    """Returns the sprite number to fetch from the DB"""
    if num:  # Make sure num is a number if it isn't false
        num = int(num)
    if count == 0:  # Error on no sprites
        raise Exception("No sprites found for {}.".format(name))
    if num and num < 0:  # Count back if possible
        num = count + num + 1 if num + count > -1 else count + 1
    if num and num > count:  # If there are not enough sprites, raise an error
        raise Exception("I only have {} sprite{} for {}.".format(count, ('s', '')[count == 1], name))
    if num and num == 0:  # If the number is zero, set it to one
        num = 1
    if not num:  # If a number is not given, select a random one
        num = random.randint(1, count)
    return num


def get_sprite_by_name(db, name, num=False):
    """Returns a sprite from a name, random or selected by number"""
    count = db.execute('''SELECT COUNT(*) FROM sprite WHERE deleted != 1
                          AND lower(name) = lower(?)''', [name]).fetchall()[0][0]

    try:
        num = get_sprite_num(num, count, name)
    except Exception as error_message:
        return error_message

    sprite = db.execute('''SELECT time, name, msg
                          FROM sprite
                          WHERE deleted != 1
                          AND lower(name) = lower(?)
                          ORDER BY time
                          LIMIT ?, 1''', (name, (num - 1))).fetchall()[0]
    return format_sprite(sprite, num, count)


def get_sprite_by_name_chan(db, chan, name, num=False):
    """Returns a sprite from a name in a channel, random or selected by number"""
    count = db.execute('''SELECT COUNT(*)
                          FROM sprite
                          WHERE deleted != 1
                          AND chan = ?
                          AND lower(name) = lower(?)''', (chan, name)).fetchall()[0][0]

    try:
        num = get_sprite_num(num, count, name)
    except Exception as error_message:
        return error_message

    sprite = db.execute('''SELECT time, name, msg
                          FROM sprite
                          WHERE deleted != 1
                          AND chan = ?
                          AND lower(name) = lower(?)
                          ORDER BY time
                          LIMIT ?, 1''', (chan, name, (num - 1))).fetchall()[0]
    return format_sprite(sprite, num, count)


def get_sprite_by_chan(db, chan, num=False):
    """Returns a sprite from a channel, random or selected by number"""
    count = db.execute('''SELECT COUNT(*)
                          FROM sprite
                          WHERE deleted != 1
                          AND chan = ?''', (chan,)).fetchall()[0][0]

    try:
        num = get_sprite_num(num, count, chan)
    except Exception as error_message:
        return error_message

    sprite = db.execute('''SELECT time, name, msg
                          FROM sprite
                          WHERE deleted != 1
                          AND chan = ?
                          ORDER BY time
                          LIMIT ?, 1''', (chan, (num - 1))).fetchall()[0]
    return format_quote(quote, num, count)


@hook.command('s')
@hook.command
def sprite(inp, name='', chan='', db=None, notice=None):
    """sprite [#chan] [name] [#n]/.sprite add <name> <msg>
    Gets random or [#n]th sprite by <name> or from <#chan>/adds sprite."""
    create_table_if_not_exists(db)

    add = re.match(r"add[^\w@]+(\S+?)>?\s+(.*)", inp, re.I)
    retrieve = re.match(r"(\S+)(?:\s+#?(-?\d+))?$", inp)
    retrieve_chan = re.match(r"(#\S+)\s+(\S+)(?:\s+#?(-?\d+))?$", inp)

    if add:
        quoted_name, msg = add.groups()
        notice(add_sprite(db, chan, quoted_name, name, msg))
        return
    elif retrieve:
        select, num = retrieve.groups()
        by_chan = True if select.startswith('#') else False
        if by_chan:
            return get_sprite_by_chan(db, select, num)
        else:
            return get_sprite_by_name(db, select, num)
    elif retrieve_chan:
        chan, name, num = retrieve_chan.groups()
        return get_quote_by_name_chan(db, chan, name, num)

    notice(sprite.__doc__)
