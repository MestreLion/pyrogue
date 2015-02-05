#!/bin/bash
#
# pyrogue - Python port of the PC-DOS classic game Rogue
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
#
# Launches the game in a new, customized xterm window

fullscreen=0

rogueargs=()
xtargs=(-fa 'Perfect DOS VGA 437 Unicode' -fs 24 -geometry 80x25 +bdc)
gamecmd=$(dirname "$(readlink -f "$0")")/pyrogue.sh

usage() {
	echo "Launch Rogue in a new, customized Xterm window"
	echo "Usage: ${0##.*/} [-h] [-f|--fullscreen] [rogue args]"
	echo "Try '$(basename "$gamecmd") --help' for help on Rogue arguments"
	exit
}

# Pre-parse for `help`
for arg in "$@"; do [[ "$arg" == "-h" || "$arg" == "--help" ]] && usage ; done

while (( $# )); do
	case "$1" in
	-f|--full-screen) fullscreen=1;;
	*) rogueargs+=("$1");;
	esac
	shift
done

if ((fullscreen)); then
	xtargs+=(-fullscreen)
fi

export ROGUETERM=xterm  # hint for the launcher to bypass TERM sniffing

xterm "${xtargs[@]}" -e "$gamecmd" "${rogueargs[@]}"
