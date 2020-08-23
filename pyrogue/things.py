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

'''Items, Weapons, Armor, etc'''

import string


# Liquid colors for potions
rainbow = (
    "amber",
    "aquamarine",
    "black",
    "blue",
    "brown",
    "clear",
    "crimson",
    "cyan",
    "ecru",
    "gold",
    "green",
    "grey",
    "magenta",
    "orange",
    "pink",
    "plaid",
    "purple",
    "red",
    "silver",
    "tan",
    "tangerine",
    "topaz",
    "turquoise",
    "vermilion",
    "violet",
    "white",
    "yellow"
)

# Stone materials and values for rings
stones = {
    "agate":           25,
    "alexandrite":     40,
    "amethyst":        50,
    "carnelian":       40,
    "diamond":        300,
    "emerald":        300,
    "germanium":      225,
    "granite":          5,
    "garnet":          50,
    "jade":           150,
    "kryptonite":     300,
    "lapis lazuli":    50,
    "moonstone":       50,
    "obsidian":        15,
    "onyx":            60,
    "opal":           200,
    "pearl":          220,
    "peridot":         63,
    "ruby":           350,
    "sapphire":       285,
    "stibotantalite": 200,
    "tiger eye":       50,
    "topaz":           60,
    "turquoise":       70,
    "taaffeite":      300,
    "zircon":          80,
}

# Wood types for Staffs and Rods
wood = (
    "avocado wood",
    "balsa",
    "bamboo",
    "banyan",
    "birch",
    "cedar",
    "cherry",
    "cinnibar",
    "cypress",
    "dogwood",
    "driftwood",
    "ebony",
    "elm",
    "eucalyptus",
    "fall",
    "hemlock",
    "holly",
    "ironwood",
    "kukui wood",
    "mahogany",
    "manzanita",
    "maple",
    "oaken",
    "persimmon wood",
    "pecan",
    "pine",
    "poplar",
    "redwood",
    "rosewood",
    "spruce",
    "teak",
    "walnut",
    "zebrawood"
)

# Metallic materials for Staffs and Rods
metal = (
    "aluminum",
    "beryllium",
    "bone",
    "brass",
    "bronze",
    "copper",
    "electrum",
    "gold",
    "iron",
    "lead",
    "magnesium",
    "mercury",
    "nickel",
    "pewter",
    "platinum",
    "steel",
    "silver",
    "silicon",
    "tin",
    "titanium",
    "tungsten",
    "zinc"
)

# For Scroll name generator
vowels     = "aeiou"
consonants = "".join((__ for __ in string.ascii_lowercase if __ not in vowels))


class Item(object):
    def __init__(self, *args, **kwargs):
        pass


class Amulet(Item):
    char = ','


class Gold(Item):
    char = '*'
    name = "Gold"
    def __init__(self, gold):
        self.gold = gold
