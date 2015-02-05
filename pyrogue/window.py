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
import operator
import functools
import logging
import time
import curses
import locale

from . import input

try:
    import enum
except ImportError:
    from . import enum


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


class COLOR(enum.Enum):
    DEFAULT = -1  # Terminal default. Actual color depends on context, fg/bg
    BLACK   =  0  # Background
    RED     =  1
    GREEN   =  2
    YELLOW  =  3
    BLUE    =  4  # DOS: Light Blue
    MAGENTA =  5
    BROWN   =  6  # 6 is CYAN in curses
    WHITE   =  7

# CP437 codes comes from rogue.h @ DEFINEs,
# Colors from curses.c @ color_attr[] and addch(chr)
chars = {
    '@': ('@', u('\u263A'), 0x01, COLOR.YELLOW),   # ☺, Player
    '^': ('^', u('\u2666'), 0x04, COLOR.MAGENTA),  # ♦, Trap
    ':': (':', u('\u2663'), 0x05, COLOR.RED),      # ♣, Food
    ']': (']', u('\u25D8'), 0x08, COLOR.BLUE),     # ◘, Armor
    '=': ('=', u('\u25CB'), 0x09, COLOR.BLUE),     # ○, Ring
    ',': (',', u('\u2640'), 0x0C, COLOR.BLUE),     # ♀, Amulet
    '?': ('?', u('\u266A'), 0x0D, COLOR.BLUE),     # ♪, Scroll
    '*': ('*', u('\u263C'), 0x0F, COLOR.YELLOW),   # ☼, Gold
    ')': (')', u('\u2191'), 0x18, COLOR.BLUE),     # ↑, Weapon
    '!': ('!', u('\u00A1'), 0xAD, COLOR.BLUE),     # ¡, Potion
    '#': ('#', u('\u2591'), 0xB1, COLOR.WHITE),    # ░, Passage (Corridor/Tunnel)
    '+': ('+', u('\u256C'), 0xCE, COLOR.BROWN),    # ╬, Door
    '/': ('/', u('\u03C4'), 0xE7, COLOR.BLUE),     # τ, Stick (Staff/Wand/Rod)
    '.': ('.', u('\u00B7'), 0xFA, COLOR.GREEN,     # ·, Floor
          curses.A_BOLD),
    '%': ('%', u('\u2261'), 0xF0, COLOR.GREEN,     # ≡, Stairs
          curses.A_REVERSE | curses.A_BLINK),      #    DOS: color 160, black on green

    '|': ('|', u('\u2551'), 0xBA, COLOR.BROWN),    # ║, V Wall
    '-': ('-', u('\u2550'), 0xCD, COLOR.BROWN),    # ═, H Wall
    '1': ('-', u('\u2554'), 0xC9, COLOR.BROWN),    # ╔, UL corner
    '2': ('-', u('\u2557'), 0xBB, COLOR.BROWN),    # ╗, UR corner
    '3': ('-', u('\u255A'), 0xC8, COLOR.BROWN),    # ╚, LL corner
    '4': ('-', u('\u255D'), 0xBC, COLOR.BROWN),    # ╝, LR corner

    '$': ('$', '$',         0x24, COLOR.WHITE),    # Magic (Good)
    '&': ('&', '+',         0x26, COLOR.WHITE),    # Magic (Bad)

    ' ': (' ', ' ',         0x20, COLOR.BLACK),    # Background
}

colors = {}  # To be initialized after curses


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
        char, attrs = self.charattrs("-")
        self.window.addstr(srow, scol + 1, char * (size[1]-2), attrs)
        self.window.addstr(erow, scol + 1, char * (size[1]-2), attrs)

        # Vertical walls and floor
        char, attrs = self.charattrs("|")
        for row in range(srow + 1, erow):
            self.window.addstr(row, scol, char, attrs)
            self.window.addstr(row, ecol, char, attrs)

        # Corners
        self.window.addstr(srow, scol, *self.charattrs("1"))
        self.window.addstr(srow, ecol, *self.charattrs("2"))
        self.window.addstr(erow, scol, *self.charattrs("3"))
        self.window.insstr(erow, ecol, *self.charattrs("4"))

        # Floor
        for row in range(srow + 1, erow):
            for col in range(scol + 1, ecol):
                self.window.addstr(row, col, *self.charattrs('.'))

    def move(self, obj, dr, dc):
        row = obj.row + dr
        col = obj.col + dc
        mr, mc = self.size

        # Account for walls on edges
        if (row < 1 or
            col < 1 or
            row > mr - 2 or
            col > mc - 2):
            return False

        # Erase previous
        self.window.addstr(obj.row, obj.col, *self.charattrs('.'))

        # Set new
        obj.row = row
        obj.col = col
        self.window.addstr(row, col, *self.charattrs(obj.char))
        return True

    def charattrs(self, char):
        if char in chars:
            c = chars[char]
            return c[1], functools.reduce(operator.or_, c[4:], colors[c[3]])


class Screen(Window):
    def __init__(self, stdscr, size):
        self.parent = None
        self.position = (0, 0)
        self.size = size
        self.window = stdscr
        if self.size != self.window.getmaxyx():
            self.window.resize(*size)

        self.dungeon = Window(self.window, (4, 0), (self.size[0]-7,
                                                    self.size[1]))
        self.dungeon.box()

        # Upper box - chars showcase
        self.box((1, 0), (3, self.size[1]))
        text = center("".join([' {} '.format(_)
                               for _ in sorted(chars,
                                               key=lambda _: chars[_][2])]),
                      self.size[1] - 2)
        for col, char in enumerate(text, 1):
            self.window.addstr(2, col, *self.charattrs(char))

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
        self.window.addstr(self.size[0]-2, 0, msg, colors[COLOR.YELLOW])

        # Extra, temporary status bar
        msg = ("Food:{:4d}\t"
               "Pos: ({:2d},{:2d})").format(
                player.food,
                player.row,
                player.col)
        self.window.addstr(self.size[0]-3, 0, msg)

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
        for i, (led, on) in enumerate(input.keyboard_leds()):
            width = len(led)
            self.window.move(row, 26 + width * i)
            if on:
                self.window.addstr(led, curses.A_REVERSE)
            else:
                self.window.addstr(width * ' ')

        # Current time
        msg = time.strftime("%H:%M")
        self.window.addstr(row, cols - len(msg) - 1, msg, curses.A_REVERSE)

    def message(self, terse, noterse="", *args, **kwargs):
        text = terse + noterse  # for now...
        msg = text.format(*args, **kwargs).replace('\n', '\\n').replace('\0', '\\0')
        log.info(msg)
        self.window.addnstr(0, 0, left(msg, self.size[1]), self.size[1])

    def clear_message(self):
        self.window.move(0, 0)
        self.window.clrtoeol()

    def update(self, player):
        self.statusbar(player)
        self.systembar()
        self.dungeon.window.move(player.row, player.col)
        self.window.refresh()
