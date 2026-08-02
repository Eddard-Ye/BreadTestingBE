"""Unit tests for digital weighing board Modbus framing/parsing."""

import struct

from app.services.digital_board_weight import (
    WEIGHT_BLOCK_COUNT,
    WEIGHT_BLOCK_REGISTER,
    build_read_holding_request,
    parse_be_s32,
    scale_weight,
)


def test_weight_poll_frame_matches_manual() -> None:
    # Manual recommended: 01 03 00 00 00 04 (+ CRC)
    frame = build_read_holding_request(0x01, WEIGHT_BLOCK_REGISTER, WEIGHT_BLOCK_COUNT)
    assert frame[:6] == bytes.fromhex("01 03 00 00 00 04")
    assert len(frame) == 8


def test_parse_be_s32_and_scale_like_manual_example() -> None:
    # Manual: display 15.32 with precision 2 → integer 1532
    raw = parse_be_s32(struct.pack(">i", 1532))
    assert raw == 1532
    assert scale_weight(raw, 2) == 15.32


def test_parse_942_20_display() -> None:
    # Vendor UI 942.20 with precision 2 → integer 94220
    raw = parse_be_s32(struct.pack(">i", 94220))
    assert raw == 94220
    assert scale_weight(raw, 2) == 942.20
