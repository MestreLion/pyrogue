#!/usr/bin/env python
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
import sys
import logging
import locale

try:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # silence ad
    import pygame
except ImportError:
    pygame = None

try:
    from . import enum
except ImportError:
    import enum
except ValueError:
    import enum


if sys.version < '3':
    import codecs
    def u(x):
        return (codecs.unicode_escape_decode(x)[0].
            encode(locale.getpreferredencoding()))
    def b(x):
        return ord(x)
else:
    def u(x):
        return x
    def b(x):
        return x

log = logging.getLogger(__name__)


class COLOR(enum.Enum):
    BLACK   = (  0,   0,   0)
    RED     = (255,   0,   0)
    GREEN   = (  0, 255,   0)
    BLUE    = (  0,   0, 255)
    YELLOW  = (255, 255,   0)
    MAGENTA = (255,   0, 255)
    CYAN    = (  0, 255, 255)
    WHITE   = (255, 255, 255)

CGA_COLORS = [
    COLOR.BLACK,
    COLOR.CYAN,
    COLOR.MAGENTA,
    COLOR.WHITE,
]

CGA_SIZE = (320, 200, 2)  # 2 bits per pixel = 4 colors
FPS = 10

# Map CGA to 8-color terminal indexes
cgaterm = {0: 0,  # Black
           1: 6,  # Cyan
           2: 5,  # Magenta
           3: 7}  # White


def display_ascii(filename, div=4, bgcolor=None):
    """
    cols, rows = (CGA_SIZE[0] // 2,
                  CGA_SIZE[1] // 4)
    """
    # Sizes
    if div == 1:
        cdiv = 1
        n = 2
    else:
        cdiv = int(div / 2)
        n = 1

    # Colors
    # Stop right there before reinventing tput!
    termreset = u("\033[00m")
    def coloresc(i):
        if os.environ['TERM'] == 'linux':  # actually, if colors == 8
            esc = '1;3' + str(i) if i else '0;30'
        else:
            esc = i + (90 if i else 30)
        return u("\033[%sm" % (esc,))
    def termcolor(i, n=1, bgcolor=None, char="\u2588"):
        if bgcolor is None or not i == bgcolor:
            out = escs[i]
        else:
            out = termreset
            char = u(' ')
        return out + n * u(char)
    # Map CGA colors to terminal escape strings
    escs = tuple(coloresc(cgaterm[i]) for i in range(len(cgaterm)))
    # Map CGA colors to output string
    colors = tuple(termcolor(i, n, bgcolor) for i in range(len(cgaterm)))

    lines = bload(filename)
    print(termreset, end='')
    for line in lines[::div]:
        print("".join(colors[c] for c in line[::cdiv]))
    print(termreset, end='', flush=True)


def display_sdl_ascii(filename, timeout=0, size=(), fullscreen=False):
    return display_sdl(filename, timeout, size, fullscreen, videodriver="caca")


def display_sdl(filename, timeout=0, size=(), fullscreen=False, videodriver=""):
    '''Display an image in PIC/BSAVE format using SDL
        for <timeout> milliseconds or until a key is pressed,
        <size> is the window size, the image itself must be CGA
        Suggested <videodriver>s: caca (colored ascii-art), fbcon
    '''
    if pygame is None:
        log.error("pygame module is required to display graphics using SDL")
        return

    if videodriver:
        os.environ['SDL_VIDEODRIVER'] = videodriver

    # Disable mouse, just in case a video user is in console
    # It would enable fbcon, which throws exception if mouse is missing
    os.environ.setdefault('SDL_NOMOUSE', '1')

    try:
        pygame.display.init()
    except pygame.error as e:
        log.error("Could not initialize video driver '%s': %s", videodriver, e)
        return

    log.debug("Displaying using SDL. Requested and actual video driver: %s",
              (videodriver, pygame.display.get_driver()))

    flags = 0
    if fullscreen:
        flags |= pygame.FULLSCREEN

    if fullscreen and not size:
        size = (pygame.display.Info().current_w,
                pygame.display.Info().current_h,)
    elif not size:
        size = 1
    if isinstance(size, int):
        size = (size * CGA_SIZE[0],
                size * CGA_SIZE[1],)

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


def export_pic(infile, outfile):
    if pygame is None:
        log.error("pygame module is required to display graphics using SDL")
        return
    image = pygame.surface.Surface(CGA_SIZE[:2])
    load_pic(infile, image)
    pygame.image.save(image, outfile)


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
            for __ in range(rows//2):
                lines.append(sum(map(tuple, map(unpackcga,
                                                fp.read(bypl))), ()))
            fp.read(192)  # Ignore padding

    # De-interlace the lines
    log.debug("Loaded '%s', image dimensions: %s x %s",
              filename, len(evens[0] if evens else[]), len(evens) + len(odds))

    return sum(zip(evens, odds), ())


def unpackcga(char):
    """Faster version of unpackbyte() with CGA parameters (2 bits per unit).

    Unpack a byte to 4 individual 2-bit values
    """
    i = b(char)
    for offset in (6, 4, 2, 0):
        yield (i >> offset) & 3


def unpackbyte(chars, bpu=2):
    """Faster version of unpackbits() for bits per unit in (1, 2, 4)."""
    assert bpu in (1, 2, 4), "bits per unit must be 1, 2 or 4. Use unpackbits() instead"
    mask = 2**bpu - 1
    offsets = tuple(reversed(range(0, 8, bpu)))
    for c in chars:
        for offset in offsets:
            yield (ord(c) >> offset) & mask


def unpackbits(chars, bpu=2):
    """Unpack <chars> bytestring, yielding every <bpu>-bit units as an integer.

    Examples:
        CGA Colors: unpackbits(b'axx', 2) -> (0, 2, 3, ...), len=24
        base64-ish: unpackbits(b'Man', 6) -> (19, 22, 5, 46), len=4

    For <bpu> in (1, 2, 4), use the faster unpackbytes()
    """
    def gcd(a, b):
        """Return greatest common divisor using Euclid's Algorithm"""
        while b:
            a, b = b, a % b
        return a
    bypg = bpu // gcd(bpu, 8)
    groups = len(chars) // bypg
    mask = 2**bpu - 1
    offsets = tuple(reversed(range(0, 8 * bypg, bpu)))
    for group in (chars[bypg*i:bypg*(i+1)] for i in range(groups)):
        word = sum(ord(char) << (8 * i)
                   for i, char in enumerate(reversed(group)))
        for offset in offsets:
            yield (word >> offset) & mask




if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG)
        splashfile = os.path.join(os.path.dirname(__file__), '..', 'rogue.pic')
        #export_pic(splashfile, 'teste.png')
        display_ascii(splashfile)
        # 960 x 600. Large enough and still safe
        display_sdl(splashfile, timeout=0, size=0, fullscreen=True)
    except KeyboardInterrupt:
        pass
    finally:
        if pygame:
            pygame.quit()
