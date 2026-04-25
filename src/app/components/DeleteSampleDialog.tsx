import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
  } from "./ui/dialog";
  import { Button } from "./ui/button";
  import { Label } from "./ui/label";
  import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
  import { Trash2 } from "lucide-react";
  import { useState } from "react";
  import { SampleConfig } from "./SampleConfigDialog";
  
  interface DeleteSampleDialogProps {
    open: boolean;
    onClose: () => void;
    sampleConfigs: Record<string, SampleConfig>;
    currentSampleType: string;
    onDelete: (sampleId: string) => void;
  }
  
  export function DeleteSampleDialog({
    open,
    onClose,
    sampleConfigs,
    currentSampleType,
    onDelete,
  }: DeleteSampleDialogProps) {
    const [selectedSample, setSelectedSample] = useState("");
  
    // 过滤出可删除的样品（排除标准样品A和B）
    const deletableSamples = Object.entries(sampleConfigs).filter(
      ([id]) => id !== "standardA" && id !== "standardB"
    );
  
    const handleDelete = () => {
      if (!selectedSample) return;
  
      if (selectedSample === currentSampleType) {
        alert("无法删除当前正在使用的样品配置，请先切换到其他样品类型");
        return;
      }
  
      onDelete(selectedSample);
      setSelectedSample("");
      onClose();
    };
  
    const handleClose = () => {
      setSelectedSample("");
      onClose();
    };
  
    return (
      <Dialog open={open} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Trash2 className="w-5 h-5 text-red-600" />
              删除样品配置
            </DialogTitle>
            <DialogDescription>
              选择要删除的样品配置。标准样品A和B无法删除。
            </DialogDescription>
          </DialogHeader>
  
          <div className="space-y-4">
            {deletableSamples.length === 0 ? (
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <p className="text-sm text-gray-600">暂无可删除的样品配置</p>
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="sampleToDelete">选择样品</Label>
                <Select value={selectedSample} onValueChange={setSelectedSample}>
                  <SelectTrigger id="sampleToDelete" className="bg-white border-gray-300">
                    <SelectValue placeholder="请选择要删除的样品" />
                  </SelectTrigger>
                  <SelectContent>
                    {deletableSamples.map(([id, config]) => (
                      <SelectItem key={id} value={id}>
                        {config.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
  
            {selectedSample && selectedSample === currentSampleType && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-2">
                <p className="text-sm text-yellow-700">
                  ⚠️ 无法删除当前正在使用的样品配置
                </p>
              </div>
            )}
          </div>
  
          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              取消
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={handleDelete}
              disabled={!selectedSample || deletableSamples.length === 0}
            >
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }