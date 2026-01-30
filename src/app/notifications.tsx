"use client";
"use client";
import { createContext, useContext, useState } from "react";

const NotificationContext = createContext<any>(null);

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<string[]>([]);
  const notify = (msg: string) => setMessages((msgs) => [...msgs, msg]);
  const remove = (i: number) => setMessages((msgs) => msgs.filter((_, idx) => idx !== i));
  return (
    <NotificationContext.Provider value={notify}>
      {children}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
        {messages.map((msg, i) => (
          <div key={i} className="bg-emerald-700 text-white px-4 py-2 rounded shadow-lg animate-fade-in">
            {msg}
            <button className="ml-2 text-xs" onClick={() => remove(i)}>
              ×
            </button>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
}

export function useNotify() {
  return useContext(NotificationContext);
}
