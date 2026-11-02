#!/usr/bin/env python3
import json, subprocess, pathlib, sys, signal

def stop(signum, frame):
    raise KeyboardInterrupt

signal.signal(signal.SIGTERM, stop)
cfg=pathlib.Path.home()/'.config/waybar/spectrum.ini'
glyphs='▁▂▃▄▅▆▇█'
print(json.dumps({'text':'▁'*38,'tooltip':'CAVA · waiting for audio'}),flush=True)
try:
    p=subprocess.Popen(['cava','-p',str(cfg)],stdout=subprocess.PIPE,text=True,bufsize=1)
    try:
        for line in p.stdout:
            try:
                values=[int(v) for v in line.strip().split(';') if v.strip()]
            except ValueError:
                continue
            if values:
                print(json.dumps({'text':''.join(glyphs[max(0,min(7,v))] for v in values),'tooltip':'CAVA audio spectrum'}),flush=True)
    finally:
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=2)
            except subprocess.TimeoutExpired:p.kill()
except FileNotFoundError:
    print(json.dumps({'text':'Install cava','tooltip':'sudo pacman -S cava','class':'error'}),flush=True)
except (BrokenPipeError,KeyboardInterrupt):
    sys.exit(0)
