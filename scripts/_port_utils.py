from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortInfo:
    device: str
    description: str
    manufacturer: str
    product: str
    hwid: str


def list_serial_ports() -> list[PortInfo]:
    from serial.tools import list_ports

    ports: list[PortInfo] = []
    for port in list_ports.comports():
        ports.append(
            PortInfo(
                device=port.device or "",
                description=port.description or "",
                manufacturer=port.manufacturer or "",
                product=port.product or "",
                hwid=port.hwid or "",
            )
        )
    return ports


def _score_port(port: PortInfo) -> int:
    haystack = " ".join(
        [
            port.device,
            port.description,
            port.manufacturer,
            port.product,
            port.hwid,
        ]
    ).lower()
    score = 0
    for token, weight in (
        ("wch", 6),
        ("ch340", 6),
        ("cp210", 6),
        ("silicon labs", 5),
        ("usb serial", 5),
        ("serial", 3),
        ("usb", 2),
        ("arduino", 2),
        ("stm", 2),
        ("modem", 2),
        ("com", 1),
    ):
        if token in haystack:
            score += weight
    return score


def detect_leader_port(requested_port: str | None) -> str:
    if requested_port and requested_port.lower() != "auto":
        return requested_port

    ports = list_serial_ports()
    if not ports:
        raise RuntimeError("No serial ports were found. Plug in the SO-100 leader arm and try again.")

    if len(ports) == 1:
        return ports[0].device

    ranked = sorted(ports, key=_score_port, reverse=True)
    if _score_port(ranked[0]) > _score_port(ranked[1]):
        return ranked[0].device

    print("Multiple serial ports were found. Pick the leader arm port:")
    for index, port in enumerate(ranked, start=1):
        label = " | ".join(part for part in [port.description, port.manufacturer, port.product] if part)
        print(f"  {index}. {port.device} - {label or port.hwid or 'unknown device'}")

    while True:
        choice = input("Enter a number: ").strip()
        if choice.isdigit():
            selected = int(choice)
            if 1 <= selected <= len(ranked):
                return ranked[selected - 1].device
        print("Invalid selection. Enter one of the listed numbers.")
