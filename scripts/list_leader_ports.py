from __future__ import annotations

from _port_utils import list_serial_ports


def main() -> int:
    ports = list_serial_ports()
    if not ports:
        print("No serial ports found.")
        return 1

    for port in ports:
        label = " | ".join(part for part in [port.description, port.manufacturer, port.product] if part)
        print(f"{port.device}: {label or port.hwid or 'unknown device'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
