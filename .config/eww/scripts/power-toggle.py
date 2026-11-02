#!/usr/bin/env python3
import json,subprocess,sys
try:
    monitors=json.loads(subprocess.check_output(['hyprctl','monitors','-j'],text=True,timeout=3))
    selected=next((m for m in monitors if m.get('focused')),monitors[0])
    screen=selected.get('model') or selected['name']
    subprocess.run(['eww','daemon'],stdout=subprocess.DEVNULL,timeout=5)
    # Reset the selection every time, so old confirmations cannot linger.
    subprocess.run(['eww','update','power_choice='],check=True)
    subprocess.run(['eww','open','--toggle','--screen',screen,'power'],check=True)
except (subprocess.SubprocessError,ValueError,IndexError,FileNotFoundError) as e:
    print(f'Power popup failed: {e}',file=sys.stderr);raise SystemExit(1)
