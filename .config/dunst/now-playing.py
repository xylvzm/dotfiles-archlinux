#!/usr/bin/env python3
"""Notify once per track while playing; no changes to media playback."""
import fcntl
import hashlib
import html
import os
from pathlib import Path
import subprocess
import time
import urllib.parse
import urllib.request

BASE = Path(__file__).resolve().parent
CACHE = Path.home() / '.cache' / 'rice-notifications'
CACHE.mkdir(parents=True, exist_ok=True)
lock = (CACHE / 'watcher.lock').open('w')
try:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit('Now-playing watcher is already running.')

def run(*args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=4)
        return p.stdout.strip() if p.returncode == 0 else ''
    except (OSError, subprocess.TimeoutExpired):
        return ''

def art_path(uri):
    fallback = str(BASE / 'music.svg')
    try:
        u = urllib.parse.urlsplit(uri)
        if u.scheme == 'file' and u.netloc in ('', 'localhost'):
            p = Path(urllib.parse.unquote(u.path))
            return str(p) if p.is_file() else fallback
        if u.scheme not in ('http', 'https'):
            return fallback
        target = CACHE / (hashlib.sha256(uri.encode()).hexdigest() + '.img')
        if target.is_file():
            return str(target)
        with urllib.request.urlopen(uri, timeout=3) as response:
            if urllib.parse.urlsplit(response.url).scheme not in ('http', 'https'):
                return fallback
            if not response.headers.get_content_type().startswith('image/'):
                return fallback
            data = response.read(4 * 1024 * 1024 + 1)
        if len(data) > 4 * 1024 * 1024:
            return fallback
        target.write_bytes(data)
        # Bound this disposable album-art cache.
        files = sorted(CACHE.glob('*.img'), key=lambda p: p.stat().st_mtime)
        for old in files[:-40]:
            old.unlink(missing_ok=True)
        return str(target)
    except Exception:
        return fallback

seen = {}
try:
    while True:
        players = run('playerctl', '--list-all').splitlines()
        for player in players:
            if run('playerctl', '-p', player, 'status') != 'Playing':
                continue
            def meta(key):
                return run('playerctl', '-p', player, 'metadata', key)
            title = meta('xesam:title')
            artist = meta('xesam:artist')
            identity = (meta('mpris:trackid'), title, artist, meta('xesam:url'))
            if not title or seen.get(player) == identity:
                continue
            seen[player] = identity
            icon = art_path(meta('mpris:artUrl'))
            # Escape player-provided text because Dunst enables Pango markup.
            run('dunstify', '-a', 'Rice Music', '-u', 'normal', '-t', '6000',
                '-h', 'string:x-dunst-stack-tag:rice-now-playing', '-i', icon,
                '--', html.escape(title[:180]),
                html.escape((artist or 'Now playing')[:180]))
            break
        seen = {p: v for p, v in seen.items() if p in players}
        time.sleep(2)
except KeyboardInterrupt:
    pass
