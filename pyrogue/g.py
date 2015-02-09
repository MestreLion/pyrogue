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

'''Global constants and paths'''

import os.path
import logging

try:
    import xdg.BaseDirectory as xdg
except ImportError:
    from . import xdg


log = logging.getLogger(__name__)

# General
VERSION = "0.1"
APPNAME = __package__

# Paths
GAMEDIR = os.path.abspath(os.path.dirname(__file__) or '.')
CONFIGDIR = xdg.save_config_path(APPNAME)

# Misc
COLS, ROWS = (80, 25)  # Screen size
PLAYERNAME = "MestreLion"  # Player default name
AMULETLEVEL = 5  # Level Amulet starts appearing @for now

# Custom exceptions
class GameError(Exception): pass
class Win(GameError): pass
class Lose(GameError): pass
