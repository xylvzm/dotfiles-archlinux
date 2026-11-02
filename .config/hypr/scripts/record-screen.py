import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import time

runtime = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
lock = (runtime / "rice-recorder.lock").open("w")

try:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit(0)

def notify(title, body):
    try:
        subprocess.run(["notify-send", title, body], check=False)
    except FileNotFoundError:
        pass

# Toggle off an existing recorder belonging to this user.
running = subprocess.run(
    ["pgrep", "-u", str(os.getuid()), "-x", "wf-recorder"],
    capture_output=True, text=True,
)
if running.returncode == 0:
    for pid in running.stdout.split():
        try:
            os.kill(int(pid), signal.SIGINT)
        except ProcessLookupError:
            pass
    notify("Recording stopping", "Finishing the video in ~/Videos/Recordings")
    raise SystemExit(0)

monitors = json.loads(subprocess.check_output(
    ["hyprctl", "-j", "monitors"], text=True
))
focused = next((m for m in monitors if m.get("focused")), None)
if focused is None:
    notify("Recording failed", "No focused display found.")
    raise SystemExit(1)

folder = Path.home() / "Videos/Recordings"
folder.mkdir(parents=True, exist_ok=True)
filename = folder / (time.strftime("%Y%m%d_%H%M%S") + f"_{time.time_ns()}.mp4")
logfile = runtime / "rice-recorder.log"

with logfile.open("w") as log:
    process = subprocess.Popen(
        ["wf-recorder", "-o", focused["name"], "-f", str(filename)],
        stdout=log, stderr=log, start_new_session=True,
    )

time.sleep(0.7)
if process.poll() is None:
    notify("Screen recording started", "Super+Shift+F9 to stop. Video only.")
else:
    notify("Recording failed", f"See {logfile}")
