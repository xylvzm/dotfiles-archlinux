#!/usr/bin/env python3
import subprocess,json

def query(*args):
    try:
        r=subprocess.run(['playerctl',*args],capture_output=True,text=True,timeout=2)
        return r.stdout.strip() if r.returncode==0 else ''
    except (FileNotFoundError,subprocess.TimeoutExpired):return ''
status=query('status')
title=query('metadata','title')
artist=query('metadata','artist')
icon='' if status=='Playing' else '' if status=='Paused' else ''
label=title or 'No media playing'
print(json.dumps({'text':f'{icon} {label[:16]}','tooltip':f'{artist} — {title}' if artist and title else label,'class':status.lower() if status else 'idle'},ensure_ascii=False))
