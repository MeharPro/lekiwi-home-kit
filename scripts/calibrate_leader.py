from __future__ import annotations

import argparse
import os

from _bootstrap import bootstrap_vendor
from _port_utils import detect_leader_port

bootstrap_vendor()

from lerobot.teleoperators.so_leader import SO100Leader, SO100LeaderConfig  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calibrate the SO-100 leader arm on Windows.")
    parser.add_argument("--leader-port", default=os.environ.get("LEKIWI_LEADER_PORT", "auto"))
    parser.add_argument("--leader-id", default=os.environ.get("LEKIWI_LEADER_ID", "leader"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    leader_port = detect_leader_port(args.leader_port)
    leader = SO100Leader(SO100LeaderConfig(port=leader_port, id=args.leader_id))

    print(f"Using leader port: {leader_port}")
    print("Before you press ENTER during calibration, keep wrist_roll centered and untwisted.")

    try:
        leader.connect(calibrate=False)
        leader.calibrate()
    except ValueError as exc:
        message = str(exc)
        if "Magnitude" in message and "2047" in message:
            print()
            print("Calibration failed because wrist_roll was more than about one turn away from center.")
            print("Undo the twist, center wrist_roll, and run calibration again.")
            return 2
        raise
    finally:
        if leader.is_connected:
            leader.disconnect()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
