import { useRef, useState, useEffect } from "react";

interface VideoPlayerProps {
  src: string;
  poster?: string;
  autoPlay?: boolean;
  compact?: boolean;
}

export function VideoPlayer({ src, poster, autoPlay = false, compact = false }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(true);
  const [loop, setLoop] = useState(true);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    setError(false);
    setReady(false);
  }, [src]);

  const togglePlay = () => {
    const v = videoRef.current;
    if (!v) return;
    if (v.paused) {
      v.play();
      setPlaying(true);
    } else {
      v.pause();
      setPlaying(false);
    }
  };

  const toggleMute = () => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = !v.muted;
    setMuted(v.muted);
  };

  const toggleFullscreen = () => {
    const v = videoRef.current;
    if (!v) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      v.requestFullscreen();
    }
  };

  const onTimeUpdate = () => {
    const v = videoRef.current;
    if (!v || !v.duration) return;
    setProgress((v.currentTime / v.duration) * 100);
  };

  const seek = (e: React.MouseEvent<HTMLDivElement>) => {
    const v = videoRef.current;
    if (!v || !v.duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    v.currentTime = ratio * v.duration;
  };

  const fmtTime = (s: number) => {
    if (!s || isNaN(s)) return "0:00";
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-black text-ms-muted text-xs p-4 text-center">
        <div>
          <div className="text-red-400 mb-1">⚠ 视频加载失败</div>
          <div className="text-xs break-all">{src || "无 src"}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative bg-black ${compact ? "h-40" : "h-full"}`}>
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        muted={muted}
        loop={loop}
        playsInline
        autoPlay={autoPlay}
        onTimeUpdate={onTimeUpdate}
        onLoadedMetadata={(e) => {
          setDuration(e.currentTarget.duration);
          setReady(true);
        }}
        onError={() => setError(true)}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        className="w-full h-full object-contain cursor-pointer"
        onClick={togglePlay}
      />
      {/* 加载提示 */}
      {!ready && !error && (
        <div className="absolute inset-0 flex items-center justify-center text-ms-muted text-xs">
          加载中...
        </div>
      )}
      {/* 控制条 */}
      {ready && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
          {/* 进度条 */}
          <div
            className="h-1 bg-ms-border rounded-full cursor-pointer mb-1.5"
            onClick={seek}
          >
            <div
              className="h-full bg-ms-accent rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <button onClick={togglePlay} className="text-white hover:text-ms-accent p-1">
                {playing ? "⏸" : "▶"}
              </button>
              <button onClick={toggleMute} className="text-white hover:text-ms-accent p-1 text-xs">
                {muted ? "🔇" : "🔊"}
              </button>
              <button
                onClick={() => {
                  const v = videoRef.current;
                  if (v) {
                    const nl = !loop;
                    v.loop = nl;
                    setLoop(nl);
                  }
                }}
                className={`p-1 text-xs ${loop ? "text-ms-accent" : "text-white"}`}
              >
                ↻
              </button>
              <span className="text-xs text-gray-400">
                {fmtTime(videoRef.current?.currentTime ?? 0)} / {fmtTime(duration)}
              </span>
            </div>
            <button onClick={toggleFullscreen} className="text-white hover:text-ms-accent p-1 text-xs">
              ⛶
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
