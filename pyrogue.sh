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
# Launches the game in current terminal
#
# Tries to enable 256 colors via TERM if terminal is known to support it
# and such support is available in terminfo database
#
# Also, for known gnome-terminals that reports TERM=xterm, the default in many
# distros, use TERM=gnome-* instead to enable keypad HOME(7) and END(1) keys.

has_terminfo() {
	local term=$1
	local termfile=terminfo/${term:0:1}/$term
	[[ -r /lib/"$termfile"       ||  # ncurses-base package
	   -r /usr/share/"$termfile" ||  # ncurses-term package
	   -r /etc/"$termfile"       ||  # empty by default
	   -r "$HOME"/."$termfile"   ]]  # dir may not exist
}

if [[ "$ROGUETERM" == gnome ]] ||
   [[ "$COLORTERM" == gnome-terminal && "$TERM" == xterm ]]
   # above sniffing will not work in gnome-terminal v3.13 onwards,
   # as it does not set COLORTERM anymore.
then
	for term in {gnome,xterm}{-256color,}; do
		if has_terminfo "$term"; then
			export TERM=$term
			break
		fi
	done
fi

gamedir=$(dirname "$(readlink -f "$0")")

cd "$gamedir"

python3 -m pyrogue "$@"
