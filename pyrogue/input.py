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

'''
Abstraction layer to deal with terminal keyboard input
and related curses methods and constants
'''

import os
import sys
import curses
import locale

from . import enum


if sys.version < '3':
    def b2s(b):
        return b
else:
    def b2s(b):
        return str(b, encoding=locale.getpreferredencoding())


class MOVE(enum.Enum):
    UP         = (curses.KEY_UP,    ord('k'))
    DOWN       = (curses.KEY_DOWN,  ord('j'))
    LEFT       = (curses.KEY_LEFT,  ord('h'))
    RIGHT      = (curses.KEY_RIGHT, ord('l'))
    UP_RIGHT   = (curses.KEY_PPAGE, ord('u'))
    DOWN_RIGHT = (curses.KEY_NPAGE, ord('n'))
    UP_LEFT    = (curses.KEY_HOME,  ord('y'), curses.KEY_FIND)
    DOWN_LEFT  = (curses.KEY_END,   ord('b'), curses.KEY_SELECT)


KEY = type("KEY",
           (enum.Enum,),
           {KEY[4:]: getattr(curses, KEY)
            for KEY in dir(curses)
            if KEY.startswith("KEY_")})


def getch(window):
    '''Get a character from user. Blocks until input.
        Wrapper for curses.window.getch()
    '''
    return window.window.getch()


def unctrl(ch):
    '''Return a a printable representation of character ch.
        Control characters are displayed with a caret, for example ^C.
        Printing characters are left as they are.
        Wrapper for curses.unctrl()
    '''
    return b2s(curses.unctrl(ch))


if os.environ.get('DISPLAY') is None:

    is_console = True

    def keyboard_leds():
        import struct
        import fcntl

        DEVICE = '/dev/tty'
        KDGETLED = 0x4B31
        SCRLOCK = 0x01
        NUMLOCK = 0x02
        CAPLOCK = 0x04

        leds = 0
        try:
            fd = os.open(DEVICE, os.O_WRONLY)
            retbytes = fcntl.ioctl(fd, KDGETLED, struct.pack('I', 0))
            [leds] = struct.unpack('I', retbytes)
        except IOError:  # not a true tty console, but an X11 terminal emulator
            pass

        return (("NUM LOCK", bool(leds & NUMLOCK)),
                ("CAP LOCK", bool(leds & CAPLOCK)),
                ("SCR LOCK", bool(leds & SCRLOCK)))


else:

    is_console = False

    def keyboard_leds():
        import subprocess

        SCRLOCK = 0x04
        NUMLOCK = 0x02
        CAPLOCK = 0x01

        leds = 0
        try:
            for line in (subprocess.check_output(["xset", "-q"]).
                         decode(locale.getpreferredencoding()).
                         split('\n')):
                if 'LED mask' in line:
                    leds = int(line.split(' ')[-1])
                    break
        except subprocess.CalledProcessError:
            pass

        return (("NUM LOCK", bool(leds & NUMLOCK)),
                ("CAP LOCK", bool(leds & CAPLOCK)),
                ("SCR LOCK", bool(leds & SCRLOCK)))
