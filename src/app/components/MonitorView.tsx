import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { VideoStream } from "./VideoStream";
import { SensorDisplay } from "./SensorDisplay";
import { DataEntryTable } from "./DataEntryTable";
import { ConnectionConfig } from "./ConnectionConfig";
import { SampleConfigDialog, SampleConfig } from "./SampleConfigDialog";
import { ViewConfigDialog } from "./ViewConfigDialog";
import { SensorFusionStatus, SensorState } from "./SensorFusionStatus";
import { SensorConfig } from "./SensorConfig";
import { DeleteSampleDialog } from "./DeleteSampleDialog";
import { Activity, Calculator, Plus, Eye, Settings, LogOut, Trash2, LogIn } from "lucide-react";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";

interface SensorData {
  temperature: number;
  weight: number;
  timestamp: Date;
}

interface MonitorViewProps {
  onLogout?: () => void;
  isLoggedIn?: boolean;
  onLoginClick?: () => void;
}

export function MonitorView({ onLogout, isLoggedIn = false, onLoginClick }: MonitorViewProps) {
  const [sensorData, setSensorData] = useState<SensorData>({
    temperature: 25.0,
    weight: 0.0,
    timestamp: new Date(),
  });

  const [isConnected, setIsConnected] = useState(false);
  const [isWaterCutEnabled, setIsWaterCutEnabled] = useState(false);
  const [sampleType, setSampleType] = useState("standardA");
  
  // 样品配置状态
  const [showAddConfig, setShowAddConfig] = useState(false);
  const [showViewConfig, setShowViewConfig] = useState(false);
  const [showDeleteConfig, setShowDeleteConfig] = useState(false);
  
  // 分别管理温度和重量的连接状态
  const [temperatureConnected, setTemperatureConnected] = useState(false);
  const [weightConnected, setWeightConnected] = useState(false);
  
  // 传感器融合状态
  const [temperatureState, setTemperatureState] = useState<SensorState>("reset");
  const [weightState, setWeightState] = useState<SensorState>("reset");
  const [visionState, setVisionState] = useState<SensorState>("reset");
  
  const [sampleConfigs, setSampleConfigs] = useState<Record<string, SampleConfig>>({
    standardA: {
      name: "标准样品A",
      temperature: { min: 20, max: 30 },
      weight: { min: 100, max: 150 },
      length: { min: 95, max: 105 },
      width: { min: 45, max: 55 },
      height: { min: 25, max: 35 },
      waterCutWidth: { min: 40, max: 50 },
    },
    standardB: {
      name: "标准样品B",
      temperature: { min: 22, max: 28 },
      weight: { min: 120, max: 140 },
      length: { min: 98, max: 108 },
      width: { min: 48, max: 52 },
      height: { min: 28, max: 32 },
      waterCutWidth: { min: 42, max: 48 },
    },
  });
  
  const handleSaveConfig = (config: SampleConfig) => {
    const configId = `custom_${Date.now()}`;
    setSampleConfigs({
      ...sampleConfigs,
      [configId]: config,
    });
    setSampleType(configId);
  };

  const handleDeleteConfig = (configId: string) => {
    const newConfigs = { ...sampleConfigs };
    delete newConfigs[configId];
    setSampleConfigs(newConfigs);
    if (sampleType === configId) {
      setSampleType("standardA");
    }
  };

  // 模拟传感器数据更新
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(() => {
      setSensorData({
        temperature: 20 + Math.random() * 10,
        weight: Math.random() * 1000,
        timestamp: new Date(),
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isConnected]);

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <Tabs defaultValue="monitor" className="flex-1 flex flex-col min-h-0">
        <div className="border-b border-gray-200 bg-white shadow-sm flex-shrink-0">
          <div className="flex items-center justify-between px-6 py-3">
            <div className="flex items-center gap-3">
              <Activity className="w-6 h-6 text-blue-600" />
              <h1 className="text-xl font-semibold text-gray-900">传感器监控系统</h1>
            </div>
            <div className="flex items-center gap-4">
              <TabsList className="bg-gray-100">
                <TabsTrigger value="monitor">主监控</TabsTrigger>
                <TabsTrigger value="config">连接配置</TabsTrigger>
                <TabsTrigger value="sensor">传感器配置</TabsTrigger>
              </TabsList>
              {onLogout && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onLogout}
                  className="gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  退出登录
                </Button>
              )}
              {!isLoggedIn && onLoginClick && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onLoginClick}
                  className="gap-2"
                >
                  <LogIn className="w-4 h-4" />
                  登录
                </Button>
              )}
            </div>
          </div>
        </div>

        <TabsContent value="monitor" className="flex-1 m-0 overflow-auto min-h-0">
          <div className="p-6 space-y-4">
            {/* 控制按钮区域 */}
            <div className="flex items-center gap-3 flex-wrap">
              <div className="flex items-center gap-3">
                <Label htmlFor="sampleType" className="text-gray-700">样品类型</Label>
                <Select value={sampleType} onValueChange={setSampleType}>
                  <SelectTrigger id="sampleType" className="w-48 bg-white border-gray-300">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(sampleConfigs).map(([id, config]) => (
                      <SelectItem key={id} value={id}>
                        {config.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button
                onClick={() => setIsWaterCutEnabled(!isWaterCutEnabled)}
                variant={isWaterCutEnabled ? "default" : "outline"}
                className="gap-2"
              >
                <Calculator className="w-4 h-4" />
                {isWaterCutEnabled ? "水切计算已启动" : "启动水切计算"}
              </Button>

              {isLoggedIn && (
                <>
                  <Button
                    onClick={() => setShowAddConfig(true)}
                    variant="outline"
                    className="gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    添加样品
                  </Button>

                  <Button
                    onClick={() => setShowDeleteConfig(true)}
                    variant="outline"
                    className="gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    删除样品
                  </Button>
                </>
              )}

              <Button
                onClick={() => setShowViewConfig(true)}
                variant="outline"
                className="gap-2"
              >
                <Eye className="w-4 h-4" />
                查看当前样品配置
              </Button>

              {isWaterCutEnabled && (
                <span className="text-sm text-green-600 font-medium">
                  水切计算功能已激活
                </span>
              )}
            </div>

            {/* 视频和传感器数据区域 */}
            <div className="grid grid-cols-4 gap-4">
              {/* 视频流 - 占2列 */}
              <div className="col-span-2">
                <VideoStream />
              </div>

              {/* 传感器数据 - 占1列 */}
              <div className="col-span-1">
                <SensorDisplay
                  temperature={sensorData.temperature}
                  weight={sensorData.weight}
                  timestamp={sensorData.timestamp}
                  isConnected={isConnected}
                  temperatureConnected={temperatureConnected}
                  weightConnected={weightConnected}
                />
              </div>

              {/* 传感器融合状态 - 占1列 */}
              <div className="col-span-1">
                <SensorFusionStatus
                  temperatureState={temperatureState}
                  weightState={weightState}
                  visionState={visionState}
                />
              </div>
            </div>

            {/* 数据录入表格 */}
            <div>
              <DataEntryTable
                isWaterCutEnabled={isWaterCutEnabled}
                sampleType={sampleType}
                sampleName={sampleConfigs[sampleType]?.name || ""}
                currentSensorData={sensorData}
                weightRange={sampleConfigs[sampleType]?.weight}
                onAddRecord={(record) => {
                  console.log("新记录:", record);
                }}
              />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="config" className="flex-1 m-0 overflow-y-auto min-h-0">
          <ConnectionConfig
            onConnectionChange={(connected) => setIsConnected(connected)}
          />
        </TabsContent>

        <TabsContent value="sensor" className="flex-1 m-0 overflow-y-auto min-h-0">
          <div className="p-6">
            <SensorConfig
              onConfigChange={(config) => {
                console.log("传感器配置更新:", config);
              }}
            />
          </div>
        </TabsContent>
      </Tabs>

      {/* 样品配置弹框 */}
      <SampleConfigDialog
        open={showAddConfig}
        onClose={() => setShowAddConfig(false)}
        onSave={handleSaveConfig}
      />

      {/* 查看配置弹框 */}
      <ViewConfigDialog
        open={showViewConfig}
        onClose={() => setShowViewConfig(false)}
        config={sampleConfigs[sampleType] || null}
      />

      {/* 删除样品弹框 */}
      <DeleteSampleDialog
        open={showDeleteConfig}
        onClose={() => setShowDeleteConfig(false)}
        sampleConfigs={sampleConfigs}
        currentSampleType={sampleType}
        onDelete={handleDeleteConfig}
      />
    </div>
  );
}