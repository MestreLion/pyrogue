# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>

'''Main module and entry point'''

import os
import logging
import argparse
import curses

from . import g
from . import window
from . import keyboard
from .player import Player


log = logging.getLogger(__name__)


class GameError(Exception):
    pass


def parseargs(argv=None):
    parser = argparse.ArgumentParser(
        description="Python port of the PC-DOS classic game Rogue")

    parser.add_argument('--quiet', '-q', dest='loglevel',
                        const=logging.WARNING, default=logging.INFO,
                        action="store_const",
                        help="Suppress informative messages.")

    parser.add_argument('--verbose', '-v', dest='loglevel',
                        const=logging.DEBUG,
                        action="store_const",
                        help="Verbose mode, output extra info.")

    parser.add_argument('savegame', nargs='?',
                        help="Save game file to load.")

    args = parser.parse_args(argv)

    return args


def main(argv=None):
    '''App entry point
        <argv>: list of command line arguments, defaults to sys.argv[1:]
    '''
    args = parseargs(argv)

    logging.basicConfig(
        level=args.loglevel,
        format="[%(levelname)-8s] %(asctime)s %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=os.path.join(g.CONFIGDIR, "{}.log".format(g.APPNAME))
    )

    keyboard.set_term()

    try:
        curses.wrapper(game)
        curses.flushinp()
    except GameError as e:
        log.error(e)


def game(stdscr):
    cols = getattr(curses, 'COLS',  0)
    rows = getattr(curses, 'LINES', 0)
    log.info("Terminal size: %d x %d", cols, rows)

    if cols < g.COLS or rows < g.ROWS:
        raise GameError("{} requires a terminal of at least {} x {},"
                        " current is {} x {}".format(
                        g.APPNAME, g.COLS, g.ROWS, cols, rows))

    curses.use_default_colors()

    # Cursor: 0=invisible, 1=normal (underline), 2="very visible" (block)
    # Normal cursor is only available in real consoles, X11-based ones
    # are always block
    if keyboard.is_console:
        curses.curs_set(1)
    else:
        curses.curs_set(0)

    screen = window.Screen(stdscr, (g.ROWS, g.COLS))
    dungeon = screen.dungeon
    player = Player(g.PLAYERNAME,
                    dungeon,
                    int(dungeon.size[0] / 2),
                    int(dungeon.size[1] / 2))

    screen.message("Hello {}. Welcome to the Dungeons of Doom",
                   player.name)

    while True:
        screen.statusbar(player)
        screen.systembar()
        dungeon.window.move(player.row, player.col)
        screen.window.refresh()

        ch = dungeon.window.getch()

        if ch == ord('Q'):
            break

        elif ch in (curses.KEY_LEFT,  ord('h')): player.move( 0, -1)  # Left
        elif ch in (curses.KEY_DOWN,  ord('j')): player.move( 1,  0)  # Down
        elif ch in (curses.KEY_UP,    ord('k')): player.move(-1,  0)  # Up
        elif ch in (curses.KEY_RIGHT, ord('l')): player.move( 0,  1)  # Right
        elif ch in (curses.KEY_PPAGE, ord('u')): player.move(-1,  1)  # Up Right
        elif ch in (curses.KEY_NPAGE, ord('n')): player.move( 1,  1)  # Down Right
        elif ch in (curses.KEY_HOME,  ord('y'), curses.KEY_FIND):   player.move(-1, -1)  # Up Left
        elif ch in (curses.KEY_END,   ord('b'), curses.KEY_SELECT): player.move( 1, -1)  # Down Left
        screen.message("Ch={}, player at ({}, {}), food is {}",
                       ch, player.row, player.col, player.food)
