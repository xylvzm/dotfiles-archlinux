#!/usr/bin/env python3
"""Local Eww audio controls. No shell evaluation or network requests."""
import json
import math
import os
from pathlib import Path
import subprocess
import sys

BASE = Path.home()/'.config/eww'
NOTICE = Path.home()/'.cache/eww-volume/message.json'

def run(args, timeout=4):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                          env={**os.environ, 'LC_ALL':'C'})

def checked(args):
    p=run(args)
    if p.returncode:
        raise ValueError('Audio command failed. Check that PipeWire is running.')
    return p.stdout.strip()

def eww(*args):
    return run(['eww','-c',str(BASE),*args])

def note(text):
    import time
    NOTICE.parent.mkdir(parents=True, exist_ok=True)
    temp=NOTICE.with_suffix('.tmp')
    temp.write_text(json.dumps({'text':text,'time':time.time()}))
    temp.replace(NOTICE)

def message():
    import time
    try:
        item=json.loads(NOTICE.read_text())
        return item['text'] if time.time()-item['time']<15 else ''
    except (OSError,ValueError,KeyError):
        return ''

def devices(kind):
    rows=json.loads(checked(['pactl','--format=json','list',kind]))
    default=checked(['pactl','get-default-sink' if kind=='sinks' else 'get-default-source'])
    result=[]
    for item in rows:
        if kind=='sources' and (item.get('monitor_of_sink_name') or str(item.get('name','')).endswith('.monitor')):
            continue
        values=[v.get('value_percent','0%') for v in item.get('volume',{}).values()]
        volumes=[float(v.rstrip('%')) for v in values]
        percent=round(sum(volumes)/len(volumes)) if volumes else 0
        result.append({'id':int(item['index']), 'name':item['name'],
                       'label':item.get('description') or item['name'],
                       'selected':item['name']==default,'volume':percent,
                       'slider':max(0,min(100,percent)), 'muted':bool(item.get('mute',False))})
    return result

def state():
    empty={'label':'Unavailable','volume':0,'slider':0,'muted':False,'available':False}
    try:
        sinks=devices('sinks'); sources=devices('sources')
        output=next((dict(v,available=True) for v in sinks if v['selected']),dict(empty))
        mic=next((dict(v,available=True) for v in sources if v['selected']),dict(empty))
        return {'output':output,'mic':mic,'outputs':sinks,'message':message()}
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError):
        return {'output':empty,'mic':dict(empty),'outputs':[],
                'message':'Cannot read audio devices. Check PipeWire / pipewire-pulse.'}

def close():
    eww('close','volume-panel'); eww('update','volume_open=false')

def toggle():
    eww('daemon')
    active=eww('active-windows').stdout
    if any(line.split(':',1)[0].strip()=='volume-panel' for line in active.splitlines()):
        close(); return
    monitors=json.loads(checked(['hyprctl','-j','monitors']))
    focused=next((m for m in monitors if m.get('focused')),monitors[0] if monitors else {})
    eww('update','volume_open=true')
    args=['open']
    if focused.get('model'): args+=['--screen',focused['model']]
    p=eww(*args,'volume-panel')
    if p.returncode:
        eww('update','volume_open=false')
        raise ValueError(p.stderr.strip() or 'Eww could not open the volume panel.')

def action(args):
    cmd=args[0]
    if cmd=='toggle': toggle(); return
    if cmd=='close': close(); return
    if cmd in ('output-volume','mic-volume'):
        value=float(args[1])
        if not math.isfinite(value) or not 0<=value<=100:
            raise ValueError('Volume must be between 0 and 100 percent.')
        target='@DEFAULT_AUDIO_SINK@' if cmd=='output-volume' else '@DEFAULT_AUDIO_SOURCE@'
        checked(['wpctl','set-volume','-l','1',target,f'{value:.0f}%'])
    elif cmd in ('output-mute','mic-mute'):
        target='@DEFAULT_AUDIO_SINK@' if cmd=='output-mute' else '@DEFAULT_AUDIO_SOURCE@'
        checked(['wpctl','set-mute',target,'toggle'])
    elif cmd=='select-output':
        index=int(args[1])
        sink=next((s for s in devices('sinks') if s['id']==index),None)
        if sink is None: raise ValueError('That output disconnected. Choose another device.')
        checked(['pactl','set-default-sink',sink['name']])
        streams=json.loads(checked(['pactl','--format=json','list','sink-inputs']))
        failed=0
        for stream in streams:
            if run(['pactl','move-sink-input',str(int(stream['index'])),str(index)]).returncode:
                failed+=1
        note('Output changed.' if not failed else 'Default changed; some apps may need playback restarted.')
    else:
        raise ValueError('Unknown audio action.')

if __name__=='__main__':
    try:
        if sys.argv[1:] == ['state']: print(json.dumps(state(),ensure_ascii=False))
        elif len(sys.argv)>1: action(sys.argv[1:])
        else: raise ValueError('Specify state, toggle, close, or an audio action.')
    except (OSError,ValueError,IndexError,KeyError,subprocess.SubprocessError) as exc:
        text=str(exc)
        note(text)
        print(text,file=sys.stderr)
        sys.exit(1)
