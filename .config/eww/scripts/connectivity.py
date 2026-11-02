#!/usr/bin/env python3
"""NetworkManager/BlueZ Eww controls. No passwords stored or passed in argv."""
import base64
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import unicodedata

BASE = Path.home() / '.config/eww'
SCRIPT = BASE / 'scripts/connectivity.py'
CACHE = Path.home() / '.cache/eww-connectivity'
STATUS = CACHE / 'status.json'
MAC = re.compile(r'^[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}$')

def clean(value, limit=100):
    return ''.join(c if not unicodedata.category(c).startswith('C') else ' ' for c in str(value))[:limit]

def run(*args, timeout=5):
    env = dict(os.environ, LC_ALL='C', NO_COLOR='1')
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return subprocess.CompletedProcess(args, 1, '', '')

def fields(line):
    out, current, escaped = [], '', False
    for c in line:
        if escaped:
            current += c; escaped = False
        elif c == '\\':
            escaped = True
        elif c == ':':
            out.append(current); current = ''
        else:
            current += c
    if escaped:
        current += '\\'
    out.append(current)
    return out

def note(message):
    CACHE.mkdir(parents=True, exist_ok=True)
    temp = CACHE / ('status-' + str(os.getpid()) + '.tmp')
    temp.write_text(json.dumps({'message': clean(message, 130), 'time': time.time()}))
    os.replace(temp, STATUS)

def message():
    try:
        data = json.loads(STATUS.read_text())
        return data['message'] if time.time() - data['time'] < 25 else ''
    except (OSError, ValueError, KeyError, TypeError):
        return ''

def wifi_interface():
    response = run('nmcli', '-t', '-f', 'DEVICE,TYPE,STATE', 'device', 'status')
    devices = [fields(line) for line in response.stdout.splitlines()]
    wifi = [v for v in devices if len(v) >= 3 and v[1] == 'wifi']
    wifi.sort(key=lambda v: not v[2].startswith('connected'))
    return wifi[0][0] if wifi else None

def wifi_state():
    info = {'available': False, 'enabled': False, 'status': 'Wi-Fi unavailable', 'networks': []}
    iface = wifi_interface()
    if not iface:
        return info
    info['available'] = True
    response = run('nmcli', 'radio', 'wifi')
    info['enabled'] = response.returncode == 0 and response.stdout.strip() == 'enabled'
    if not info['enabled']:
        info['status'] = 'Wi-Fi off / blocked'
        return info
    response = run('nmcli', '-t', '-e', 'yes', '-f', 'IN-USE,SSID,SIGNAL,SECURITY',
                   'device', 'wifi', 'list', 'ifname', iface, '--rescan', 'no')
    if response.returncode:
        info['status'] = 'Could not read Wi-Fi networks'
        return info
    by_name = {}
    connected = False
    for line in response.stdout.splitlines():
        parts = fields(line)
        if len(parts) != 4 or not parts[1]:
            continue
        active, ssid, signal, security = parts
        try:
            strength = max(0, min(100, int(signal)))
        except ValueError:
            continue
        is_connected = active == '*'
        connected |= is_connected
        item = {'id': base64.urlsafe_b64encode(ssid.encode()).decode(),
                'name': clean(ssid), 'signal': strength, 'connected': is_connected,
                'detail': ('Connected · ' if is_connected else '') + (clean(security) if security and security != '--' else 'Open network')}
        previous = by_name.get(ssid)
        if previous is None or (is_connected, strength) > (previous['connected'], previous['signal']):
            by_name[ssid] = item
    info['networks'] = sorted(by_name.values(), key=lambda v: (not v['connected'], -v['signal'], v['name']))[:18]
    info['status'] = 'Wi-Fi connected' if connected else ('Choose a network' if info['networks'] else 'No networks · try Scan')
    return info

def bt_list(kind=None):
    args = ['bluetoothctl', 'devices'] + ([kind] if kind else [])
    response = run(*args)
    devices = {}
    for line in response.stdout.splitlines():
        match = re.match(r'^Device ([0-9A-Fa-f:]{17}) (.+)$', line.strip())
        if match and MAC.fullmatch(match[1]):
            devices[match[1].upper()] = clean(match[2])
    return devices

def bt_state():
    info = {'available': False, 'enabled': False, 'status': 'Install bluez-utils', 'devices': []}
    if not shutil.which('bluetoothctl'):
        return info
    response = run('bluetoothctl', 'show')
    if response.returncode or 'Controller ' not in response.stdout:
        info['status'] = 'No Bluetooth controller'
        return info
    info['available'] = True
    info['enabled'] = bool(re.search(r'^\s*Powered:\s+yes\s*$', response.stdout, re.M))
    if not info['enabled']:
        info['status'] = 'Bluetooth off / blocked'
        return info
    devices = bt_list()
    paired = bt_list('Paired')
    connected = bt_list('Connected')
    devices.update(paired); devices.update(connected)
    for ident, name in devices.items():
        active, known = ident in connected, ident in paired
        info['devices'].append({'id': ident, 'name': name, 'connected': active,
            'action': 'Disconnect' if active else ('Connect' if known else 'Pair'),
            'detail': 'Connected' if active else ('Paired device' if known else 'Nearby / discovered device')})
    info['devices'].sort(key=lambda d: (not d['connected'], d['action'] == 'Pair', d['name']))
    info['devices'] = info['devices'][:30]
    info['status'] = 'Bluetooth on' if info['devices'] else 'No devices · try Scan'
    return info

def eww(*args):
    return run('eww', '-c', str(BASE), *args)

def close():
    eww('close', 'connectivity')
    eww('update', 'radio_open=false')

def toggle(tab):
    if tab not in ('wifi', 'bluetooth'):
        return
    eww('daemon')
    active = eww('active-windows').stdout
    opened = any(line.split(':', 1)[0].strip() == 'connectivity' for line in active.splitlines())
    current = eww('get', 'radio_tab').stdout.strip().strip('"')
    if opened and current == tab:
        close(); return
    eww('update', 'radio_tab=' + tab, 'radio_open=true')
    if opened:
        return
    monitor = '0'
    try:
        monitors = json.loads(run('hyprctl', '-j', 'monitors').stdout)
        focused = next((m for m in monitors if m.get('focused')), monitors[0])
        monitor = focused.get('model') or str(focused['id'])
    except (ValueError, TypeError, KeyError, IndexError):
        pass
    result = eww('open', '--screen', monitor, 'connectivity')
    if result.returncode:
        eww('update', 'radio_open=false')
        print(result.stderr or result.stdout, file=sys.stderr)

def terminal(action, *args):
    close()
    if not shutil.which('kitty'):
        note('Kitty is required for private connection prompts.'); return
    subprocess.Popen(['kitty', '--title', 'Connection setup', '-e', 'python3',
                      str(SCRIPT), action, *args, '--terminal'], start_new_session=True)

def interactive(command, success):
    # nmcli/bluetoothctl read secrets or confirmations directly from the terminal.
    result = subprocess.run(command, env=dict(os.environ, LC_ALL='C'))
    note(success if result.returncode == 0 else 'Connection setup did not complete.')
    if result.returncode:
        input('\nSetup did not complete. Press Enter to close…')
    else:
        time.sleep(0.5)

def action(name, args):
    if name in ('wifi-on', 'wifi-off'):
        result = run('nmcli', 'radio', 'wifi', 'on' if name.endswith('-on') else 'off')
        note('Wi-Fi setting updated.' if not result.returncode else 'Wi-Fi toggle failed; check rfkill / permissions.')
    elif name == 'wifi-scan':
        iface = wifi_interface()
        if iface:
            result = run('nmcli', 'device', 'wifi', 'rescan', 'ifname', iface, timeout=15)
            note('Wi-Fi scan requested.' if not result.returncode else 'Wi-Fi scan failed; radio may be off.')
    elif name == 'wifi-disconnect':
        iface = wifi_interface()
        if iface:
            result = run('nmcli', 'device', 'disconnect', iface, timeout=15)
            note('Wi-Fi disconnected.' if not result.returncode else 'Could not disconnect Wi-Fi.')
    elif name == 'wifi-connect' and args:
        encoded = args[0]
        if not re.fullmatch(r'[A-Za-z0-9_=-]{1,256}', encoded):
            return
        try:
            ssid = base64.b64decode(encoded, altchars=b'-_', validate=True).decode('utf-8')
        except (ValueError, UnicodeError):
            return
        if not ssid or '\x00' in ssid or '\n' in ssid or len(ssid.encode()) > 32:
            return
        if '--terminal' not in args:
            terminal(name, encoded); return
        iface = wifi_interface()
        if iface:
            interactive(['nmcli', '--ask', 'device', 'wifi', 'connect', ssid, 'ifname', iface], 'Wi-Fi connection updated.')
    elif name in ('bt-on', 'bt-off'):
        result = run('bluetoothctl', 'power', 'on' if name.endswith('-on') else 'off')
        note('Bluetooth setting requested.' if not result.returncode else 'Bluetooth toggle failed.')
    elif name == 'bt-scan':
        note('Scanning for Bluetooth devices…')
        result = run('bluetoothctl', '--timeout', '8', 'scan', 'on', timeout=12)
        run('bluetoothctl', 'scan', 'off')
        note('Bluetooth scan finished.' if not result.returncode else 'Bluetooth scan ended; check the device list.')
    elif name == 'bt-device' and args and MAC.fullmatch(args[0]):
        ident = args[0].upper()
        detail = run('bluetoothctl', 'info', ident).stdout
        if re.search(r'^\s*Connected:\s+yes\s*$', detail, re.M):
            result = run('bluetoothctl', 'disconnect', ident, timeout=20)
            note('Bluetooth disconnect requested.' if not result.returncode else 'Bluetooth disconnect failed.')
        elif re.search(r'^\s*Paired:\s+yes\s*$', detail, re.M):
            result = run('bluetoothctl', 'connect', ident, timeout=25)
            note('Bluetooth connection requested.' if not result.returncode else 'Bluetooth connection failed.')
        elif '--terminal' not in args:
            terminal(name, ident)
        else:
            print('Confirm pairing only if the device and any displayed code match.')
            result = subprocess.run(['bluetoothctl', '--timeout', '60', '--agent', 'KeyboardDisplay', 'pair', ident])
            if result.returncode == 0:
                interactive(['bluetoothctl', '--timeout', '20', 'connect', ident], 'Bluetooth pairing/connection requested.')
            else:
                note('Bluetooth pairing did not complete.')
                input('\nPress Enter to close…')
    elif name == 'advanced':
        close()
        if shutil.which('nmtui'):
            subprocess.Popen(['kitty', '--title', 'Network settings', '-e', 'nmtui'], start_new_session=True)
        else:
            note('nmtui is unavailable; install networkmanager for advanced settings.')

def main():
    if len(sys.argv) < 2:
        return
    name, args = sys.argv[1], sys.argv[2:]
    if name == 'state':
        print(json.dumps({'message': message(), 'wifi': wifi_state(), 'bt': bt_state()}, ensure_ascii=True))
    elif name == 'toggle':
        toggle(args[0] if args else 'wifi')
    elif name == 'close':
        close()
    else:
        action(name, args)

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, EOFError, KeyboardInterrupt):
        if len(sys.argv) > 1 and sys.argv[1] != 'state':
            note('Connectivity action interrupted or unavailable.')
