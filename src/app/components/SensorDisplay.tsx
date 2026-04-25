import { Card } from "./ui/card";
import { Thermometer, Weight, Circle } from "lucide-react";

interface SensorDisplayProps {
  temperature: number;
  weight: number;
  timestamp: Date;
  isConnected: boolean;
  temperatureConnected?: boolean;
  weightConnected?: boolean;
}

export function SensorDisplay({
  temperature,
  weight,
  timestamp,
  isConnected,
  temperatureConnected = false,
  weightConnected = false,
}: SensorDisplayProps) {
  return (
    <Card className="h-full bg-white border-gray-200 flex flex-col shadow-sm">
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">传感器数据</h3>
      </div>

      <div className="flex-1 p-6 space-y-6">
        {/* 温度显示 */}
        <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-lg p-6 border border-red-100">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-100 rounded-lg">
                <Thermometer className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-gray-700 font-medium">温度</p>
                <p className="text-xs text-gray-500">红外传感器</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Circle
                className={`w-2 h-2 ${
                  temperatureConnected ? "fill-green-500 text-green-500" : "fill-gray-400 text-gray-400"
                }`}
              />
              <span className="text-xs text-gray-600">
                {temperatureConnected ? "已连接" : "未连接"}
              </span>
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-5xl font-bold text-red-600">
              {temperature.toFixed(1)}
            </span>
            <span className="text-2xl text-gray-500">°C</span>
          </div>
        </div>

        {/* 重量显示 */}
        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-6 border border-blue-100">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Weight className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-700 font-medium">重量</p>
                <p className="text-xs text-gray-500">串口天平</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Circle
                className={`w-2 h-2 ${
                  weightConnected ? "fill-green-500 text-green-500" : "fill-gray-400 text-gray-400"
                }`}
              />
              <span className="text-xs text-gray-600">
                {weightConnected ? "已连接" : "未连接"}
              </span>
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-5xl font-bold text-blue-600">
              {weight.toFixed(2)}
            </span>
            <span className="text-2xl text-gray-500">g</span>
          </div>
        </div>

        {/* 时间戳 */}
        <div className="pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            最后更新: {timestamp.toLocaleTimeString("zh-CN")}
          </p>
        </div>
      </div>
    </Card>
  );
}