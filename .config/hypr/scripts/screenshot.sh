#!/bin/sh

area=$(slurp) || exit 0
[ -n "$area" ] || exit 0

directory="$HOME/Pictures/Screenshots"
mkdir -p "$directory" || exit 1
file="$directory/$(date +%Y%m%d_%H%M%S_%N).png"

if grim -g "$area" "$file"; then
    if command -v wl-copy >/dev/null 2>&1; then
        wl-copy --type image/png < "$file"
    fi
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "Screenshot saved" "$file"
    fi
fi
