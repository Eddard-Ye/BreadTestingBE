import { Card } from "./ui/card";
import { Thermometer, Weight, Camera, AlertCircle } from "lucide-react";

export type SensorState = "reset" | "measuring" | "complete";

interface SensorFusionStatusProps {
  temperatureState: SensorState;
  weightState: SensorState;
  visionState: SensorState;
}

const stateLabels: Record<SensorState, string> = {
  reset: "等待测量",
  measuring: "正在测量",
  complete: "测量完成",
};

const stateColors: Record<SensorState, string> = {
  reset: "text-gray-500 bg-gray-100",
  measuring: "text-blue-600 bg-blue-100",
  complete: "text-green-600 bg-green-100",
};

export function SensorFusionStatus({
  temperatureState,
  weightState,
  visionState,
}: SensorFusionStatusProps) {
  const allComplete =
    temperatureState === "complete" &&
    weightState === "complete" &&
    visionState === "complete";

  return (
    <Card className="bg-white border-gray-200 shadow-sm">
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">数据融合状态</h3>
      </div>

      <div className="p-4 space-y-3">
        {/* 温度传感器状态 */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <Thermometer className="w-5 h-5 text-red-600" />
            </div>
            <span className="text-sm font-medium text-gray-700">温度传感器</span>
          </div>
          <span
            className={`text-xs font-medium px-3 py-1 rounded-full ${stateColors[temperatureState]}`}
          >
            {stateLabels[temperatureState]}
          </span>
        </div>

        {/* 重量传感器状态 */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Weight className="w-5 h-5 text-blue-600" />
            </div>
            <span className="text-sm font-medium text-gray-700">重量传感器</span>
          </div>
          <span
            className={`text-xs font-medium px-3 py-1 rounded-full ${stateColors[weightState]}`}
          >
            {stateLabels[weightState]}
          </span>
        </div>

        {/* 视觉传感器状态 */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Camera className="w-5 h-5 text-purple-600" />
            </div>
            <span className="text-sm font-medium text-gray-700">视觉传感器</span>
          </div>
          <span
            className={`text-xs font-medium px-3 py-1 rounded-full ${stateColors[visionState]}`}
          >
            {stateLabels[visionState]}
          </span>
        </div>

        {/* 整体状态提示 */}
        <div
          className={`flex items-center gap-2 p-3 rounded-lg border-2 ${
            allComplete
              ? "bg-green-50 border-green-200"
              : "bg-yellow-50 border-yellow-200"
          }`}
        >
          <AlertCircle
            className={`w-5 h-5 flex-shrink-0 ${
              allComplete ? "text-green-600" : "text-yellow-600"
            }`}
          />
          <span
            className={`text-sm font-medium ${
              allComplete ? "text-green-700" : "text-yellow-700"
            }`}
          >
            {allComplete
              ? "所有传感器测量完成，可记录数据"
              : "等待所有传感器测量完成"}
          </span>
        </div>
      </div>
    </Card>
  );
}