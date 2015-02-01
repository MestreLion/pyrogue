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
Basic implementation of enum module for Python 2 and 3

Adapted from https://github.com/MestreLion/enum
'''

__all__ = ['Enum']  # not necessary as Enum is the only non-__*__ name

import sys

class _meta(type):
    @property
    def __members__(self):
        return {k: v for k, v in self.__dict__.items()
                if  not k.startswith("_")
                and not self._callable(getattr(self, k))}

    def __iter__(self):
        '''Yield members sorted by value, not declaration order'''
        return iter(sorted(self.__members__.values()))

    def __getitem__(self, k):
        try:
            return self.__members__[k]
        except KeyError:
            # re-raise as AttributeError, for consistency with Enum.VALUE
            raise AttributeError("type object '{}' has no attribute '{}'".
                                 format(self.__name__, k))

    def __contains__(self, k):
        return k in self.__members__

    def __len__(self):
        return len(self.__members__)


class _base(object):
    @staticmethod
    def _callable(obj):
        '''Helper wrapper for callable() that works on Python 3.0 and 3.1'''
        try:
            return callable(obj)
        except NameError:
            # Python 3.0 and 3.1 has no callable()
            # which is a tiny safer than hasattr approach
            return hasattr(obj, "__call__")

    @classmethod
    def name(cls, value):
        '''
        Fallback for getting a friendly member name
        Return a titled string with underscores replaced by spaces
            AnEnum.name(AnEnum.AN_ORDINARY_MEMBER) => "An Ordinary Member"
        Enums can customize member names by overriding this method
        '''
        # value not handled in subclass name()
        for k, v in cls.__members__.items():
            if v == value:
                return k.replace('_', ' ').title()

        # Value not find. Try again using value as member name.
        # Allows usage as Enum.name("VALUE") besides Enum.name(Enum.VALUE)
        return cls.name(cls[value])

    @classmethod
    def members(cls):
        '''
        Return a list of member attribute names (strings),
        ordered by value to make it consistent with class iterator
        '''
        return sorted(cls.__members__, key=cls.__members__.get)


# Python 2
if sys.version_info[0] < 3:
    class Enum(_base):
        '''A basic implementation of Enums for Python 2'''
        __metaclass__ = _meta

# Python 3
else:
    # Python 2 see Python 3 metaclass declaration as SyntaxError, hence exec()
    exec("class Enum(_base, metaclass=_meta):"
         "'''A basic implementation of Enums for Python 3'''")

del sys, _base, _meta
