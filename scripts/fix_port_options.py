"""Remove /dev/* entries from frontend serial port dropdown (o6)."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-Sb-0d3gP.js"

OLD = (
    'const o6=["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8",'
    '"/dev/ttyUSB0","/dev/ttyUSB1","/dev/ttyS0","/dev/ttyS1"]'
)
NEW = 'const o6=["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8"]'


def main() -> None:
    content = BUNDLE.read_text(encoding="utf-8")
    if NEW in content:
        print("o6 already filtered to COM ports")
        return
    if OLD not in content:
        raise RuntimeError("o6 array not found in bundle")
    BUNDLE.write_text(content.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"Updated o6 in {BUNDLE}")


if __name__ == "__main__":
    main()
