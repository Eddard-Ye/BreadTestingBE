import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

export interface SampleConfig {
  name: string;
  temperature: { min: number; max: number };
  weight: { min: number; max: number };
  length: { min: number; max: number };
  width: { min: number; max: number };
  height: { min: number; max: number };
  waterCutWidth: { min: number; max: number };
}

interface SampleConfigDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (config: SampleConfig) => void;
  initialConfig?: SampleConfig;
}

export function SampleConfigDialog({
  open,
  onClose,
  onSave,
  initialConfig,
}: SampleConfigDialogProps) {
  const [config, setConfig] = useState<SampleConfig>(
    initialConfig || {
      name: "",
      temperature: { min: 0, max: 0 },
      weight: { min: 0, max: 0 },
      length: { min: 0, max: 0 },
      width: { min: 0, max: 0 },
      height: { min: 0, max: 0 },
      waterCutWidth: { min: 0, max: 0 },
    }
  );

  const handleRangeChange = (
    field: keyof Omit<SampleConfig, "name">,
    type: "min" | "max",
    value: string
  ) => {
    setConfig({
      ...config,
      [field]: {
        ...config[field],
        [type]: parseFloat(value) || 0,
      },
    });
  };

  const handleSave = () => {
    onSave(config);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>添加样品配置</DialogTitle>
          <DialogDescription>
            配置样品的参数范围
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 样品名称 */}
          <div className="space-y-2">
            <Label htmlFor="sampleName">样品名称</Label>
            <Input
              id="sampleName"
              value={config.name}
              onChange={(e) => setConfig({ ...config, name: e.target.value })}
              placeholder="输入样品名称"
              className="bg-white"
            />
          </div>

          {/* 参数范围配置 */}
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">参数范围配置</h4>
            
            {/* 温度 */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-sm">温度下限 (°C)</Label>
                <Input
                  type="number"
                  value={config.temperature.min}
                  onChange={(e) =>
                    handleRangeChange("temperature", "min", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-sm">温度上限 (°C)</Label>
                <Input
                  type="number"
                  value={config.temperature.max}
                  onChange={(e) =>
                    handleRangeChange("temperature", "max", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
            </div>

            {/* 重量 */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-sm">重量下限 (g)</Label>
                <Input
                  type="number"
                  value={config.weight.min}
                  onChange={(e) =>
                    handleRangeChange("weight", "min", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-sm">重量上限 (g)</Label>
                <Input
                  type="number"
                  value={config.weight.max}
                  onChange={(e) =>
                    handleRangeChange("weight", "max", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
            </div>

            {/* 长 */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-sm">长度下限 (mm)</Label>
                <Input
                  type="number"
                  value={config.length.min}
                  onChange={(e) =>
                    handleRangeChange("length", "min", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-sm">长度上限 (mm)</Label>
                <Input
                  type="number"
                  value={config.length.max}
                  onChange={(e) =>
                    handleRangeChange("length", "max", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
            </div>

            {/* 宽 */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-sm">宽度下限 (mm)</Label>
                <Input
                  type="number"
                  value={config.width.min}
                  onChange={(e) =>
                    handleRangeChange("width", "min", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-sm">宽度上限 (mm)</Label>
                <Input
                  type="number"
                  value={config.width.max}
                  onChange={(e) =>
                    handleRangeChange("width", "max", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
            </div>

            {/* 高 */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-sm">高度下限 (mm)</Label>
                <Input
                  type="number"
                  value={config.height.min}
                  onChange={(e) =>
                    handleRangeChange("height", "min", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-sm">高度上限 (mm)</Label>
                <Input
                  type="number"
                  value={config.height.max}
                  onChange={(e) =>
                    handleRangeChange("height", "max", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
            </div>

            {/* 水切宽度 */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-sm">水切宽度下限 (mm)</Label>
                <Input
                  type="number"
                  value={config.waterCutWidth.min}
                  onChange={(e) =>
                    handleRangeChange("waterCutWidth", "min", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-sm">水切宽度上限 (mm)</Label>
                <Input
                  type="number"
                  value={config.waterCutWidth.max}
                  onChange={(e) =>
                    handleRangeChange("waterCutWidth", "max", e.target.value)
                  }
                  className="bg-white"
                />
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            取消
          </Button>
          <Button onClick={handleSave}>保存配置</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}