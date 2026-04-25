import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Thermometer, Weight, Camera, Save } from "lucide-react";
import { useState } from "react";

interface SensorConfigProps {
  onConfigChange?: (config: SensorResetConfig) => void;
}

export interface SensorResetConfig {
  temperature: number;
  weight: number;
  depth: number;
}

export function SensorConfig({ onConfigChange }: SensorConfigProps) {
  const [config, setConfig] = useState<SensorResetConfig>({
    temperature: 25,
    weight: 0,
    depth: 0,
  });

  const handleConfigChange = (field: keyof SensorResetConfig, value: string) => {
    const newConfig = {
      ...config,
      [field]: parseFloat(value) || 0,
    };
    setConfig(newConfig);
    onConfigChange?.(newConfig);
  };

  const handleReset = (sensor: 'temperature' | 'weight' | 'depth') => {
    console.log(`保存${sensor}传感器数值: ${config[sensor]}`);
    alert(`已保存${sensor === 'temperature' ? '温度' : sensor === 'weight' ? '重量' : '深度'}数值: ${config[sensor]}`);
  };

  return (
    <div className="space-y-4">
      {/* 红外传感器配置 */}
      <Card className="bg-white border-gray-200 shadow-sm">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Thermometer className="w-5 h-5 text-red-600" />
            <h3 className="font-semibold text-gray-900">红外传感器配置</h3>
          </div>
        </div>
        <div className="p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="resetTemp">重置温度 (°C)</Label>
              <Input
                id="resetTemp"
                type="number"
                step="0.1"
                value={config.temperature}
                onChange={(e) => handleConfigChange('temperature', e.target.value)}
                className="bg-white border-gray-300"
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={() => handleReset('temperature')}
                className="w-full gap-2"
                variant="outline"
              >
                <Save className="w-4 h-4" />
                保存数值
              </Button>
            </div>
          </div>
          <p className="text-xs text-gray-500">
            设置温度传感器的重置基准值，用于校准传感器读数
          </p>
        </div>
      </Card>

      {/* 串口天平配置 */}
      <Card className="bg-white border-gray-200 shadow-sm">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Weight className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">串口天平配置</h3>
          </div>
        </div>
        <div className="p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="resetWeight">重置重量 (g)</Label>
              <Input
                id="resetWeight"
                type="number"
                step="0.01"
                value={config.weight}
                onChange={(e) => handleConfigChange('weight', e.target.value)}
                className="bg-white border-gray-300"
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={() => handleReset('weight')}
                className="w-full gap-2"
                variant="outline"
              >
                <Save className="w-4 h-4" />
                保存数值
              </Button>
            </div>
          </div>
          <p className="text-xs text-gray-500">
            设置天平的重置归零值，通常设置为0用于去皮
          </p>
        </div>
      </Card>

      {/* 实时视频流配置 */}
      <Card className="bg-white border-gray-200 shadow-sm">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Camera className="w-5 h-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">实时视频流配置</h3>
          </div>
        </div>
        <div className="p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="resetDepth">重置深度 (mm)</Label>
              <Input
                id="resetDepth"
                type="number"
                step="0.1"
                value={config.depth}
                onChange={(e) => handleConfigChange('depth', e.target.value)}
                className="bg-white border-gray-300"
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={() => handleReset('depth')}
                className="w-full gap-2"
                variant="outline"
              >
                <Save className="w-4 h-4" />
                保存数值
              </Button>
            </div>
          </div>
          <p className="text-xs text-gray-500">
            设置视觉深度测量的重置基准值，用于校准深度计算
          </p>
        </div>
      </Card>
    </div>
  );
}