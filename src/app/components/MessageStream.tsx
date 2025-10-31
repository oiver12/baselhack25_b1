"use client";

import { useEffect, useRef, useState } from "react";
import type { Message } from "@/lib/types";

interface StreamMessage extends Message {
  id: string;
  timestamp: number;
  expiresAt: number;
}

const MESSAGE_TTL = 45_000; // 45 seconds
const MAX_MESSAGES = 14;

export default function MessageStream() {
  const [messages, setMessages] = useState<StreamMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const eventSource = new EventSource("/api/webhook");

    eventSource.onopen = () => {
      setIsConnected(true);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "connected") {
          return;
        }

        if (data.type === "message") {
          const now = Date.now();
          const newMessage: StreamMessage = {
            id: `${now}-${Math.random().toString(16).slice(2)}`,
            user: data.user,
            message: data.message,
            timestamp: now,
            expiresAt: now + MESSAGE_TTL,
          };

          setMessages((prev) => {
            const filtered = prev.filter((message) => message.expiresAt > now);
            const updated = [...filtered, newMessage];
            if (updated.length > MAX_MESSAGES) {
              return updated.slice(updated.length - MAX_MESSAGES);
            }
            return updated;
          });
        }
      } catch (err) {
        console.error("Error parsing message:", err);
      }
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  useEffect(() => {
    const cleanup = setInterval(() => {
      const now = Date.now();
      setMessages((prev) => prev.filter((message) => message.expiresAt > now));
    }, 5_000);

    return () => {
      clearInterval(cleanup);
    };
  }, []);

  useEffect(() => {
    // Auto-scroll to the bottom to show the newest message
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-3xl border border-white/50 bg-white/70 shadow-xl shadow-blue-200/40 backdrop-blur-xl dark:border-white/10 dark:bg-white/10 dark:shadow-blue-900/15">
      <div className="rounded-t-3xl border-b border-white/50 bg-gradient-to-r from-white/80 via-white/60 to-white/80 px-5 py-4 dark:border-white/10 dark:from-white/10 dark:via-white/5 dark:to-white/10">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold tracking-tight text-slate-800 dark:text-slate-100">
            Live Feed
          </h2>
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
            <span
              className={`flex h-2.5 w-2.5 items-center justify-center rounded-full ${
                isConnected
                  ? "bg-emerald-400 shadow-[0_0_12px_rgba(74,222,128,0.7)]"
                  : "bg-rose-500 shadow-[0_0_10px_rgba(244,114,182,0.6)]"
              }`}
            />
            {isConnected ? "Connected" : "Disconnected"}
          </div>
        </div>
      </div>
      <div
        ref={messagesContainerRef}
        className="flex-1 space-y-3 overflow-y-auto px-5 py-6"
      >
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center rounded-2xl border border-dashed border-slate-200/60 bg-white/60 p-6 text-sm text-slate-400 dark:border-white/10 dark:bg-white/5 dark:text-slate-500">
            Waiting for fresh ideas...
          </div>
        ) : (
          messages.map((message) => (
            <article
              key={message.id}
              className="group relative overflow-hidden rounded-2xl border border-white/60 bg-white/90 p-4 shadow-lg shadow-blue-100/40 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-2xl dark:border-white/10 dark:bg-white/10 dark:shadow-blue-900/20"
            >
              <div className="absolute right-4 top-4 text-[10px] uppercase tracking-[0.32em] text-slate-400/70">
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </div>
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-sm font-semibold text-white shadow-md">
                  {message.user[0]?.toUpperCase()}
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                    {message.user}
                  </div>
                  <p className="mt-1 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
                    {message.message}
                  </p>
                </div>
              </div>
              <div className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                <div className="absolute inset-[-30%] bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/15 blur-3xl" />
              </div>
            </article>
          ))
        )}
      </div>
    </div>
  );
}
