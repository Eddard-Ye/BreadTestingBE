# -*- coding: utf-8 -*-
"""Read net weight and zero a digital weighing board via Modbus RTU.

Aligned with vendor tool「数字传感器通信软件」working capture:
- TX: 01 03 00 01 00 05 …  (read 5 holding regs from protocol address 0x0001)
- Default serial: 19200 8N1, slave 0x01
- Scaled register value is exposed as grams for the app (same numeric display
  as the vendor tool; if the board is truly calibrated in kg, readings will
  need an extra ×1000).

Parsed from the 5-register block (10 bytes):
- regs 0x0001/0x0002: signed 32-bit weight, high word first
- reg  0x0003: decimal places 0-3
- reg  0x0004: status bits
- reg  0x0005: reserved / unused by us

Zero command (unchanged from module doc): write 1 to holding reg 0x0004.
"""

from __future__ import annotations

import struct
import sys
import time
from dataclasses import dataclass
from typing import Any

DEFAULT_PORT = "COM6"
DEFAULT_BAUDRATE = 19200
DEFAULT_SLAVE_ID = 0x01
# Vendor tool poll: start=0x0001, count=5
WEIGHT_BLOCK_REGISTER = 0x0001
WEIGHT_BLOCK_COUNT = 5
ZERO_COMMAND_REGISTER = 0x0004
ZERO_COMMAND_VALUE = 0x0001
READ_TIMEOUT_S = 2.0
DEFAULT_RETRIES = 2
POST_OPEN_DELAY_S = 0.1
POST_COMMAND_SETTLE_S = 0.35
MIN_COMMAND_GAP_S = 0.05


@dataclass(frozen=True)
class WeightReading:
    raw: int
    decimal_places: int
    value: float
    status: int


def modbus_char_time_s(baudrate: int) -> float:
    return 11.0 / baudrate


def modbus_inter_byte_timeout_s(baudrate: int) -> float:
    return modbus_char_time_s(baudrate) * 3.5


def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def build_read_holding_request(slave_id: int, register: int, count: int) -> bytes:
    payload = struct.pack(">BBHH", slave_id, 0x03, register, count)
    return payload + struct.pack("<H", crc16_modbus(payload))


def build_write_single_request(slave_id: int, register: int, value: int) -> bytes:
    payload = struct.pack(">BBHH", slave_id, 0x06, register, value & 0xFFFF)
    return payload + struct.pack("<H", crc16_modbus(payload))


def _verify_crc(frame: bytes) -> None:
    payload, recv_crc = frame[:-2], struct.unpack("<H", frame[-2:])[0]
    if crc16_modbus(payload) != recv_crc:
        raise ValueError(f"CRC check failed on frame: {frame.hex(' ')}")


def parse_holding_read_response(response: bytes, slave_id: int) -> bytes:
    if len(response) < 5:
        raise ValueError(f"response too short: {len(response)} bytes, data={response.hex(' ')}")

    resp_slave, func_code = response[0], response[1]
    if resp_slave != slave_id:
        raise ValueError(
            f"unexpected slave id: 0x{resp_slave:02X}, expected 0x{slave_id:02X}"
        )

    if func_code & 0x80:
        frame = response[:5]
        _verify_crc(frame)
        raise RuntimeError(f"modbus exception code: 0x{frame[2]:02X}")

    if func_code != 0x03:
        raise ValueError(f"unexpected function code: 0x{func_code:02X}")

    byte_count = response[2]
    expected_len = 3 + byte_count + 2
    if len(response) < expected_len:
        raise ValueError(
            f"incomplete response: got {len(response)} bytes, need {expected_len}"
        )

    frame = response[:expected_len]
    _verify_crc(frame)
    return frame[3:-2]


def parse_write_single_response(response: bytes, slave_id: int, register: int, value: int) -> None:
    if len(response) < 8:
        raise ValueError(f"response too short: {len(response)} bytes")

    resp_slave, func_code = response[0], response[1]
    if resp_slave != slave_id:
        raise ValueError(
            f"unexpected slave id: 0x{resp_slave:02X}, expected 0x{slave_id:02X}"
        )

    if func_code == 0x86:
        frame = response[:5]
        _verify_crc(frame)
        raise RuntimeError(f"modbus exception code: 0x{frame[2]:02X}")

    if func_code != 0x06:
        raise ValueError(f"unexpected function code: 0x{func_code:02X}")

    frame = response[:8]
    _verify_crc(frame)
    resp_reg, resp_value = struct.unpack(">HH", frame[2:6])
    if resp_reg != register or resp_value != (value & 0xFFFF):
        raise ValueError(
            f"unexpected write ack: reg=0x{resp_reg:04X} value=0x{resp_value:04X}"
        )


def parse_be_s32(data: bytes) -> int:
    """Big-endian signed 32-bit (high register word first)."""
    if len(data) < 4:
        raise ValueError(f"expected 4 bytes, got {len(data)}")
    return struct.unpack(">i", data[:4])[0]


def parse_u16(data: bytes) -> int:
    if len(data) < 2:
        raise ValueError(f"expected 2 bytes, got {len(data)}")
    return struct.unpack(">H", data[:2])[0]


def scale_weight(raw: int, decimal_places: int) -> float:
    """Scale raw integer by decimal places → device display value."""
    places = max(0, min(3, int(decimal_places)))
    if places <= 0:
        return float(raw)
    return raw / float(10**places)


def read_modbus_frame(
    ser: Any,
    slave_id: int,
    timeout: float,
    function: int = 0x03,
) -> bytes:
    deadline = time.monotonic() + timeout
    buffer = bytearray()
    exception_func = function | 0x80
    fixed_response_len = 8 if function in (0x06, 0x10) else None

    while time.monotonic() < deadline:
        chunk = ser.read(ser.in_waiting or 1)
        if not chunk:
            continue

        buffer.extend(chunk)

        for start in range(max(0, len(buffer) - 64), len(buffer) - 1):
            if buffer[start] != slave_id:
                continue

            func_code = buffer[start + 1]
            if func_code == exception_func:
                end = start + 5
                if len(buffer) >= end:
                    return bytes(buffer[start:end])
            elif func_code == function:
                if fixed_response_len is not None:
                    end = start + fixed_response_len
                    if len(buffer) >= end:
                        return bytes(buffer[start:end])
                    continue

                if len(buffer) < start + 3:
                    continue
                expected_len = 3 + buffer[start + 2] + 2
                end = start + expected_len
                if len(buffer) >= end:
                    return bytes(buffer[start:end])

    raise TimeoutError(
        f"no complete Modbus response within {timeout:.1f}s; "
        f"received={bytes(buffer).hex(' ') or '(empty)'}"
    )


class DigitalBoardWeightTransmitter:
    """Digital weighing board: read weight (g) and zero over Modbus RTU."""

    def __init__(
        self,
        port: str = DEFAULT_PORT,
        baudrate: int = DEFAULT_BAUDRATE,
        slave_id: int = DEFAULT_SLAVE_ID,
        timeout: float = READ_TIMEOUT_S,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.timeout = timeout
        self.retries = max(0, retries)
        self._ser: Any = None
        self._last_command_at = 0.0

    def __enter__(self) -> "DigitalBoardWeightTransmitter":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def open(self) -> None:
        if self._ser and self._ser.is_open:
            return

        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("pyserial is required: pip install pyserial") from exc

        self._ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
            inter_byte_timeout=modbus_inter_byte_timeout_s(self.baudrate),
            write_timeout=self.timeout,
            rtscts=False,
            dsrdtr=False,
        )
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()
        time.sleep(POST_OPEN_DELAY_S)

    def close(self) -> None:
        if self._ser and self._ser.is_open:
            self._ser.close()
        self._ser = None

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_command_at
        if elapsed < MIN_COMMAND_GAP_S:
            time.sleep(MIN_COMMAND_GAP_S - elapsed)

    def _read_registers(self, register: int, count: int, debug: bool = False) -> bytes:
        if not self._ser or not self._ser.is_open:
            raise RuntimeError("serial port is not open")

        request = build_read_holding_request(self.slave_id, register, count)
        last_error: Optional[Exception] = None

        for attempt in range(self.retries + 1):
            try:
                self._throttle()
                self._ser.reset_input_buffer()
                self._ser.write(request)
                self._ser.flush()
                self._last_command_at = time.monotonic()

                response = read_modbus_frame(self._ser, self.slave_id, self.timeout, 0x03)
                if debug:
                    print(f"TX: {request.hex(' ')}", file=sys.stderr)
                    print(f"RX: {response.hex(' ')}", file=sys.stderr)

                return parse_holding_read_response(response, self.slave_id)
            except (TimeoutError, ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(modbus_char_time_s(self.baudrate) * 4)

        assert last_error is not None
        raise last_error

    def _write_register(self, register: int, value: int, debug: bool = False) -> None:
        if not self._ser or not self._ser.is_open:
            raise RuntimeError("serial port is not open")

        request = build_write_single_request(self.slave_id, register, value)
        last_error: Optional[Exception] = None

        for attempt in range(self.retries + 1):
            try:
                self._throttle()
                self._ser.reset_input_buffer()
                self._ser.write(request)
                self._ser.flush()
                self._last_command_at = time.monotonic()

                response = read_modbus_frame(self._ser, self.slave_id, self.timeout, 0x06)
                if debug:
                    print(f"TX: {request.hex(' ')}", file=sys.stderr)
                    print(f"RX: {response.hex(' ')}", file=sys.stderr)

                parse_write_single_response(response, self.slave_id, register, value)
                return
            except (TimeoutError, ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(modbus_char_time_s(self.baudrate) * 4)

        assert last_error is not None
        raise last_error

    def read_net(self, debug: bool = False) -> WeightReading:
        """Read instantaneous weight; ``value`` matches vendor numeric display (app grams)."""
        data = self._read_registers(
            WEIGHT_BLOCK_REGISTER,
            WEIGHT_BLOCK_COUNT,
            debug=debug,
        )
        if len(data) < 8:
            raise ValueError(
                f"expected at least 8 data bytes from weight block, got {len(data)}"
            )

        raw = parse_be_s32(data[0:4])
        decimal_places = parse_u16(data[4:6])
        status = parse_u16(data[6:8])

        return WeightReading(
            raw=raw,
            decimal_places=decimal_places,
            value=scale_weight(raw, decimal_places),
            status=status,
        )

    def read(self, debug: bool = False) -> WeightReading:
        return self.read_net(debug=debug)

    def zero(self, debug: bool = False) -> WeightReading:
        """Clear displayed weight (module zero command)."""
        self._write_register(ZERO_COMMAND_REGISTER, ZERO_COMMAND_VALUE, debug=debug)
        time.sleep(POST_COMMAND_SETTLE_S)
        return self.read_net(debug=debug)
