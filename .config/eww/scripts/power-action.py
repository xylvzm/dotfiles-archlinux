#!/usr/bin/env python3
import subprocess,sys
commands={
    'suspend':['systemctl','suspend'],
    'logout':['hyprctl','dispatch','exit'],
    'reboot':['systemctl','reboot'],
    'shutdown':['systemctl','poweroff'],
}
if len(sys.argv)!=2 or sys.argv[1] not in commands:raise SystemExit('Invalid power action; nothing executed.')
# Invoked only by the popup's explicit Confirm button. No shell/eval.
subprocess.run(['eww','close','power'])
r=subprocess.run(commands[sys.argv[1]])
if r.returncode:print('Action was refused or failed. Check system permissions/session state.',file=sys.stderr)
raise SystemExit(r.returncode)
