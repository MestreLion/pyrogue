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

from . import g
from . import input
from .player import Player


class Game(object):

    def __init__(self, screen):
        self.screen = screen
        self.player = None
        self.level = None

    def new(self):
        # initialize all names and materials, seed the random generator
        self.player = Player(g.PLAYERNAME)
        self.level = Level(1, self.screen, self.player)

        self.screen.message("Hello {}.".format(self.player.name),
                            " Welcome to the Dungeons of Doom")

    def load(self, savegame):
        # load file and set all attributes that new() does
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

        # create rooms, monsters, etc

        # position the player
        self.player.dungeon = self.screen.dungeon
        self.player.row = int((self.screen.dungeon.size[0] - 2) / 2)
        self.player.col = int((self.screen.dungeon.size[1] - 2) / 2)
        self.player.move(0, 0)

    def play(self):
        while True:
            self.screen.update(self.player)

            ch = input.getch(self.screen.dungeon)

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
            self.screen.message("Ch={}, player at ({}, {}), food is {}", "",
                                ch,
                                self.player.row,
                                self.player.col,
                                self.player.food)
