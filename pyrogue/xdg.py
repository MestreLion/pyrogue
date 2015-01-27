# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015 Freedesktop.org <http://freedesktop.org>
#    License: GNU Lesser General Public License v2 (LGPLv2)

'''Partial xdg.BaseDirectory for systems lacking Python 3 xdg support'''

import os

_home = os.path.expanduser('~')

xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or \
                  os.path.join(_home, '.config')

xdg_config_dirs = [xdg_config_home] + \
                  (os.environ.get('XDG_CONFIG_DIRS') or '/etc/xdg').split(':')

xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or \
                 os.path.join(_home, '.cache')

def save_config_path(*resource):
    """Ensure $XDG_CONFIG_HOME/<resource>/ exists, and return its path.
    'resource' should normally be the name of your application. Use this
    when SAVING configuration settings. Use the xdg_config_dirs variable
    for loading."""
    resource = os.path.join(*resource)
    assert not resource.startswith('/')
    path = os.path.join(xdg_config_home, resource)
    if not os.path.isdir(path):
        os.makedirs(path, 0o700)
    return path
