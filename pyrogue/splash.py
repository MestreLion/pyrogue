#!/usr/bin/env python2
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

'''Display the splash (title) image'''

import os
import logging

try:
    import pygame
except ImportError:
    pygame = None

try:
    from . import enum
except ImportError:
    import enum
except ValueError:
    import enum


log = logging.getLogger(__name__)

class COLOR(enum.Enum):
    BLACK   = (  0,   0,   0)
    RED     = (255,   0,   0)
    GREEN   = (  0, 255,   0)
    BLUE    = (  0,   0, 255)
    CYAN    = (  0, 255, 255)
    MAGENTA = (255,   0, 255)
    YELLOW  = (255, 255,   0)
    WHITE   = (255, 255, 255)


CGA_COLORS = [
    COLOR.BLACK,
    COLOR.CYAN,
    COLOR.MAGENTA,
    COLOR.WHITE,
]

CGA_SIZE = (320, 200, 2)  # 2 bits per pixel = 4 colors
FPS = 10


def display_ascii(filename, timeout=0, size=(), fullscreen=False):
    return display_sdl(filename, timeout, size, fullscreen, videodriver="caca")

def display_sdl(filename, timeout=0, size=(), fullscreen=False, videodriver=""):
    '''Display an image in PIC/BSAVE format using SDL
        for <timeout> milliseconds or until a key is pressed,
        <size> is the window size, the image itself must be CGA
        Suggested <videodriver>s: caca (colored ascii-art), fbcon
    '''
    if pygame is None:
        log.warn("pygame module is required to display graphics using SDL")
        return

    if videodriver:
        os.environ['SDL_VIDEODRIVER'] = videodriver

    # Disable mouse, just in case a video user is in console
    # It would enable fbcon, which throws exception if mouse is missing
    os.environ.setdefault('SDL_NOMOUSE', '1')

    pygame.display.init()
    log.debug("Displaying using SDL. Requested and actual video driver: %s",
              (videodriver, pygame.display.get_driver()))

    flags = 0
    if fullscreen:
        flags |= pygame.FULLSCREEN

    # 960 x 600. Large enough and still safe
    bigcga = (3 * CGA_SIZE[0],
              3 * CGA_SIZE[1],)
    if not size:
        size = bigcga
    if fullscreen or size == (0, 0):
        size = (pygame.display.Info().current_w,
                pygame.display.Info().current_h,)
    if size == (0, 0):  # pygame Info() failed. (can be caca)
        size = bigcga

    log.debug("Initializing display in mode %s, fullscreen %s", size, fullscreen)

    screen = pygame.display.set_mode(size, flags)
    image = pygame.surface.Surface(CGA_SIZE[:2])
    load_pic(filename, image)
    try:
        screen.blit(pygame.transform.smoothscale(image, screen.get_size()), (0, 0))
    except ValueError:
        screen.blit(pygame.transform.scale(image, screen.get_size()), (0, 0))  # caca
    pygame.display.update()

    clock = pygame.time.Clock()
    running = True
    elapsed = 0
    while running and (timeout == 0 or elapsed < timeout):
        for event in pygame.event.get():
            if event.type in (pygame.QUIT,
                              pygame.KEYDOWN,
                              pygame.MOUSEBUTTONDOWN):
                running= False
        elapsed += clock.tick(FPS)

    pygame.quit()


def load_pic(filename, surface):
    lines = bload(filename)
    for row, line in enumerate(lines):
        for col, color in enumerate(line):
            surface.set_at((col, row), CGA_COLORS[color])


def bload(filename):
    '''Load a BSAVE CGA image and return a tuple with
        <rows> de-interlaced tuples, each line containing
        <cols> CGA color indexes
    '''
    cols, rows, bpp = CGA_SIZE
    bypl = cols * bpp // 8  # bytes per line

    evens = []
    odds  = []

    with open(filename, mode='rb') as fp:
        fp.read(7)  # Ignore header
        for lines in (evens, odds):
            for _ in range(rows//2):
                lines.append(sum(map(tuple, map(unpackcga,
                                                fp.read(bypl))), ()))
            fp.read(192)  # Ignore padding

    # De-interlace the lines
    log.debug("Loaded '%s', image dimensions: %s x %s",
              filename, len(evens[0] if evens else[]), len(evens) + len(odds))

    return sum(zip(evens, odds), ())


def unpackcga(chars):
    '''Simplified version of unpackbyte() with CGA parameters'''
    for c in chars:
        for offset in (6, 4, 2, 0):
            yield (ord(c) >> offset) & 3


def unpackbyte(chars, bpu=2):
    '''Simplified version of unpackbits()
        works only for bpu in (1, 2, 4), ie, units fully fits a byte.
    '''
    mask = 2**bpu - 1
    offsets = tuple(reversed(range(0, 8, bpu)))
    for c in chars:
        for offset in offsets:
            yield (ord(c) >> offset) & mask


def unpackbits(chars, bpu=2):
    '''Unpack <chars> bytestring, yielding every <bpu> bits as an integer
        Examples:
            CGA Colors: unpackbits(b'axx', 2) -> (0, 2, 3, ...), len=24
            base64-ish: unpackbits(b'Man', 6) -> (19, 22, 5, 46), len=4
        For <bpu> in (1, 2, 4), use the simplified version unpackcga()
    '''
    bypg = bpu // gcd(bpu, 8)
    groups = len(chars) // bypg
    mask = 2**bpu - 1
    offsets = tuple(reversed(range(0, 8 * bypg, bpu)))
    for group in (chars[bypg*i:bypg*(i+1)] for i in range(groups)):
        word = sum(ord(char) << (8 * i)
                   for i, char in enumerate(reversed(group)))
        for offset in offsets:
            yield (word >> offset) & mask


def gcd(a, b):
    '''Return greatest common divisor using Euclid's Algorithm'''
    while b:
        a, b = b, a % b
    return a




if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG)
        display_sdl(os.path.join(os.path.dirname(__file__), '..', 'rogue.pic'),
                    timeout=0, size=(0, 0), fullscreen=False)
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
