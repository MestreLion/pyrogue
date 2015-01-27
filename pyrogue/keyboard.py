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

'''Environment-dependent keyboard and terminal functions'''

import os

if os.environ.get('DISPLAY') is None:

    is_console = True

    def leds():
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
            bytes = fcntl.ioctl(fd, KDGETLED, struct.pack('I', 0))
            [leds] = struct.unpack('I', bytes)
        except IOError:  # not a true tty console, but an X11 terminal emulator
            pass

        return (("NUM LOCK", bool(leds & NUMLOCK)),
                ("CAP LOCK", bool(leds & CAPLOCK)),
                ("SCR LOCK", bool(leds & SCRLOCK)))


else:

    is_console = False

    def leds():
        import subprocess

        SCRLOCK = 0x04
        NUMLOCK = 0x02
        CAPLOCK = 0x01

        leds = 0
        try:
            for line in str(subprocess.check_output(["xset", "-q"])).split('\\n'):
                if 'LED mask' in line:
                    leds = int(line.split(' ')[-1])
                    break
        except subprocess.CalledProcessError:
            pass

        return (("NUM LOCK", bool(leds & NUMLOCK)),
                ("CAP LOCK", bool(leds & CAPLOCK)),
                ("SCR LOCK", bool(leds & SCRLOCK)))


def set_term():
    '''
    Dirty hack to workaround gnome-terminal's wrong numpad HOME and END keys
    Must be done before initializing curses
    '''
    if (os.environ.get('TERM') == 'xterm'
        and os.environ.get('COLORTERM') == 'gnome-terminal'
        and os.environ.get('XTERM_SHELL') is None):
        os.environ['TERM'] = 'gnome'
