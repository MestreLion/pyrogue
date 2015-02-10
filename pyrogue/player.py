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

'''Player class'''

import logging

from . import g
from . import rnd
from . import enum


log = logging.getLogger(__name__)


class HUNGER(enum.Enum):
    '''Minimum food in stomach before some effect or warning
        Values represent the last "safe" food amount before the step
    '''
    HUNGRY =  300  # WEAK * 2 in DOS. No effect, just a warning.
    WEAK   =  150  # No effect either, just the warning
    FAINT  =    0  # Start fainting. Unix: 20
    STARVE = -851  # Die of starvation. Unix: 0. Ouch! :)
        # This is the effective value in DOS, intended was probably -850

    @classmethod
    def name(cls, v):
        if v == cls.STARVE: return "?"  # Per DOS code, but never seen by player
        return super(HUNGER, cls).name(v)


class Player(object):

    # Constants
    char    =  "@"  # Display character
    ac      =    1  # Armor Class when wearing no armor
    stomach = 2000  # Stomach size, how much food can the player have

    xplevels = tuple(10*2**xplevels for xplevels in range(19)) + (0,)

    def __init__(self, name, screen=None):
        self.name = name

        # Input and output
        self.screen = screen

        # Map and position
        self.level = None
        self.row = 0
        self.col = 0

        # Items
        self.armor     = None  # Worn armor
        self.weapon    = None  # Wielded weapon
        self.ringright = None  # Ring on right hand
        self.ringleft  = None  # Ring on left hand
        self.pack      = []    # Inventory (list of items)

        # Main status
        self.hp      = 12      # Current hit points left (life)
        self.hpmax   = 12      # Maximum hit points
        self.str     = 16      # Current strength
        self.strmax  = 16      # Maximum strength
        self.gold    = 0       # Gold (purse)
        self.xp      = 0       # Experience points
        self.xplevel = 1       # Experience level

        # Food left in stomach. Fixed 1250 in Unix
        self.food = rnd.spread(1300)

        # Condition status and flags
        self.skipturns = 0  # Used by sleep, faint, freeze, etc

    @property
    def armorclass(self):
        if self.armor is None:
            return self.ac
        else:
            return self.armor.ac

    @property
    def hungerstage(self):
        '''Name of the hunger stage, based on current food in stomach'''
        # DOS: "Faint" in status bar is only displayed after player actually
        #  faints for the first time. This would require a private property,
        #  `hungry_stage` or similar, which would defeat the whole point
        #  of this function.
        for food in HUNGER:
            if self.food < food:
                return HUNGER.name(food)
        else:
            return ""  # All fine :)

    @property
    def metabolism(self):
        '''How much food is consumed every turn.
            Depends on current food, worn rings and screen width.
            Some rings have random consumption, so this value may change
            on every read!
        '''
        deltafood = 1

        if self.food <= HUNGER.FAINT:
            return deltafood

        for ring in (self.ringleft,
                     self.ringright):
            if ring is not None:
                deltafood += ring.consumption

        # DOS: 40 column mode use food twice as fast
        if self.screen.size[1] <= 40:
            deltafood *= 2

        return deltafood

    @property
    def has_amulet(self):
        return "AMULET" in self.pack  # @@fake

    # ACTIONS ###########

    def move(self, dr, dc):
        row = self.row + dr
        col = self.col + dc

        if not self.level.is_passable(row, col):
            return

        # Update current tile
        self.level.reveal(self.row, self.col)

        # Update to new position
        self.row = row
        self.col = col
        self.level.draw(self)

        self.level.tick()

    def rest(self):
        '''Do nothing for a turn'''
        self.level.tick()

    # DAEMONS ###########

    def heal(self):
        pass

    def digest(self):
        '''Deplete food in stomach'''
        # Unix has very different mechanics, specially on fainting and rings

        oldfood = self.food
        self.food -= self.metabolism

        if self.food < HUNGER.STARVE:
            raise g.Lose("Starvation")

        if self.food < HUNGER.FAINT:
            # 80% chance to avoid fainting, if not already
            if self.skipturns > 0 or rnd.perc(80):
                return

            # Faint for a few turns
            self.skipturns += rnd.rand(4, 11)  # Harsh!

            #@@ Disable running
            #@@ Cancel multiple actions

            # DOS 1.1: "%sYou faint", "You feel too weak from lack of food.  "
            self.screen.message("%sYou faint from the lack of food",
                                "You feel very weak. ")
            return

        if self.food < HUNGER.WEAK and oldfood >= HUNGER.WEAK:
            self.screen.message("You are starting to feel weak")

        elif self.food < HUNGER.HUNGRY and oldfood >= HUNGER.HUNGRY:
            self.screen.message("You are starting to get hungry")
