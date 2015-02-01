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

'''Window-related functions'''

import sys
import logging
import time
import curses
import locale

from . import keyboard



log = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, '')

if sys.version < '3':
    import codecs
    def u(x):
        return (codecs.unicode_escape_decode(x)[0].
            encode(locale.getpreferredencoding()))
else:
    def u(x):
        return x

def left(  text, width, fill=' '): return align(text, width, fill, "<")
def center(text, width, fill=' '): return align(text, width, fill, "^")
def right( text, width, fill=' '): return align(text, width, fill, ">")
def align( text, width, fill, align):
    return "{0:{1}{2}{3}}".format(text.replace("\t", 4 * " "),
                                  fill, align, width)


class Window(object):
    def __init__(self, parent, position, size):
        self.parent = parent
        self.position = position
        self.size = size
        self.window = self.parent.derwin(*(self.size + self.position))
        self.window.keypad(1)

    def box(self, position=(), size=()):
        if not position:
            position = (0, 0)
        if not size:
            size = self.size

        # curses.box() requires byte chars in 0-255 range, unicode not supported.
        # So must draw the box manually

        srow, scol = position
        erow, ecol = (position[0] + size[0] - 1,
                      position[1] + size[1] - 1)

        # Horizontal walls
        self.window.addstr(srow, scol + 1, '\u2550' * (size[1]-2))  # CP437 0xCD, ═, HWall
        self.window.addstr(erow, scol + 1, '\u2550' * (size[1]-2))

        # Vertical walls
        for row in range(srow + 1, erow):
            self.window.addstr(row, scol, '\u2551')  # CP437 0xBA, ║, VWall
            self.window.addstr(row, ecol, '\u2551')

        # Corners
        self.window.addstr(srow, scol, '\u2554')  # CP437 0xC9, ╔, UL
        self.window.addstr(srow, ecol, '\u2557')  # CP437 0xBB, ╗, UR
        self.window.addstr(erow, scol, '\u255A')  # CP437 0xC8, ╚, LL
        self.window.insstr(erow, ecol, '\u255D')  # CP437 0xBC, ╝, LR

    def move(self, object, dr, dc):
        row = object.row + dr
        col = object.col + dc
        mr, mc = self.size

        # Account for walls on edges
        if (row < 1 or
            col < 1 or
            row > mr - 2 or
            col > mc - 2):
            return False

        # Erase previous
        self.window.addch(object.row, object.col, ' ')

        # Set new
        object.row = row
        object.col = col
        self.window.addch(row, col, object.char)
        return True


class Screen(Window):
    def __init__(self, stdscr, size):
        self.parent = None
        self.position = (0, 0)
        self.size = size
        self.window = stdscr
        if self.size != self.window.getmaxyx():
            self.window.resize(*size)

        self.dungeon = Window(self.window, (1, 0), (self.size[0]-3, self.size[1]))
        self.dungeon.box()

    def statusbar(self, player):
        level = 1
        # Formatting rationale: all attributes should touch the ':' when
        # at their *typical* value, hence the {:2d} in Level, Hits, Str, etc
        # Gold and XP will always increase line width when up a new power of 10
        # So will the uncommon Armor >= 10 and Hits >= 100
        msg = ("Level:{:2d}\t"
               "Hits:{:2d}({:2d})\t"
               "Str:{:2d}({:2d})\t"
               "Gold:{}\t"
               "Armor:{}\t"
               "Exp:{:2d}/{}".format(
                level,
                player.hp,
                player.hpmax,
                player.str,
                player.strmax,
                player.gold,
                player.armorclass,
                player.xplevel,
                player.xp)).replace('\t', 3 * ' ')
        self.window.addstr(self.size[0]-2, 0, msg)

        row, col = self.size[0] - 1, 60
        self.window.addstr(row, col, 10 * ' ')
        hungerstage = player.hungerstage
        if hungerstage:
            self.window.addstr(row, col, hungerstage, curses.A_REVERSE)

    def systembar(self):
        row, cols = (self.size[0]-1, self.size[1])

        # Terminal capabilities (temporary)
        msg = ("Color:{:5}  "
               "RGB:{:5}".format(
                str(curses.has_colors()),
                str(curses.can_change_color())))
        self.window.addstr(row, 0, msg, curses.A_REVERSE)

        # Keyboard Scroll/Num/Caps Lock led status
        for i, (led, on) in enumerate(keyboard.leds()):
            width = len(led)
            self.window.move(row, 26 + width * i)
            if on:
                self.window.addstr(led, curses.A_REVERSE)
            else:
                self.window.addstr(width * ' ')

        # Current time
        msg = time.strftime("%H:%M")
        self.window.insstr(row, cols - len(msg), msg, curses.A_REVERSE)


    def message(self, text, *args, **kwargs):
        msg = text.format(*args, **kwargs).replace('\n', '\\n').replace('\0', '\\0')
        log.info(msg)
        self.window.addnstr(0, 0, left(msg, self.size[1]), self.size[1])
