"use client";
"use client";
import { useEffect, useState } from "react";

export default function ExplainabilityFeed({ recipientType }: { recipientType: "client" | "admin" }) {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const fetchEvents = async () => {
      const res = await fetch("/api/explainability/events");
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
      <div className="font-semibold mb-2">Explainable AI Feed</div>
      {loading && <div className="text-zinc-400 text-xs">Loading...</div>}
      <ul className="text-xs">
        {events.filter(e => e.recipient_type === recipientType).map((e, i) => (
          <li key={i} className="mb-2">
            {recipientType === "client" ? (
              <span>
                <b>Why:</b> {e.observation || e.reasoning}. <b>What:</b> {e.action}. <b>So What:</b> {e.outcome || (e.financial_impact ? `Estimated ROI: ${e.financial_impact.estimated_roi}${e.financial_impact.currency}` : "")}
              </span>
            ) : (
              <span>
                <b>Agent:</b> {e.agent}. <b>Reason:</b> {e.reasoning}. <b>Action:</b> {e.action}. <b>Recovery:</b> {e.recovery_path || "-"}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
