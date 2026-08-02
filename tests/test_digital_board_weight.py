"""Unit tests for digital weighing board Modbus framing/parsing."""

from app.services.digital_board_weight import (
    WEIGHT_BLOCK_COUNT,
    WEIGHT_BLOCK_REGISTER,
    build_read_holding_request,
    decode_weight_payload,
    round_weight_g,
)


def test_weight_poll_frame_matches_field_capture() -> None:
    # Field / vendor tool: 01 03 00 01 00 05 (+ CRC)
    frame = build_read_holding_request(0x01, WEIGHT_BLOCK_REGISTER, WEIGHT_BLOCK_COUNT)
    assert frame[:6] == bytes.fromhex("01 03 00 01 00 05")
    assert len(frame) == 8


def test_decode_captured_942_37_frame() -> None:
    # … 01 70 1D … → 942.37 → rounded to 0.05g → 942.35
    data = bytes.fromhex("00 D7 00 5B 8A 01 70 1D 8A 01")
    reading = decode_weight_payload(data)
    assert reading.raw == 94237
    assert reading.value == 942.35


def test_decode_captured_942_39_frame() -> None:
    data = bytes.fromhex("00 D7 00 5B 8A 01 70 1F 8A 01")
    reading = decode_weight_payload(data)
    assert reading.raw == 94239
    assert reading.value == 942.4


def test_decode_captured_942_46_frame() -> None:
    data = bytes.fromhex("00 D7 00 5B 8A 01 70 26 8A 01")
    reading = decode_weight_payload(data)
    assert reading.raw == 94246
    assert reading.value == 942.45


def test_round_weight_to_0_05g() -> None:
    assert round_weight_g(942.46) == 942.45
    assert round_weight_g(942.39) == 942.4
    assert round_weight_g(942.375) == 942.4
    assert round_weight_g(942.325) == 942.35
