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

import locale
locale.setlocale(locale.LC_ALL, '')

import os
import logging.handlers
import argparse
import curses

from . import g
from . import window
from . import input

from .game import Game


log = logging.getLogger(__name__)


class GameError(Exception):
    pass


def parseargs(argv=None):
    parser = argparse.ArgumentParser(
        description="Python port of the PC-DOS classic game Rogue")

    parser.add_argument('savegame', nargs='?',
                        help="Save game file to load.")

    args = parser.parse_args(argv)

    return args


def setuplogging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # must be the lowest

    # Console output (stderr)
    sh = logging.StreamHandler()
    sh.setLevel(logging.WARNING)  # default
    sh.setFormatter(logging.Formatter(fmt="%(message)s"))

    # Rotating log file (10 x 1MB)
    fh = logging.handlers.RotatingFileHandler(
        filename=os.path.join(g.CONFIGDIR, "{}.log".format(g.APPNAME)),
        maxBytes=2**20,
        backupCount=10,
        delay=True)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        fmt="[%(levelname)-8s] %(asctime)s %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"))

    logger.addHandler(fh)
    logger.addHandler(sh)


def main(argv=None):
    '''App entry point
        <argv>: list of command line arguments, defaults to sys.argv[1:]
    '''
    args = parseargs(argv)
    setuplogging()

    log.debug("Initializing curses with TERM=%s", os.environ.get("TERM"))

    try:
        curses.wrapper(init, args)
        curses.flushinp()
    except GameError as e:
        log.error(e)
    except Exception as e:
        log.critical(e, exc_info=1)


def init(stdscr, args):
    cols = getattr(curses, 'COLS',  0)
    rows = getattr(curses, 'LINES', 0)
    log.info("Terminal size: %d x %d", cols, rows)

    if cols < g.COLS or rows < g.ROWS:
        raise GameError("{} requires a terminal of at least {} x {},"
                        " current is {} x {}".format(
                        g.APPNAME, g.COLS, g.ROWS, cols, rows))

    if not curses.has_colors():
        raise GameError("{} requires a color terminal")

    curses.use_default_colors()

    # Setup basic color pairs: each curses named color with default background
    for color in window.COLOR:  #curses.COLORS):  # @UndefinedVariable
        if not color == window.COLOR.DEFAULT:
            curses.init_pair(color, color, -1)
            window.colors[color] = curses.color_pair(color)

    # Some adjustments:
    #curses.init_pair(max(window.COLOR) + 1, -1, -1)
    #window.colors[window.COLOR.DEFAULT] = curses.color_pair(max(window.COLOR) + 1)
    window.colors[window.COLOR.BROWN] = window.colors[window.COLOR.YELLOW]
    window.colors[window.COLOR.YELLOW] |= curses.A_BOLD  # Yellow is Brown in curses (despite the name)
    window.colors[window.COLOR.BLUE]   |= curses.A_BOLD  # Blue is Light blue in Rogue

    # Cursor: 0=invisible, 1=normal (underline), 2="very visible" (block)
    # Normal cursor is disabled by default in some X11 terminal emulators
    # such as xterm and gnome-terminal, so we only enable it in "real"
    # tty terminals consoles such as the Linux console
    if input.is_console:
        curses.curs_set(1)
    else:
        curses.curs_set(0)

    screen = window.Screen(stdscr, (g.ROWS, g.COLS))

    game = Game(screen)
    if args.savegame:
        game.load(args.savegame)
    else:
        game.new()

    game.play()
