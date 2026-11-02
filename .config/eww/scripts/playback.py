#!/usr/bin/env python3
import subprocess,sys
if len(sys.argv)!=2:raise SystemExit(1)
mode=sys.argv[1]
if mode not in ('shuffle','repeat'):raise SystemExit(1)
key='shuffle' if mode=='shuffle' else 'loop'
r=subprocess.run(['playerctl',key],capture_output=True,text=True)
if r.returncode:raise SystemExit('No compatible player')
value=r.stdout.strip().lower()
new=('Off' if value=='on' else 'On') if mode=='shuffle' else ('None' if value=='track' else 'Track')
raise SystemExit(subprocess.run(['playerctl',key,new]).returncode)
