import json

from fastapi.testclient import TestClient

from tests.test_recipes import _auth_headers


def test_get_current_temperature(client: TestClient) -> None:
    response = client.get("/api/v1/sensors/temperature")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["value"], float)
    assert 0 <= data["value"] <= 100
    assert data["connected"] is True


def test_get_current_weight(client: TestClient) -> None:
    response = client.get("/api/v1/sensors/weight")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["value"], float)
    assert 0 <= data["value"] <= 100
    assert data["connected"] is True


def test_get_sensor_config_creates_defaults(client: TestClient, isolated_sensor_config) -> None:
    response = client.get("/api/v1/sensors/config")
    assert response.status_code == 200
    data = response.json()
    assert data["temperature"]["enableMock"] is True
    assert data["temperature"]["baudRate"] == "9600"
    assert data["weight"]["baudRate"] == "38400"
    assert data["temperature"]["dataBits"] == "8"
    assert data["temperature"]["calibrationDelta"] == 0
    assert data["weight"]["calibrationDelta"] == 0
    assert "height" not in data
    assert isolated_sensor_config.exists()


def test_update_sensor_config_requires_auth(client: TestClient) -> None:
    payload = {
        "temperature": {
            "port": "COM3",
            "baudRate": "9600",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": False,
        },
        "weight": {
            "port": "COM4",
            "baudRate": "38400",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": True,
        },
    }
    response = client.put("/api/v1/sensors/config", json=payload)
    assert response.status_code == 401


def test_update_sensor_config_persists_to_file(client: TestClient, isolated_sensor_config) -> None:
    payload = {
        "temperature": {
            "port": "COM3",
            "baudRate": "9600",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": False,
        },
        "weight": {
            "port": "COM4",
            "baudRate": "38400",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": True,
        },
    }
    headers = _auth_headers(client)
    response = client.put("/api/v1/sensors/config", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["temperature"]["port"] == "COM3"
    assert data["temperature"]["enableMock"] is False
    assert data["weight"]["enableMock"] is True

    saved = json.loads(isolated_sensor_config.read_text(encoding="utf-8"))
    assert saved["temperature"]["enableMock"] is False
    assert "height" not in saved

    reload_response = client.get("/api/v1/sensors/config")
    assert reload_response.json()["temperature"]["port"] == "COM3"


def test_read_temperature_uses_hardware_when_mock_disabled(
    client: TestClient,
    monkeypatch,
) -> None:
    from app.services import sensor_service

    payload = {
        "temperature": {
            "port": "COM3",
            "baudRate": "9600",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": False,
        },
        "weight": {
            "port": "COM4",
            "baudRate": "38400",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": True,
        },
    }
    headers = _auth_headers(client)
    client.put("/api/v1/sensors/config", json=payload, headers=headers)

    monkeypatch.setattr(
        sensor_service,
        "_read_temperature_hw",
        lambda _config: sensor_service.SensorReading(value=36.5, connected=True),
    )

    response = client.get("/api/v1/sensors/temperature")
    assert response.status_code == 200
    assert response.json() == {"value": 36.5, "connected": True}


def test_read_temperature_applies_calibration_delta(
    client: TestClient,
    monkeypatch,
) -> None:
    from app.services import sensor_service

    payload = {
        "temperature": {
            "port": "COM3",
            "baudRate": "9600",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": False,
            "calibrationDelta": -1.5,
        },
        "weight": {
            "port": "COM4",
            "baudRate": "38400",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": True,
        },
    }
    headers = _auth_headers(client)
    client.put("/api/v1/sensors/config", json=payload, headers=headers)

    monkeypatch.setattr(
        sensor_service,
        "_read_temperature_hw",
        lambda _config: sensor_service.SensorReading(value=36.5, connected=True),
    )

    response = client.get("/api/v1/sensors/temperature")
    assert response.status_code == 200
    assert response.json() == {"value": 35.0, "connected": True}


def test_update_sensor_config_persists_temperature_calibration_delta(
    client: TestClient,
    isolated_sensor_config,
) -> None:
    payload = {
        "temperature": {
            "port": "COM3",
            "baudRate": "9600",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": True,
            "calibrationDelta": 2.25,
        },
        "weight": {
            "port": "COM4",
            "baudRate": "38400",
            "dataBits": "8",
            "stopBits": "1",
            "parity": "None",
            "enableMock": True,
        },
    }
    headers = _auth_headers(client)
    response = client.put("/api/v1/sensors/config", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["temperature"]["calibrationDelta"] == 2.25

    saved = json.loads(isolated_sensor_config.read_text(encoding="utf-8"))
    assert saved["temperature"]["calibrationDelta"] == 2.25


def test_get_serial_ports(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.endpoints.sensors.list_serial_ports",
        lambda: ["COM3", "COM4"],
    )
    response = client.get("/api/v1/sensors/ports")
    assert response.status_code == 200
    assert response.json()["ports"] == ["COM3", "COM4"]


def test_list_serial_ports_filters_com_only(monkeypatch) -> None:
    import sys
    from types import ModuleType

    from app.services.sensor_config_service import list_serial_ports

    class FakePort:
        def __init__(self, device: str) -> None:
            self.device = device

    fake_list_ports = ModuleType("serial.tools.list_ports")
    fake_list_ports.comports = lambda: [
        FakePort("COM3"),
        FakePort("/dev/ttyUSB0"),
        FakePort("COM10"),
    ]
    fake_tools = ModuleType("serial.tools")
    fake_tools.list_ports = fake_list_ports
    fake_serial = ModuleType("serial")
    fake_serial.tools = fake_tools

    monkeypatch.setitem(sys.modules, "serial", fake_serial)
    monkeypatch.setitem(sys.modules, "serial.tools", fake_tools)
    monkeypatch.setitem(sys.modules, "serial.tools.list_ports", fake_list_ports)

    assert list_serial_ports() == ["COM3", "COM10"]


def test_sensor_session_reuses_open_connection(monkeypatch) -> None:
    import sys
    from types import ModuleType

    from app.services import sensor_service
    from app.schemas.sensor import SerialPortConfig

    sensor_service.invalidate_sensor_sessions()

    open_calls = 0
    read_calls = 0

    class FakeSensor:
        def __init__(self, **_kwargs) -> None:
            self._ser = type("Ser", (), {"is_open": True})()

        def open(self) -> None:
            nonlocal open_calls
            open_calls += 1

        def close(self) -> None:
            pass

        def read(self) -> float:
            nonlocal read_calls
            read_calls += 1
            return 25.5

    fake_module = ModuleType("app.services.rs485_temperature")
    fake_module.Rs485Thermometer = FakeSensor
    monkeypatch.setitem(sys.modules, "app.services.rs485_temperature", fake_module)
    monkeypatch.setattr(
        "app.services.sensor_service._serial_available",
        lambda: True,
    )

    config = SerialPortConfig(
        port="COM3",
        baud_rate="9600",
        data_bits="8",
        stop_bits="1",
        parity="None",
        enable_mock=False,
    )

    first = sensor_service._read_temperature_hw(config)
    second = sensor_service._read_temperature_hw(config)

    assert first == sensor_service.SensorReading(value=25.5, connected=True)
    assert second == sensor_service.SensorReading(value=25.5, connected=True)
    assert open_calls == 1
    assert read_calls == 2

    sensor_service.invalidate_sensor_sessions()


def test_read_temperature_hw_open_failure_returns_disconnected(monkeypatch) -> None:
    import sys
    from types import ModuleType

    from app.services import sensor_service
    from app.schemas.sensor import SerialPortConfig

    sensor_service.invalidate_sensor_sessions()

    class FakeSensor:
        def __init__(self, **_kwargs) -> None:
            self._ser = None

        def open(self) -> None:
            raise OSError("Port COM3 not found")

        def close(self) -> None:
            pass

        def read(self) -> float:
            raise RuntimeError("should not read")

    fake_module = ModuleType("app.services.rs485_temperature")
    fake_module.Rs485Thermometer = FakeSensor
    monkeypatch.setitem(sys.modules, "app.services.rs485_temperature", fake_module)
    monkeypatch.setattr(
        "app.services.sensor_service._serial_available",
        lambda: True,
    )

    config = SerialPortConfig(
        port="COM3",
        baud_rate="9600",
        data_bits="8",
        stop_bits="1",
        parity="None",
        enable_mock=False,
    )

    reading = sensor_service._read_temperature_hw(config)

    assert reading == sensor_service.SensorReading(value=0.0, connected=False)
    assert "temperature" not in sensor_service._sessions

    sensor_service.invalidate_sensor_sessions()


def test_read_temperature_hw_read_failure_clears_session(monkeypatch) -> None:
    import sys
    from types import ModuleType

    from app.services import sensor_service
    from app.schemas.sensor import SerialPortConfig

    sensor_service.invalidate_sensor_sessions()
    read_calls = 0

    class FakeSensor:
        def __init__(self, **_kwargs) -> None:
            self._ser = type("Ser", (), {"is_open": True})()

        def open(self) -> None:
            pass

        def close(self) -> None:
            self._ser = type("Ser", (), {"is_open": False})()

        def read(self) -> float:
            nonlocal read_calls
            read_calls += 1
            if read_calls == 1:
                raise TimeoutError("no response")
            return 36.2

    fake_module = ModuleType("app.services.rs485_temperature")
    fake_module.Rs485Thermometer = FakeSensor
    monkeypatch.setitem(sys.modules, "app.services.rs485_temperature", fake_module)
    monkeypatch.setattr(
        "app.services.sensor_service._serial_available",
        lambda: True,
    )

    config = SerialPortConfig(
        port="COM3",
        baud_rate="9600",
        data_bits="8",
        stop_bits="1",
        parity="None",
        enable_mock=False,
    )

    failed = sensor_service._read_temperature_hw(config)
    recovered = sensor_service._read_temperature_hw(config)

    assert failed == sensor_service.SensorReading(value=0.0, connected=False)
    assert recovered == sensor_service.SensorReading(value=36.2, connected=True)
    assert read_calls == 2

    sensor_service.invalidate_sensor_sessions()


def test_read_weight_converts_kg_to_g(monkeypatch) -> None:
    import sys
    from types import ModuleType

    from app.services import sensor_service
    from app.schemas.sensor import SerialPortConfig

    sensor_service.invalidate_sensor_sessions()

    class FakeWeightSensor:
        def __init__(self, **_kwargs) -> None:
            self._ser = type("Ser", (), {"is_open": True})()

        def open(self) -> None:
            pass

        def close(self) -> None:
            pass

        def read_net(self):
            return type("Reading", (), {"value": 1.2})()

    fake_module = ModuleType("app.services.km11_weight")
    fake_module.Km11WeightTransmitter = FakeWeightSensor
    monkeypatch.setitem(sys.modules, "app.services.km11_weight", fake_module)
    monkeypatch.setattr(
        "app.services.sensor_service._serial_available",
        lambda: True,
    )

    config = SerialPortConfig(
        port="COM3",
        baud_rate="38400",
        data_bits="8",
        stop_bits="1",
        parity="None",
        enable_mock=False,
    )

    reading = sensor_service._read_weight_hw(config)

    assert reading == sensor_service.SensorReading(value=1200.0, connected=True)

    sensor_service.invalidate_sensor_sessions()


def test_read_weight_returns_negative_kg_as_negative_g(monkeypatch) -> None:
    import sys
    from types import ModuleType

    from app.services import sensor_service
    from app.schemas.sensor import SerialPortConfig

    sensor_service.invalidate_sensor_sessions()

    class FakeWeightSensor:
        def __init__(self, **_kwargs) -> None:
            self._ser = type("Ser", (), {"is_open": True})()

        def open(self) -> None:
            pass

        def close(self) -> None:
            pass

        def read_net(self):
            return type("Reading", (), {"value": -0.3})()

    fake_module = ModuleType("app.services.km11_weight")
    fake_module.Km11WeightTransmitter = FakeWeightSensor
    monkeypatch.setitem(sys.modules, "app.services.km11_weight", fake_module)
    monkeypatch.setattr(
        "app.services.sensor_service._serial_available",
        lambda: True,
    )

    config = SerialPortConfig(
        port="COM3",
        baud_rate="38400",
        data_bits="8",
        stop_bits="1",
        parity="None",
        enable_mock=False,
    )

    reading = sensor_service._read_weight_hw(config)

    assert reading == sensor_service.SensorReading(value=-300.0, connected=True)

    sensor_service.invalidate_sensor_sessions()


def test_tare_weight_hw_calls_sensor_tare(monkeypatch) -> None:
    import sys
    from types import ModuleType

    from app.services import sensor_service
    from app.schemas.sensor import SerialPortConfig

    sensor_service.invalidate_sensor_sessions()
    tare_calls = 0

    class FakeWeightSensor:
        def __init__(self, **_kwargs) -> None:
            self._ser = type("Ser", (), {"is_open": True})()
            self._kg = 0.5

        def open(self) -> None:
            pass

        def close(self) -> None:
            pass

        def tare(self) -> None:
            nonlocal tare_calls
            tare_calls += 1
            self._kg = 0.0

        def read_net(self):
            return type("Reading", (), {"value": self._kg})()

    fake_module = ModuleType("app.services.km11_weight")
    fake_module.Km11WeightTransmitter = FakeWeightSensor
    monkeypatch.setitem(sys.modules, "app.services.km11_weight", fake_module)
    monkeypatch.setattr(
        "app.services.sensor_service._serial_available",
        lambda: True,
    )

    config = SerialPortConfig(
        port="COM3",
        baud_rate="38400",
        data_bits="8",
        stop_bits="1",
        parity="None",
        enable_mock=False,
    )

    reading = sensor_service._tare_weight_hw(config)

    assert tare_calls == 1
    assert reading == sensor_service.SensorReading(value=0.0, connected=True)

    sensor_service.invalidate_sensor_sessions()


def test_post_weight_tare_mock(client: TestClient) -> None:
    response = client.post("/api/v1/sensors/weight/tare")
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == 0.0
    assert data["connected"] is True


def test_zero_weight_hw_calls_sensor_zero(monkeypatch) -> None:
    import sys
    from types import ModuleType

    from app.services import sensor_service
    from app.schemas.sensor import SerialPortConfig

    sensor_service.invalidate_sensor_sessions()
    zero_calls = 0

    class FakeWeightSensor:
        def __init__(self, **_kwargs) -> None:
            self._ser = type("Ser", (), {"is_open": True})()
            self._kg = 0.5

        def open(self) -> None:
            pass

        def close(self) -> None:
            pass

        def zero(self):
            nonlocal zero_calls
            zero_calls += 1
            self._kg = 0.0
            return type("Reading", (), {"value": self._kg, "raw": 0, "decimal_places": 1})()

        def read_net(self):
            return type("Reading", (), {"value": self._kg})()

    fake_module = ModuleType("app.services.km11_weight")
    fake_module.Km11WeightTransmitter = FakeWeightSensor
    monkeypatch.setitem(sys.modules, "app.services.km11_weight", fake_module)
    monkeypatch.setattr(
        "app.services.sensor_service._serial_available",
        lambda: True,
    )

    config = SerialPortConfig(
        port="COM3",
        baud_rate="38400",
        data_bits="8",
        stop_bits="1",
        parity="None",
        enable_mock=False,
    )

    reading = sensor_service._zero_weight_hw(config)

    assert zero_calls == 1
    assert reading == sensor_service.SensorReading(value=0.0, connected=True)

    sensor_service.invalidate_sensor_sessions()


def test_post_weight_zero_mock(client: TestClient) -> None:
    response = client.post("/api/v1/sensors/weight/zero")
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == 0.0
    assert data["connected"] is True

    follow_up = client.get("/api/v1/sensors/weight")
    assert follow_up.status_code == 200
    assert abs(follow_up.json()["value"]) <= 0.2


def test_post_weight_tare_returns_502_when_disconnected(
    client: TestClient,
    monkeypatch,
) -> None:
    from app.services import sensor_service

    monkeypatch.setattr(
        "app.api.v1.endpoints.sensors.tare_weight",
        lambda: sensor_service.SensorReading(value=0.0, connected=False),
    )

    response = client.post("/api/v1/sensors/weight/tare")
    assert response.status_code == 502
    assert "校准失败" in response.json()["detail"]
