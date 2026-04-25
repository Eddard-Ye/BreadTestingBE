import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
  } from "./ui/dialog";
  import { SampleConfig } from "./SampleConfigDialog";
  
  interface ViewConfigDialogProps {
    open: boolean;
    onClose: () => void;
    config: SampleConfig | null;
  }
  
  export function ViewConfigDialog({
    open,
    onClose,
    config,
  }: ViewConfigDialogProps) {
    if (!config) return null;
  
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>样品配置详情</DialogTitle>
            <DialogDescription>
              查看当前样品的参数范围和SPC控制数据
            </DialogDescription>
          </DialogHeader>
  
          <div className="space-y-4 py-4">
            {/* 样品名称 */}
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900">样品名称</h4>
              <p className="text-gray-700">{config.name}</p>
            </div>
  
            {/* 参数范围 */}
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">参数范围配置</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600">温度 (°C)</p>
                  <p className="text-gray-900 font-medium">
                    {config.temperature.min} ~ {config.temperature.max}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600">重量 (g)</p>
                  <p className="text-gray-900 font-medium">
                    {config.weight.min} ~ {config.weight.max}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600">长 (mm)</p>
                  <p className="text-gray-900 font-medium">
                    {config.length.min} ~ {config.length.max}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600">宽 (mm)</p>
                  <p className="text-gray-900 font-medium">
                    {config.width.min} ~ {config.width.max}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600">高 (mm)</p>
                  <p className="text-gray-900 font-medium">
                    {config.height.min} ~ {config.height.max}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600">水切宽度 (mm)</p>
                  <p className="text-gray-900 font-medium">
                    {config.waterCutWidth.min} ~ {config.waterCutWidth.max}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }