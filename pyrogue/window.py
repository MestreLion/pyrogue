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


def align(text, width, align, fill=' '):
    return "{0:{1}{2}{3}}".format(text.replace("\t", 4 * " "),
                                  fill, align, width)

def left(  text, width): return align(text, width, "<")
def center(text, width): return align(text, width, "^")
def right( text, width): return align(text, width, ">")


def statusbar(window, player):
    rows, cols = window.getmaxyx()
    msg = center("Screen size: {} x {}\t"
                 "Color support: {}\t"
                 "RGB support: {}".format(
                        cols, rows,
                        curses.has_colors(),
                        curses.can_change_color()),
                 cols)  # last line has width - 1 to avoid scrolling
    window.insstr(rows-1, 0, msg, curses.A_REVERSE)

def box(window, position, size):
    subwin = window.subwin(*(size + position))
    subwin.box()
