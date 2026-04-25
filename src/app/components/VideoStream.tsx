import { useEffect, useRef, useState } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Video, VideoOff } from "lucide-react";

export function VideoStream() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string>("");
  const streamRef = useRef<MediaStream | null>(null);

  const startVideo = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
        audio: false,
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsStreaming(true);
        setError("");
      }
    } catch (err) {
      setError("无法访问摄像头。请检查设备连接和权限设置。");
      console.error("视频流错误:", err);
    }
  };

  const stopVideo = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
  };

  useEffect(() => {
    return () => {
      stopVideo();
    };
  }, []);

  return (
    <Card className="h-full bg-white border-gray-200 flex flex-col shadow-sm">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">实时视频流</h3>
        <Button
          size="sm"
          variant={isStreaming ? "destructive" : "default"}
          onClick={isStreaming ? stopVideo : startVideo}
        >
          {isStreaming ? (
            <>
              <VideoOff className="w-4 h-4 mr-2" />
              停止
            </>
          ) : (
            <>
              <Video className="w-4 h-4 mr-2" />
              启动
            </>
          )}
        </Button>
      </div>
      <div className="flex-1 relative bg-gray-900 overflow-hidden">
        {/* 默认背景图片 - 替换为你自己的图片URL */}
        {!isStreaming && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
            <p className="text-gray-400">等待启动视频流...</p>
          </div>
        )}
        
        {error ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80">
            <div className="text-center p-6">
              <VideoOff className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-300">{error}</p>
            </div>
          </div>
        ) : null}
        
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`w-full h-full object-contain ${isStreaming ? 'block' : 'hidden'}`}
        />
      </div>
    </Card>
  );
}