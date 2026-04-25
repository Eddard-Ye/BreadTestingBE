import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Lock } from "lucide-react";

interface LoginDialogProps {
  open: boolean;
  onClose: () => void;
  onLogin: (passcode: string) => void;
}

export function LoginDialog({ open, onClose, onLogin }: LoginDialogProps) {
  const [passcode, setPasscode] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!passcode) {
      setError("请输入登录口令");
      return;
    }

    // 简单的演示验证，口令为 "admin123"
    if (passcode === "admin123") {
      setError("");
      onLogin(passcode);
      setPasscode("");
      onClose();
    } else {
      setError("口令错误");
    }
  };

  const handleClose = () => {
    setPasscode("");
    setError("");
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Lock className="w-5 h-5 text-blue-600" />
            管理员登录
          </DialogTitle>
          <DialogDescription>
            请输入登录口令以访问样品配置管理功能
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="passcode">登录口令</Label>
            <Input
              id="passcode"
              type="password"
              value={passcode}
              onChange={(e) => setPasscode(e.target.value)}
              placeholder="请输入口令"
              className="bg-white border-gray-300"
              autoFocus
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-2">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
            演示口令：admin123
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              取消
            </Button>
            <Button type="submit">
              登录
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}