#!/usr/bin/env python3
import json,subprocess,sys
if len(sys.argv)!=2 or sys.argv[1] not in ('music','calendar'):raise SystemExit('Choose music or calendar')
try:
    r=subprocess.run(['hyprctl','monitors','-j'],capture_output=True,text=True,check=True,timeout=3)
    monitors=json.loads(r.stdout)
    name=next((m['model'] for m in monitors if m.get('focused')),monitors[0]['model'])
    # daemon is idempotent: an already-running daemon is left alone.
    subprocess.run(['eww','daemon'],stdout=subprocess.DEVNULL,timeout=5)
    subprocess.run(['eww','open','--toggle','--screen',name,sys.argv[1]],check=True)
except (subprocess.SubprocessError,ValueError,IndexError,FileNotFoundError) as e:
    print(f'Eww popup failed: {e}',file=sys.stderr);raise SystemExit(1)
