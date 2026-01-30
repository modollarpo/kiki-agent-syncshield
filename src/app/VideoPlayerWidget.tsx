"use client";
import React, { useState, useEffect, useRef } from "react";

interface VideoJobStatus {
  job_id: string;
  status: string;
  progress: number;
  video_url?: string;
  error?: string;
}

interface VideoPlayerWidgetProps {
  jobId: string;
}

export const VideoPlayerWidget: React.FC<VideoPlayerWidgetProps> = ({ jobId }) => {
  const [status, setStatus] = useState<VideoJobStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showVideo, setShowVideo] = useState(false);

  const interval = useRef<NodeJS.Timeout | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    const fetchStatus = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/synccreate/video_status?job_id=${jobId}`);
        if (!res.ok) throw new Error("Failed to fetch video status");
        const data = await res.json();
        setStatus(data);
        if (data.status === "completed") {
          setShowVideo(true);
          if (interval.current) clearInterval(interval.current);
        }
        if (data.status === "failed") {
          setError(data.error || "Video generation failed");
          if (interval.current) clearInterval(interval.current);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unknown error");
        if (interval.current) clearInterval(interval.current);
      }
      setLoading(false);
    };
    fetchStatus();
    interval.current = setInterval(fetchStatus, 2000);
    return () => { if (interval.current) clearInterval(interval.current); };
  }, [jobId]);

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (videoRef.current.requestFullscreen) videoRef.current.requestFullscreen();
    }
  };

  if (loading && !status) return <div className="text-xs text-zinc-400">Loading video status...</div>;
  if (error) return <div className="text-xs text-red-400">{error}</div>;
  if (!status) return null;

  return (
    <div className="rounded bg-black/40 p-2 flex flex-col items-center">
      <div className="text-xs mb-1">Video Job Status: <span className="font-mono">{status.status}</span></div>
      {status.status === "in_progress" && (
        <div className="w-full bg-zinc-800 rounded h-2 mb-2" aria-label="Progress bar" role="progressbar" aria-valuenow={status.progress || 0} aria-valuemin={0} aria-valuemax={100}>
          <div className="bg-emerald-500 h-2 rounded" style={{ width: `${status.progress || 0}%` }} />
        </div>
      )}
      {showVideo && status.video_url && (
        <div className="relative w-64 h-40 mt-2">
          <video ref={videoRef} src={status.video_url} controls className="w-64 h-40 rounded shadow-lg" preload="auto" poster="/video_placeholder.png">
            Your browser does not support the video tag.
          </video>
          <button onClick={handleFullscreen} className="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded hover:bg-black/80">Fullscreen</button>
        </div>
      )}
      {status.status === "completed" && status.video_url && (
        <a href={status.video_url} download className="text-emerald-400 text-xs mt-1">Download Video</a>
      )}
    </div>
  );
};
