from __future__ import annotations

import argparse
import os
import time

from _bootstrap import bootstrap_vendor
from _port_utils import detect_leader_port

bootstrap_vendor()

from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig  # noqa: E402
from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop, KeyboardTeleopConfig  # noqa: E402
from lerobot.teleoperators.so_leader import SO100Leader, SO100LeaderConfig  # noqa: E402
from lerobot.utils.robot_utils import precise_sleep  # noqa: E402

FPS = 30
BASE_SPEEDS = {
    "slow_xy": 0.15,
    "medium_xy": 0.22,
    "fast_xy": 0.27,
    "slow_theta": 45,
    "medium_theta": 75,
    "fast_theta": 105,
}
SPEED_INDEX = {"slow": 0, "medium": 1, "fast": 2}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launcher for LEKIWI manual control.")
    parser.add_argument("--robot-ip", default=os.environ.get("LEKIWI_REMOTE_IP", "10.42.0.1"))
    parser.add_argument("--robot-id", default=os.environ.get("LEKIWI_ROBOT_ID", "follow-mobile"))
    parser.add_argument("--leader-id", default=os.environ.get("LEKIWI_LEADER_ID", "leader"))
    parser.add_argument("--leader-port", default=os.environ.get("LEKIWI_LEADER_PORT", "auto"))
    parser.add_argument("--fps", type=int, default=FPS)
    parser.add_argument("--start-speed", choices=tuple(SPEED_INDEX), default="fast")
    parser.add_argument("--enable-robot-cameras", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    leader_port = detect_leader_port(args.leader_port)
    robot_config_kwargs = {}
    if not args.enable_robot_cameras:
        robot_config_kwargs["cameras"] = {}

    robot = LeKiwiClient(
        LeKiwiClientConfig(
            remote_ip=args.robot_ip,
            id=args.robot_id,
            slow_xy_speed=BASE_SPEEDS["slow_xy"],
            medium_xy_speed=BASE_SPEEDS["medium_xy"],
            fast_xy_speed=BASE_SPEEDS["fast_xy"],
            slow_theta_speed=BASE_SPEEDS["slow_theta"],
            medium_theta_speed=BASE_SPEEDS["medium_theta"],
            fast_theta_speed=BASE_SPEEDS["fast_theta"],
            default_speed_index=SPEED_INDEX[args.start_speed],
            **robot_config_kwargs,
        )
    )
    leader_arm = SO100Leader(SO100LeaderConfig(port=leader_port, id=args.leader_id))
    keyboard = KeyboardTeleop(KeyboardTeleopConfig(id="windows_keyboard"))

    print(f"Using leader port: {leader_port}")
    print(f"Connecting to LeKiwi host at {args.robot_ip}")

    try:
        robot.connect()
        leader_arm.connect()
        keyboard.connect()

        if not robot.is_connected or not leader_arm.is_connected or not keyboard.is_connected:
            raise RuntimeError("Robot, leader arm, or keyboard listener failed to connect.")

        print("Manual control started.")
        print("W/A/S/D move, Q/E rotate, R/F change speed, P quits.")

        while True:
            t0 = time.perf_counter()
            _ = robot.get_observation()

            arm_action = {f"arm_{key}": value for key, value in leader_arm.get_action().items()}
            keyboard_keys = keyboard.get_action()
            if robot.teleop_keys["quit"] in keyboard_keys:
                print("Quit requested. Stopping teleop.")
                break

            base_action = robot._from_keyboard_to_base_action(keyboard_keys)
            action = {**arm_action, **base_action}
            robot.send_action(action)

            precise_sleep(max(1.0 / args.fps - (time.perf_counter() - t0), 0.0))
    finally:
        if keyboard.is_connected:
            keyboard.disconnect()
        if leader_arm.is_connected:
            leader_arm.disconnect()
        if robot.is_connected:
            robot.disconnect()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
