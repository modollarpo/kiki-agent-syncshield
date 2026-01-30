"use client";
import { useEffect, useState } from "react";

export default function ReasoningFeed() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const fetchEvents = async () => {
      const res = await fetch("/api/syncnotify/reasoning");
      const data = await res.json();
      setEvents(data || []);
      setLoading(false);
    };
    fetchEvents();
    const interval = setInterval(fetchEvents, 5000);
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="rounded-xl p-4 bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">Reasoning Feed (Explainable AI)</div>
      {loading && <div className="text-zinc-400 text-xs">Loading...</div>}
      <ul className="text-xs">
        {events.map((e, i) => (
          <li key={i} className="mb-2">
            <b>Intent:</b> {e.intent}. <b>Evidence:</b> {e.evidence}. <b>Reasoning:</b> {e.reasoning_text}
          </li>
        ))}
      </ul>
    </div>
  );
}
