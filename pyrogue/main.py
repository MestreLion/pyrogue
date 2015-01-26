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

import logging
import argparse
import curses

from . import g, window
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
    )

    try:
        curses.wrapper(game)
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
    curses.curs_set(False)

    screen = curses.newwin(g.ROWS, g.COLS, 0, 0)  # x and y are swapped!
    screen.clear()

    player = Player(g.PLAYERNAME)
    screen.addch(player.row, player.col, player.char)

    window.statusbar(screen, player)
    window.box(screen, (10, 10), (5, 5))


    screen.refresh()
    screen.getkey()
