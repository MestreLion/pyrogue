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

'''Game load and play'''

import string
import logging

from . import g
from . import input
from . import rnd
from . import enum

from .player import Player


log = logging.getLogger(__name__)


class TILE(enum.Enum):
    # FEATURES
    STAIRS   = '%'
    DOOR     = '+'
    TRAP     = '^'

    # PASSAGES
    FLOOR    = '.'
    TUNNEL   = '#'

    # OBJECTS
    ARMOR    = ']'
    WEAPON   = ')'
    SCROLL   = '?'
    POTION   = "!"
    GOLD     = '*'
    FOOD     = ':'
    STICK    = '/'
    RING     = '='
    AMULET   = ','

    # WALLS
    HORWALL  = '|'
    VERTWALL = '-'
    ULCORNER = '1'
    URCORNER = '2'
    LLCORNER = '3'
    LRCORNER = '4'
    NOTHING  = ' '

    # Things you can walk on
    # but not pick up or drop things on
    FEATURE = {
               STAIRS,
               DOOR,
               TRAP,
    }

    # Things you can walk on and pick up
    # but not drop things on
    OBJECT  = {
               ARMOR,
               WEAPON,
               SCROLL,
               POTION,
               GOLD,
               FOOD,
               STICK,
               RING,
               AMULET,
    }

    # Things you can walk and drop things on,
    # but not pick up
    PASSAGE = {
               FLOOR,
               TUNNEL,
    }

    # Things you can not walk on - cancel move
    # (and obviously not pick up or drop things onto)
    WALL    = {
               HORWALL,
               VERTWALL,
               ULCORNER,
               URCORNER,
               LLCORNER,
               LRCORNER,
               NOTHING,
    }

    # Can not walk on - initiate a fight
    MONSTER = set(string.ascii_uppercase)

# Add monsters
[setattr(TILE, _, _) for _ in string.ascii_uppercase]


class Game(object):

    def __init__(self, screen):
        self.screen = screen  # window.Screen instance to draw
        self.player = None    # player.Player instance
        self.level  = None    # Level instance of current level
        self.rng    = None    # current RNG state, may be used on save/load

    def new(self, seed=None):
        '''Initialize all names and materials, seed the random generator,
            and start a new game in Level 1
        '''
        # For reproductible results, initialize the RNG before instancing
        # any object, as Player and Level use the RNG in their initializations
        rnd.seed(seed)
        self.rng = rnd.get_state()

        self.player = Player(g.PLAYERNAME)
        self.level = Level(1, self.screen, self.player)

        self.screen.message("Hello {}.".format(self.player.name),
                            " Welcome to the Dungeons of Doom")

    def load(self, savegame):
        # load file and set all attributes that new() does
        rnd.seed()  # fake
        state = rnd.get_state()  # also fake

        rnd.set_state(state)
        self.player = Player("Loaded Game")
        self.level = Level(15, self.screen, self.player)

        self.screen.message("Hello {}.".format(self.player.name),
                            " Welcome back to the Dungeons of Doom")

    def play(self):
        # wiring between levels
        while True:
            level = self.level.play()

            if self.player.hp == 0:
                self.death()
                return

            if level == 0:
                self.win()
                return

            break  # single level, for now

            self.level = Level(level, self.screen, self.player)

    def win(self):
        self.screen.message("You win, congratulations!!")

    def death(self):
        self.screen.message("You're dead!")


class Level(object):
    def __init__(self, level, screen, player):
        self.level = level
        self.screen = screen
        self.player = player

        rows, cols = self.screen.playarea.size
        self.dungeon = rows * [cols * [TILE.FLOOR]]

        # create rooms, monsters, etc

        # position the player
        self.player.level = self
        self.player.row = int((rows - 2) / 2)
        self.player.col = int((cols - 2) / 2)
        self.draw(self.player)
        self.screen.playarea.draw(self.player.row,
                                  self.player.col,
                                  self.player.char)

    def play(self):
        while True:
            self.screen.update(self.player)

            ch = input.getch(self.screen.playarea)
            self.screen.clear_message()

            if ch == ord('Q'):
                break

            elif ch in input.MOVE.LEFT:       self.player.move( 0, -1)  # Left
            elif ch in input.MOVE.DOWN:       self.player.move( 1,  0)  # Down
            elif ch in input.MOVE.UP:         self.player.move(-1,  0)  # Up
            elif ch in input.MOVE.RIGHT:      self.player.move( 0,  1)  # Right
            elif ch in input.MOVE.UP_RIGHT:   self.player.move(-1,  1)  # Up Right
            elif ch in input.MOVE.DOWN_RIGHT: self.player.move( 1,  1)  # Down Right
            elif ch in input.MOVE.UP_LEFT:    self.player.move(-1, -1)  # Up Left
            elif ch in input.MOVE.DOWN_LEFT:  self.player.move( 1, -1)  # Down Left

            else:
                self.screen.message("Illegal command '{}'", "", input.unctrl(ch))

    def draw(self, thing):
        '''Draw something at its current position'''
        self.screen.playarea.draw(thing.row,
                                  thing.col,
                                  thing.char)

    def reveal(self, row, col):
        '''Draw tile char at (row, col)'''
        self.screen.playarea.draw(row, col, self.dungeon[row][col])

    def is_passable(self, row, col):
        return self.dungeon[row][col] not in TILE.WALL
