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

"""
Random Number Generator functions

Using the same formulas and similar API as original DOS Rogue
to produce identical results given the same seed
"""

import time


_seed = _initial = 1


def seed(seed=None):
    '''Resets the random number generator with the given seed
        By default uses current system time as seed
    '''
    _seed = _initial = int(seed or time.time())


def get_state():
    '''Return the current state of the RNG generator
        Currently a 2-tuple (current seed, initial seed)
    '''
    return (_seed, _initial)


def set_state(state):
    '''Sets current state of the RNG generator'''
    global _seed, _initial
    _seed, _initial = state


def rnd(n):
    '''Pick a random integer in range [0, n)'''
    if n < 1:
        return 0

    def _ran():
        '''Trivia: Magic numbers from 'Remark on Algorithm 266'
            Google that ;)
        '''
        global _seed
        _seed *= 125
        _seed %= 2796203
        return _seed

    return ((_ran() + _ran()) & 0x7fffffff) % n;


def spread(n):
    '''Return a random integer in range [n +/- 10%)'''
    return n - n // 10 + rnd(n // 5)

def roll(number, sides):
    '''Roll <number> times a dice of <sides> sides,
        and return the sum of the rolls
    '''
    return sum(rnd(sides) + 1 for number in range(number))
