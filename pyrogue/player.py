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


log = logging.getLogger(__name__)


class Player(object):

    # Constants
    char    =  "@"  # Display character
    ac      =    1  # Armor Class when wearing no armor

    stomach = 2000  # Stomach size, how much food can the player have
    hunger  =  150  # Food left for hunger effects: 2*hunger=Hungry, 1*hunger=Weak
    starve  = -850  # Food deficit (below 0) to die of starvation

    hungerstages = ((hunger * 2, ""),  # All fine :)
                    (hunger,     "Hungry"),
                    (1,          "Weak"),
                    (starve,     "Faint"))

    def __init__(self, name, dungeon, row=0, col=0):
        self.name = name
        self.dungeon = dungeon

        self.row = row
        self.col = col

        self.armor     = None  # Worn armor
        self.weapon    = None  # Wielded weapon
        self.ringright = None  # Ring on right hand
        self.ringleft  = None  # Ring on left hand
        self.pack      = []    # Inventory (list of items)

        self.hp      = 12      # Current hit points left (life)
        self.hpmax   = 12      # Maximum hit points
        self.str     = 16      # Current strength
        self.strmax  = 16      # Maximum strength
        self.gold    = 0       # Gold (purse)
        self.xp      = 0       # Experience points
        self.xplevel = 1       # Experience level
        self.food    = 1300    # Food left in stomach. 1250 in Unix, 1300+/-10% in DOS

        self.move(0, 0)

    @property
    def armorclass(self):
        if self.armor is None:
            return self.ac
        else:
            return self.armor.ac

    @property
    def hungerstage(self):
        for food, stage in self.hungerstages:
            if self.food >= food:
                return stage
        else:
            return "?"

    def move(self, dr, dc):
        if self.dungeon.move(self, dr, dc):
            self.food -= 1
