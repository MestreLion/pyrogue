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
from . import things

from .player import Player


log = logging.getLogger(__name__)

MAXLEVEL = 99  # No such restriction in DOS


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
    HORWALL  = '-'
    VERTWALL = '|'
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
[setattr(TILE, __, __) for __ in string.ascii_uppercase]


class Game(object):

    def __init__(self, screen):
        self.screen   = screen  # window.Screen instance to draw
        self.player   = None    # player.Player instance
        self.level    = None    # Level instance of current level
        self.rng      = None    # current RNG state, may be used on save/load
        self.maxlevel = 0       # deepest level player has reached

    def new(self, seed=None):
        '''Initialize all names and materials, seed the random generator,
            and start a new game in Level 1
        '''
        # For reproductible results, initialize the RNG before instancing
        # any object, as Player and Level use the RNG in their initializations
        rnd.seed(seed)
        self.rng = rnd.get_state()

        self.maxlevel = 1
        self.player = Player(g.PLAYERNAME, self.screen)
        self.level = Level(self.maxlevel, self.screen, self.player)

        # DOS 1.1: "Hello {}%s", ", Welcome to the Dungeons of Doom"
        # DOS: Had an extra space before 'Welcome', probably a typo
        self.screen.message("Hello {}%s.",
                            ". Welcome to the Dungeons of Doom",
                            self.player.name)

    def load(self, savegame):
        # load file and set all attributes that new() does
        rnd.seed()  # fake
        state = rnd.get_state()  # also fake

        rnd.set_state(state)
        self.player = Player("Loaded Game", self.screen)
        self.maxlevel = 15
        self.level = Level(self.maxlevel, self.screen, self.player)

        self.screen.msgterse("{}, Welcome back!",
                            "Hello {}, Welcome back to the Dungeons of Doom!",
                            self.player.name)

    def play(self):
        # wiring between levels
        try:
            while True:
                nextlevel = min(self.level.play(), MAXLEVEL)
                if nextlevel == 0:
                    raise g.Win()

                self.maxlevel = max(nextlevel, self.maxlevel)
                self.level = Level(nextlevel, self.screen, self.player)

        except g.Win as e:
            self.win()

        except g.Lose as e:
            self.death(e)

    def win(self):
        self.screen.message("You win, congratulations!!")
        input.getch(self.screen)

    def death(self, msg=None):
        self.screen.message("You're dead! {}", "",
                            msg or "")
        input.getch(self.screen)


class Level(object):
    def __init__(self, level, screen, player):
        self.level = level
        self.screen = screen
        self.player = player

        self.rows, self.cols = self.screen.playarea.size

        self.dungeon  = {}  # the map
        self.items    = {}
        self.monsters = {}

        for coord in ((row, col)
                      for col in range(self.rows)
                      for row in range(self.cols)):
            self.dungeon[coord] = things.Item()

        self.dungeon = [[TILE.NOTHING] * self.cols for __ in range(self.rows)]

        # create rooms, monsters, etc
        self.dig_dungeon()
        self.put_stairs()
        self.light_room()

        # position the player
        self.player.level = self
        self.player.row = int((self.rows - 2) / 2)
        self.player.col = int((self.cols - 2) / 2)
        self.draw(self.player)

    def play(self):
        while True:
            self.screen.update(self.player, self.level)

            ch = input.getch(self.screen.playarea)
            self.screen.clear_message()

            if ch == ord('Q'):
                raise g.Lose("Quit")

            elif ch == input.KEY.RESIZE:
                self.screen.message("Terminal resized")
                print("\x1b[8;25;80t")
                input.getch(self.screen.playarea)

            elif ch == input.KEY.ESC:     self.screen.message("ESC")
            elif ch == input.KEY.ALT_F9:  self.screen.message("Set macro")
            elif ch == input.ctrl('R'):   self.screen.message("Re-message")

            elif ch in input.MOVE.LEFT:       self.player.move( 0, -1)  # Left
            elif ch in input.MOVE.DOWN:       self.player.move( 1,  0)  # Down
            elif ch in input.MOVE.UP:         self.player.move(-1,  0)  # Up
            elif ch in input.MOVE.RIGHT:      self.player.move( 0,  1)  # Right
            elif ch in input.MOVE.UP_RIGHT:   self.player.move(-1,  1)  # Up Right
            elif ch in input.MOVE.DOWN_RIGHT: self.player.move( 1,  1)  # Down Right
            elif ch in input.MOVE.UP_LEFT:    self.player.move(-1, -1)  # Up Left
            elif ch in input.MOVE.DOWN_LEFT:  self.player.move( 1, -1)  # Down Left

            elif ch == ord('.'): self.player.rest()
            elif ch == ord('i'): self.player.show_inventory()

            elif ch == ord('<'):
                if self.check_stairs(down=False):
                    return self.level - 1

            elif ch == ord('>'):
                if self.check_stairs(down=True):
                    return self.level + 1

            elif ch == ord(' '):
                pass  # ignore spaces. Can be used to dismiss messages

            else:
                self.screen.message("Illegal command '{}', ch={}", "",
                                    input.unctrl(ch), ch)

    def tick(self):
        '''Advance the world one tick (turn)
            some commands, like rest, search or successful move trigger this
            others like see inventory, help or failed move do not
        '''
        self.player.heal()
        self.player.digest()
        # auto-search
        # create wander monsters
        # move monsters
        # ...

    def draw(self, thing):
        '''Draw something at its current position'''
        self.screen.playarea.draw(thing.row,
                                  thing.col,
                                  thing.char)

    def reveal(self, row, col):
        '''Draw tile char at (row, col)'''
        self.screen.playarea.draw(row, col, self.dungeon[row][col])

    def is_passable(self, row, col):
        if not (0 <= row < self.rows and
                0 <= col < self.cols):
            log.warn("Trying to move outside bounds: %d, %d", row, col)
            return False

        return self.dungeon[row][col] not in TILE.WALL

    def dig_dungeon(self):
        self.dig_room((0, 0),
                      (self.rows, self.cols))

    def dig_room(self, topleft, size):
        rows, cols = size
        srow, scol = topleft
        erow, ecol = (srow + rows - 1,  # bottom right
                      scol + cols - 1)

        log.debug("Digging room at %r, size %r: (%d, %d)-(%d, %d)",
                  topleft, size, srow, scol, erow, ecol)

        # Horizontal walls
        for row in (srow, erow):
            self.dungeon[row][scol + 1:ecol] = (cols - 2) * [TILE.HORWALL]

        # Vertical walls
        for col in (scol, ecol):
            for row in range(srow + 1, erow):
                self.dungeon[row][col] = TILE.VERTWALL

        # Corners
        self.dungeon[srow][scol] = TILE.ULCORNER
        self.dungeon[srow][ecol] = TILE.URCORNER
        self.dungeon[erow][scol] = TILE.LLCORNER
        self.dungeon[erow][ecol] = TILE.LRCORNER

        # Floor
        for row in range(srow + 1, erow):
            for col in range(scol + 1, ecol):
                self.dungeon[row][col] = TILE.FLOOR

    def light_room(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.reveal(row, col)

    def check_stairs(self, down=True):
        if self.dungeon[self.player.row][self.player.col] != TILE.STAIRS:
            self.screen.message("I see no way {}", "",
                                "down" if down else "up")
            return False

        if down:
            if self.level >= g.AMULETLEVEL - 1:
                if not self.player.has_amulet:
                    self.player.pack.append("AMULET")
                self.screen.message("You have the amulet!")
            return True

        if not self.player.has_amulet:
            self.screen.message("Your way is magically blocked")
            return False

        self.screen.message("You feel a wrenching sensation in your gut")
        return True

    def put_stairs(self):
        goodtile = False
        while not goodtile:
            row = rnd.rnd(self.rows)
            col = rnd.rnd(self.cols)
            goodtile = self.dungeon[row][col] == TILE.FLOOR
        self.dungeon[row][col] = TILE.STAIRS
