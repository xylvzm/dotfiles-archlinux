#!/bin/sh

logdir="$HOME/.local/state/rice-startup"
mkdir -p "$logdir"
uid="$(id -u)"

start_once() {
    name="$1"
    shift
    if ! pgrep -u "$uid" -x "$name" >/dev/null; then
        "$@" >>"$logdir/$name.log" 2>&1 &
    fi
}

# Mako replaces our previous Dunst setup.
pkill -u "$uid" -x dunst 2>/dev/null || true

start_once hyprpaper hyprpaper
start_once mako mako
start_once waybar waybar \
    -c "$HOME/.config/waybar/config.jsonc" \
    -s "$HOME/.config/waybar/style.css"

# Eww's daemon command safely handles an already-running daemon.
eww -c "$HOME/.config/eww" daemon >>"$logdir/eww.log" 2>&1 &

# Keep the existing now-playing notifications.
if [ -f "$HOME/.config/dunst/now-playing.py" ]; then
    if ! pgrep -u "$uid" -f \
        '^python3 /home/xylvzm/.config/dunst/now-playing.py$' >/dev/null; then
        python3 "$HOME/.config/dunst/now-playing.py" \
            >>"$logdir/now-playing.log" 2>&1 &
    fi
fi
