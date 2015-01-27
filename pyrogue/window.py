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

import logging
import curses


log = logging.getLogger(__name__)


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

    def box(self, position=(), size=()):
        if not position:
            position = (0, 0)
        if not size:
            size = self.size
        boxwin = Window(self.window, position, size)
        boxwin.window.box()
        return boxwin


class Screen(Window):
    def __init__(self, stdscr, size):
        self.parent = stdscr
        self.position = (0, 0)
        self.size = size
        self.window = curses.newwin(*(self.size + self.position))
        self.dungeon = Window(self.window, (1, 0), (self.size[0]-3, self.size[1]))
        self.dungeon.box()

    def statusbar(self, player):
        rows, cols = self.size
        msg = center("Screen size: {} x {}\t"
                     "Color support: {}\t"
                     "RGB support: {}".format(
                            cols, rows,
                            curses.has_colors(),
                            curses.can_change_color()),
                     cols)
        self.window.insstr(rows-1, 0, msg, curses.A_REVERSE)

    def message(self, text, *args, **kwargs):
        msg = text.format(*args, **kwargs).replace('\n', '\\n').replace('\0', '\\0')
        log.info(msg)
        self.window.addnstr(0, 0, left(msg, self.size[1]), self.size[1])
