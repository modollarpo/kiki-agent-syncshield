"use client";
import React from "react";

interface VideoGalleryProps {
  videos: { job_id: string; video_url: string; prompt?: string; created_at?: string }[];
  onSelect?: (jobId: string) => void;
}

export const VideoGallery: React.FC<VideoGalleryProps> = ({ videos, onSelect }) => {
  if (!videos.length) return <div className="text-zinc-400 text-xs">No videos yet.</div>;
  return (
    <div className="flex flex-wrap gap-4">
      {videos.map((v, i) => (
        <div key={v.job_id || i} className="w-40 cursor-pointer" onClick={() => onSelect?.(v.job_id)}>
          <video src={v.video_url} controls className="w-40 h-28 rounded shadow mb-1" preload="auto" poster="/video_placeholder.png" />
          <div className="text-xs truncate">{v.prompt || "(no prompt)"}</div>
          {v.created_at && <div className="text-xs text-zinc-400">{new Date(v.created_at).toLocaleString()}</div>}
          <a href={v.video_url} download className="text-emerald-400 text-xs">Download</a>
        </div>
      ))}
    </div>
  );
};
