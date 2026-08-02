"""Unit tests for digital weighing board Modbus framing/parsing."""

from app.services.digital_board_weight import (
    WEIGHT_BLOCK_COUNT,
    WEIGHT_BLOCK_REGISTER,
    build_read_holding_request,
    parse_be_s32,
    scale_weight,
)


def test_weight_poll_frame_matches_vendor_tool() -> None:
    # Vendor capture: 01 03 00 01 00 05 (+ CRC)
    frame = build_read_holding_request(0x01, WEIGHT_BLOCK_REGISTER, WEIGHT_BLOCK_COUNT)
    assert frame[:6] == bytes.fromhex("01 03 00 01 00 05")
    assert len(frame) == 8


def test_parse_be_s32_and_scale_like_vendor_display() -> None:
    import struct

    # 942.20 with 2 decimal places → raw 94220
    raw = parse_be_s32(struct.pack(">i", 94220))
    assert raw == 94220
    assert scale_weight(raw, 2) == 942.20
