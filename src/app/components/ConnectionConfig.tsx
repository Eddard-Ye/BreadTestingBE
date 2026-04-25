import { useState, useEffect } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Usb, Video, CheckCircle2, XCircle, Thermometer, RefreshCw } from "lucide-react";
import { toast } from "sonner";

interface ConnectionConfigProps {
  onConnectionChange?: (connected: boolean) => void;
}

export function ConnectionConfig({ onConnectionChange }: ConnectionConfigProps) {
  const [serialPort, setSerialPort] = useState<SerialPort | null>(null);
  const [serialConnected, setSerialConnected] = useState(false);
  const [infraredPort, setInfraredPort] = useState<SerialPort | null>(null);
  const [infraredConnected, setInfraredConnected] = useState(false);
  const [videoConnected, setVideoConnected] = useState(false);
  
  const [availableSerialPorts, setAvailableSerialPorts] = useState<string[]>(["COM1", "COM2", "COM3", "COM4"]);
  const [selectedScalePort, setSelectedScalePort] = useState("");
  const [selectedInfraredPort, setSelectedInfraredPort] = useState("");
  
  const [availableVideoDevices, setAvailableVideoDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedVideoDevice, setSelectedVideoDevice] = useState("");

  const [serialBaudRate, setSerialBaudRate] = useState("9600");
  const [serialDataBits, setSerialDataBits] = useState("8");
  const [serialStopBits, setSerialStopBits] = useState("1");
  const [serialParity, setSerialParity] = useState("none");

  const [infraredBaudRate, setInfraredBaudRate] = useState("9600");
  const [infraredDataBits, setInfraredDataBits] = useState("8");
  const [infraredStopBits, setInfraredStopBits] = useState("1");
  const [infraredParity, setInfraredParity] = useState("none");

  // 获取可用的视频设备
  const getVideoDevices = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === "videoinput");
      setAvailableVideoDevices(videoDevices);
      if (videoDevices.length > 0 && !selectedVideoDevice) {
        setSelectedVideoDevice(videoDevices[0].deviceId);
      }
    } catch (error) {
      console.error("获取视频设备错误:", error);
      toast.error("无法获取视频设备列表");
    }
  };

  useEffect(() => {
    getVideoDevices();
  }, []);

  const refreshSerialPorts = () => {
    setAvailableSerialPorts(["COM1", "COM2", "COM3", "COM4"]);
    toast.info("串口列表已刷新");
  };

  const connectSerial = async () => {
    try {
      if (!selectedScalePort) {
        toast.error("请选择天平串口");
        return;
      }
      
      // Web Serial API
      const port = await (navigator as any).serial.requestPort();
      await port.open({
        baudRate: parseInt(serialBaudRate),
        dataBits: parseInt(serialDataBits),
        stopBits: parseInt(serialStopBits),
        parity: serialParity as any,
      });

      setSerialPort(port);
      setSerialConnected(true);
      toast.success(`天平串口连接成功 (${selectedScalePort})`);
      onConnectionChange?.(true);

      const reader = port.readable.getReader();
      readLoop(reader);
    } catch (error) {
      console.error("串口连接错误:", error);
      toast.error("串口连接失败，请检查设备或浏览器权限");
    }
  };

  const disconnectSerial = async () => {
    if (serialPort) {
      try {
        await serialPort.close();
        setSerialPort(null);
        setSerialConnected(false);
        toast.info("天平串口已断开");
        onConnectionChange?.(false);
      } catch (error) {
        console.error("断开串口错误:", error);
      }
    }
  };

  const connectInfrared = async () => {
    try {
      if (!selectedInfraredPort) {
        toast.error("请选择红外传感器串口");
        return;
      }

      const port = await (navigator as any).serial.requestPort();
      await port.open({
        baudRate: parseInt(infraredBaudRate),
        dataBits: parseInt(infraredDataBits),
        stopBits: parseInt(infraredStopBits),
        parity: infraredParity as any,
      });

      setInfraredPort(port);
      setInfraredConnected(true);
      toast.success(`红外传感器串口连接成功 (${selectedInfraredPort})`);

      const reader = port.readable.getReader();
      readLoop(reader);
    } catch (error) {
      console.error("红外串口连接错误:", error);
      toast.error("红外串口连接失败，请检查设备或浏览器权限");
    }
  };

  const disconnectInfrared = async () => {
    if (infraredPort) {
      try {
        await infraredPort.close();
        setInfraredPort(null);
        setInfraredConnected(false);
        toast.info("红外传感器串口已断开");
      } catch (error) {
        console.error("断开红外串口错误:", error);
      }
    }
  };

  const readLoop = async (reader: any) => {
    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          reader.releaseLock();
          break;
        }
        console.log("接收数据:", new TextDecoder().decode(value));
      }
    } catch (error) {
      console.error("读取数据错误:", error);
    }
  };

  const connectVideo = async () => {
    try {
      if (!selectedVideoDevice) {
        toast.error("请选择摄像头设备");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: selectedVideoDevice },
      });
      stream.getTracks().forEach((track) => track.stop());
      setVideoConnected(true);
      toast.success("视频设备连接成功");
    } catch (error) {
      console.error("视频连接错误:", error);
      toast.error("视频设备连接失败，请检查摄像头或浏览器权限");
    }
  };

  const disconnectVideo = () => {
    setVideoConnected(false);
    toast.info("视频设备已断开");
  };

  return (
    <div className="p-6 space-y-6">
      {/* 天平串口连接配置 */}
      <Card className="bg-white border-gray-200 shadow-sm">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Usb className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">天平串口连接</h3>
                <p className="text-sm text-gray-600">配置天平串口参数</p>
              </div>
            </div>
            {serialConnected ? (
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle2 className="w-5 h-5" />
                <span className="text-sm">已连接</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-gray-400">
                <XCircle className="w-5 h-5" />
                <span className="text-sm">未连接</span>
              </div>
            )}
          </div>

          <div className="space-y-4 mb-6">
            <div className="flex items-end gap-2">
              <div className="flex-1 space-y-2">
                <Label htmlFor="scalePort" className="text-gray-700">选择串口</Label>
                <Select value={selectedScalePort} onValueChange={setSelectedScalePort}>
                  <SelectTrigger id="scalePort" className="bg-gray-50 border-gray-300">
                    <SelectValue placeholder="选择天平串口" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableSerialPorts.map(port => (
                      <SelectItem key={port} value={port}>{port}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button size="sm" variant="outline" onClick={refreshSerialPorts}>
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="baudRate" className="text-gray-700">波特率</Label>
                <Select value={serialBaudRate} onValueChange={setSerialBaudRate}>
                  <SelectTrigger id="baudRate" className="bg-gray-50 border-gray-300">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="9600">9600</SelectItem>
                    <SelectItem value="19200">19200</SelectItem>
                    <SelectItem value="38400">38400</SelectItem>
                    <SelectItem value="57600">57600</SelectItem>
                    <SelectItem value="115200">115200</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dataBits" className="text-gray-700">数据位</Label>
                <Select value={serialDataBits} onValueChange={setSerialDataBits}>
                  <SelectTrigger id="dataBits" className="bg-gray-50 border-gray-300">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7">7</SelectItem>
                    <SelectItem value="8">8</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="stopBits" className="text-gray-700">停止位</Label>
                <Select value={serialStopBits} onValueChange={setSerialStopBits}>
                  <SelectTrigger id="stopBits" className="bg-gray-50 border-gray-300">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1</SelectItem>
                    <SelectItem value="2">2</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="parity" className="text-gray-700">校验位</Label>
                <Select value={serialParity} onValueChange={setSerialParity}>
                  <SelectTrigger id="parity" className="bg-gray-50 border-gray-300">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">无</SelectItem>
                    <SelectItem value="even">偶校验</SelectItem>
                    <SelectItem value="odd">奇校验</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <Button
            onClick={serialConnected ? disconnectSerial : connectSerial}
            className="w-full"
            variant={serialConnected ? "destructive" : "default"}
          >
            {serialConnected ? "断开连接" : "连接串口"}
          </Button>
        </div>
      </Card>

      {/* 红外传感器串口连接配置 */}
      <Card className="bg-white border-gray-200 shadow-sm">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-100 rounded-lg">
                <Thermometer className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">红外传感器串口连接</h3>
                <p className="text-sm text-gray-600">配置红外传感器串口参数</p>
              </div>
            </div>
            {infraredConnected ? (
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle2 className="w-5 h-5" />
                <span className="text-sm">已连接</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-gray-400">
                <XCircle className="w-5 h-5" />
                <span className="text-sm">未连接</span>
              </div>
            )}
          </div>

          <div className="space-y-4 mb-6">
            <div className="flex items-end gap-2">
              <div className="flex-1 space-y-2">
                <Label htmlFor="infraredPort" className="text-gray-700">选择串口</Label>
                <Select value={selectedInfraredPort} onValueChange={setSelectedInfraredPort}>
                  <SelectTrigger id="infraredPort" className="bg-gray-50 border-gray-300">
                    <SelectValue placeholder="选择红外传感器串口" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableSerialPorts.map(port => (
                      <SelectItem key={port} value={port}>{port}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button size="sm" variant="outline" onClick={refreshSerialPorts}>
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="infraredBaudRate" className="text-gray-700">波特率</Label>
                <Select value={infraredBaudRate} onValueChange={setInfraredBaudRate}>
                  <SelectTrigger id="infraredBaudRate" className="bg-gray-50 border-gray-300">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="9600">9600</SelectItem>
                    <SelectItem value="19200">19200</SelectItem>
                    <SelectItem value="38400">38400</SelectItem>
                    <SelectItem value="57600">57600</SelectItem>
                    <SelectItem value="115200">115200</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="infraredDataBits" className="text-gray-700">数据位</Label>
                <Select value={infraredDataBits} onValueChange={setInfraredDataBits}>
                  <SelectTrigger id="infraredDataBits" className="bg-gray-50 border-gray-300">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7">7</SelectItem>
                    <SelectItem value="8">8</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="infraredStopBits" className="text-gray-700">停止位</Label>
                <Select value={infraredStopBits} onValueChange={setInfraredStopBits}>
                  <SelectTrigger id="infraredStopBits" className="bg-gray-50 border-gray-300">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1</SelectItem>
                    <SelectItem value="2">2</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="infraredParity" className="text-gray-700">校验位</Label>
                <Select value={infraredParity} onValueChange={setInfraredParity}>
                  <SelectTrigger id="infraredParity" className="bg-gray-50 border-gray-300">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">无</SelectItem>
                    <SelectItem value="even">偶校验</SelectItem>
                    <SelectItem value="odd">奇校验</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <Button
            onClick={infraredConnected ? disconnectInfrared : connectInfrared}
            className="w-full"
            variant={infraredConnected ? "destructive" : "default"}
          >
            {infraredConnected ? "断开连接" : "连接串口"}
          </Button>
        </div>
      </Card>

      {/* 视频连接配置 */}
      <Card className="bg-white border-gray-200 shadow-sm">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Video className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">视频连接</h3>
                <p className="text-sm text-gray-600">配置摄像头设备</p>
              </div>
            </div>
            {videoConnected ? (
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle2 className="w-5 h-5" />
                <span className="text-sm">已连接</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-gray-400">
                <XCircle className="w-5 h-5" />
                <span className="text-sm">未连接</span>
              </div>
            )}
          </div>

          <div className="space-y-4 mb-6">
            <div className="flex items-end gap-2">
              <div className="flex-1 space-y-2">
                <Label htmlFor="videoDevice" className="text-gray-700">选择摄像头</Label>
                <Select value={selectedVideoDevice} onValueChange={setSelectedVideoDevice}>
                  <SelectTrigger id="videoDevice" className="bg-gray-50 border-gray-300">
                    <SelectValue placeholder="选择摄像头设备" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableVideoDevices.length > 0 ? (
                      availableVideoDevices
                        .filter(device => device.deviceId && device.deviceId.trim() !== "")
                        .map(device => (
                          <SelectItem key={device.deviceId} value={device.deviceId}>
                            {device.label || `摄像头 ${device.deviceId.substring(0, 8)}`}
                          </SelectItem>
                        ))
                    ) : (
                      <SelectItem value="no-device" disabled>
                        未检测到摄像头设备
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
              <Button size="sm" variant="outline" onClick={getVideoDevices}>
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>

            <p className="text-sm text-gray-600">
              连接后可在主监控界面启动视频流。系统将使用所选摄像头进行视频采集。
            </p>
          </div>

          <Button
            onClick={videoConnected ? disconnectVideo : connectVideo}
            className="w-full"
            variant={videoConnected ? "destructive" : "default"}
          >
            {videoConnected ? "断开连接" : "连接视频设备"}
          </Button>
        </div>
      </Card>

      {/* 提示信息 */}
      <Card className="bg-amber-50 border-amber-200 shadow-sm">
        <div className="p-6">
          <h4 className="font-semibold mb-2 text-amber-900">注意事项</h4>
          <ul className="text-sm text-amber-800 space-y-1 list-disc list-inside">
            <li>串口连接需要使用支持 Web Serial API 的浏览器（Chrome、Edge 等）</li>
            <li>首次连接时需要授予浏览器相应的设备访问权限</li>
            <li>确保设备驱动程序已正确安装</li>
            <li>连接前请关闭其他占用串口的应用程序</li>
            <li>请确保天平和红外传感器连接到不同的串口</li>
          </ul>
        </div>
      </Card>
    </div>
  );
}