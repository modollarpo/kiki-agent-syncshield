"use client";
import { useEffect, useRef, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";

function exportCSV(logs: string[]) {
  const csvContent = "data:text/csv;charset=utf-8," + logs.map(l => `"${l.replace(/"/g, '""')}"`).join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "logs.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function exportTXT(logs: string[]) {
  const txtContent = "data:text/plain;charset=utf-8," + logs.join("\n");
  const encodedUri = encodeURI(txtContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "logs.txt");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function exportJSON(logs: string[]) {
  const jsonContent = "data:application/json;charset=utf-8," + encodeURIComponent(JSON.stringify(logs, null, 2));
  const link = document.createElement("a");
  link.setAttribute("href", jsonContent);
  link.setAttribute("download", "logs.json");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function NeuralLog({ endpoint = "ws://localhost:8001/logs/ws" }: { endpoint?: string }) {
  const [logs, setLogs] = useState<string[]>([]);
  const [filter, setFilter] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let fallback = false;
    try {
      wsRef.current = new WebSocket(endpoint);
      wsRef.current.onmessage = (event) => {
        setLogs((prev) => [...prev.slice(-99), event.data]);
      };
      wsRef.current.onerror = () => {
        fallback = true;
        setLogs(["Error connecting to log stream. Fetching from API..."]);
        fetch("/api/logs")
          .then((res) => res.json())
          .then((data) => setLogs(data.logs || []));
      };
    } catch {
      fallback = true;
      setLogs(["WebSocket not supported. Fetching from API..."]);
      fetch("/api/logs")
        .then((res) => res.json())
        .then((data) => setLogs(data.logs || []));
    }
    return () => {
      wsRef.current?.close();
    };
  }, [endpoint]);

  const filteredLogs = logs.filter(l => l.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div className="bg-card p-4 rounded-lg border border-border h-64 flex flex-col">
      <div className="flex gap-2 mb-2">
        <input
          type="text"
          placeholder="Filter logs..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="px-2 py-1 rounded border text-xs w-1/2"
        />
        <button
          className="px-2 py-1 rounded border bg-primary text-primary-foreground text-xs"
          onClick={() => exportCSV(filteredLogs)}
        >
          Export CSV
        </button>
        <button
          className="px-2 py-1 rounded border bg-secondary text-secondary-foreground text-xs"
          onClick={() => exportTXT(filteredLogs)}
        >
          Export TXT
        </button>
        <button
          className="px-2 py-1 rounded border bg-accent text-accent-foreground text-xs"
          onClick={() => exportJSON(filteredLogs)}
        >
          Export JSON
        </button>
      </div>
      <div className="overflow-y-auto font-mono text-xs text-accent-foreground flex-1">
        {filteredLogs.length === 0 ? (
          <Skeleton className="h-24 w-full" />
        ) : (
          <ul>
            {filteredLogs.map((log, idx) => (
              <li key={idx} className="whitespace-pre-wrap">{log}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
