"use client";
import { useEffect } from "react";
import { useNotify } from "./notifications";

// Listen for compliance/error events from SyncShield (SSE example)
export function ComplianceEventListener() {
  const notify = useNotify();
  useEffect(() => {
    const evtSource = new EventSource("http://localhost:8005/events");
    evtSource.onmessage = (e) => {
      const event = JSON.parse(e.data);
      if (event.type === "compliance_violation") {
        notify(`Compliance violation: ${event.detail}`);
      } else if (event.type === "error") {
        notify(`Error: ${event.detail}`);
      }
    };
    return () => evtSource.close();
  }, [notify]);
  return null;
}
