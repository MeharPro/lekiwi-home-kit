# LEKIWI Home Kit

This repo is a plug-and-play handoff package for the SO-100 leader arm and LEKIWI follower base.

It does not change your original local code. Instead, it ships:

- a clean vendored snapshot of the current `lerobot` source under `vendor/lerobot`
- bundled leader calibration files under `assets/calibration/`
- Mac setup and launcher scripts under `mac/`
- Windows setup and launcher scripts under `windows/`
- standalone wrapper scripts under `scripts/`

The repo now carries a full vendored copy of `lerobot`, not just a minimal subset.

## Mac Quick Start

1. Download or clone this repo on the Mac laptop.
2. Plug in the SO-100 leader arm by USB.
3. Make sure the Mac can reach the Pi over the same network. The default robot IP in the launcher is `10.42.0.1`.
4. Run:

```bash
chmod +x ./mac/*.sh
./mac/Setup-Mac.sh
./mac/Start-Manual-Control.sh
```

If auto-detection picks the wrong serial port:

```bash
export LEKIWI_LEADER_PORT=/dev/tty.usbmodem5AE60840411
./mac/Start-Manual-Control.sh
```

## Windows Quick Start

1. Download this repo on the Windows laptop.
2. Plug in the SO-100 leader arm by USB.
3. Make sure the Windows laptop can reach the Pi over the same network. The default robot IP in the launcher is `10.42.0.1`.
4. Double-click `windows/Setup-Windows.bat`.
5. Double-click `windows/Start-Manual-Control.bat`.

`Setup-Windows.bat` now installs the bundled SO-100 leader calibration into the Windows Hugging Face cache automatically, so the default `leader` teleoperator id matches your existing setup.

If auto-detection picks the wrong serial port, double-click `windows/List-Leader-Ports.bat` and then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\Start-Manual-Control.ps1 -LeaderPort COM5
```

If the leader arm needs calibration, double-click `windows/Calibrate-Leader.bat`.

Important for calibration: keep `wrist_roll` centered and untwisted before pressing Enter at the midpoint prompt.

## Windows Commands

Setup:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\Setup-Windows.ps1
```

Start manual control:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\Start-Manual-Control.ps1
```

Start manual control with an explicit IP and COM port:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\Start-Manual-Control.ps1 -RobotIp 10.42.0.1 -LeaderPort COM5
```

List available serial ports:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\List-Leader-Ports.ps1
```

Calibrate the leader:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\Calibrate-Leader.ps1
```

## Mac Commands

Setup:

```bash
chmod +x ./mac/*.sh
./mac/Setup-Mac.sh
```

Start manual control:

```bash
./mac/Start-Manual-Control.sh
```

Start manual control with an explicit IP and serial port:

```bash
LEKIWI_REMOTE_IP=10.42.0.1 LEKIWI_LEADER_PORT=/dev/tty.usbmodem5AE60840411 ./mac/Start-Manual-Control.sh
```

Calibrate the leader:

```bash
./mac/Calibrate-Leader.sh
```

## OPTIMIZED MANUAL CONTROL

PI:

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd ~/lerobot

python -m lerobot.robots.lekiwi.lekiwi_host \
  --host.connection_time_s=3600 \
  --robot.id=follow-mobile \
  --robot.cameras='{}' \
  --robot.base_max_raw_velocity=6000 \
  --robot.base_wheel_torque_limit=700
```

mac:

```bash
source /Users/meharkhanna/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd /Users/meharkhanna/lerobot

python examples/lekiwi/teleoperate.py
```

## STOP ALL COMMANDS

PI:

```bash
export LEKIWI_ROBOT_PORT=/dev/ttyACM0

if command -v lsof >/dev/null 2>&1; then
  pids="$(lsof -tiTCP:5555 -sTCP:LISTEN || true) $(lsof -tiTCP:5556 -sTCP:LISTEN || true)"
  if [ -n "$pids" ]; then
    kill $pids >/dev/null 2>&1 || true
    sleep 1
    kill -9 $pids >/dev/null 2>&1 || true
  fi
fi

pkill -f 'python -m lerobot\.robots\.lekiwi\.lekiwi_host' >/dev/null 2>&1 || true
pkill -f 'scripts/lekiwi_.*host\.py' >/dev/null 2>&1 || true
sleep 1

source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate lerobot
cd "$HOME/lerobot"

python - <<'PY'
import os
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

motors = {
    f"m{i}": Motor(i, "sts3215", MotorNormMode.RANGE_M100_100)
    for i in range(1, 10)
}

bus = FeetechMotorsBus(
    port=os.environ["LEKIWI_ROBOT_PORT"],
    motors=motors,
)

bus.connect(handshake=False)
disabled = []
failed = []

for motor_name in motors:
    try:
        bus.disable_torque(motor_name)
        disabled.append(motor_name)
    except Exception as exc:
        failed.append((motor_name, str(exc)))

bus.disconnect(disable_torque=False)

print(f"Disabled torque on: {', '.join(disabled) if disabled else 'none'}")
if failed:
    print("Failed to disable torque on:")
    for motor_name, error in failed:
        print(f"  - {motor_name}: {error}")
PY
```

## CALIBRATE!!!

PI:

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd ~/lerobot

lerobot-calibrate \
  --robot.type=lekiwi \
  --robot.id=follow-mobile \
  --robot.cameras='{}'
```

MAC:

```bash
source /Users/meharkhanna/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd /Users/meharkhanna/lerobot

lerobot-calibrate \
  --teleop.type=so100_leader \
  --teleop.port=/dev/tty.usbmodem5AE60840411 \
  --teleop.id=leader
```

## Notes

- The Windows launcher starts in the fast LEKIWI speed tier automatically.
- The Mac and Windows launchers both use `Q/E` for rotation, `R/F` for speed changes, and `P` to quit.
- The Windows launcher keeps robot cameras disabled by default, matching your manual Pi host usage.
- The Mac launcher uses the same wrapper and bundled calibration install flow as the Windows package.
- The package includes your cached SO-100 leader calibration files for `leader` and `lead`.
- The default launcher uses teleoperator id `leader`, so it will use `assets/calibration/teleoperators/so_leader/leader.json` after setup copies it into the cache.
- If the Pi is not reachable at `10.42.0.1`, pass the correct address with `-RobotIp`.
- Vendored `lerobot` code remains under its original Apache 2.0 license in `vendor/lerobot`.
