"use client";

import { useEffect, useState } from "react";
import type { Message } from "@/lib/types";

interface ToastMessage extends Message {
  id: string;
  timestamp: number;
  isExiting?: boolean;
  groupId?: number; // Group ID for messages that appear at the same time
}

const MIN_TOAST_DURATION = 6000; // 5 seconds
const MAX_TOAST_DURATION = 8000; // 8 seconds
const MAX_VISIBLE_TOASTS = 5;
const EXIT_ANIMATION_DURATION = 300; // 300ms for fade out
const SIMULTANEOUS_THRESHOLD = 500; // Messages within 500ms are considered simultaneous

export default function MessageStream() {
  const [messages, setMessages] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const eventSource = new EventSource("/api/webhook");

    eventSource.onopen = () => {
      // Connection status not needed for toasts
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "connected") {
          return;
        }

        if (data.type === "message") {
          const now = Date.now();
          const messageId = `${now}-${Math.random().toString(16).slice(2)}`;

          setMessages((prev) => {
            // Check if this message arrives at the same time as the last one
            const lastMessage = prev[prev.length - 1];
            const isSimultaneous =
              lastMessage &&
              (now - lastMessage.timestamp) < SIMULTANEOUS_THRESHOLD;

            // Use the same group ID if simultaneous, otherwise get next group ID
            let groupId: number;
            if (isSimultaneous && lastMessage.groupId !== undefined) {
              groupId = lastMessage.groupId;
            } else {
              // Get the highest group ID from existing messages and add 1
              const maxGroupId = prev.reduce((max, msg) =>
                Math.max(max, msg.groupId ?? -1), -1
              );
              groupId = maxGroupId + 1;
            }

            const newMessage: ToastMessage = {
              id: messageId,
              user: data.user,
              message: data.message,
              timestamp: now,
              isExiting: false,
              groupId,
            };

            // Add new message at the end (will appear at top of stack)
            const updated = [...prev, newMessage];
            // Keep only the most recent messages
            return updated.slice(-MAX_VISIBLE_TOASTS);
          });

          // Auto-dismiss after duration
          setTimeout(() => {
            setMessages((prev) => {
              // Mark as exiting first
              return prev.map((msg) =>
                msg.id === messageId ? { ...msg, isExiting: true } : msg,
              );
            });

            // Remove after exit animation
            setTimeout(() => {
              setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
            }, EXIT_ANIMATION_DURATION);
          }, MAX_TOAST_DURATION);
        }
      } catch (err) {
        console.error("Error parsing message:", err);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  if (messages.length === 0) {
    return null;
  }

  // Reverse messages so newest appear on top
  const reversedMessages = messages.slice().reverse();

  return (
    <div className="fixed top-4 right-4 z-50 pointer-events-none">
      <div className="relative">
        {reversedMessages.map((message, index) => {
        // Index 0 is the newest message (appears at top)
        const reverseIndex = index;

        // Calculate stack offset - messages stack downward
        // Newest message has no offset (stays at top)
        let stackOffset = 0;
        for (let i = 0; i < index; i++) {
          const msgAbove = reversedMessages[i];
          const msgBelow = reversedMessages[i + 1];
          // Spacing between consecutive messages
          if (msgAbove.groupId === msgBelow.groupId) {
            stackOffset += 20;
          } else {
            stackOffset += 30;
          }
        }

        const stackScale = 1 - reverseIndex * 0.05;
        const stackOpacity = 1 - reverseIndex * 0.15;

        return (
          <div
            key={message.id}
            className={`pointer-events-auto transition-all duration-300 ${message.isExiting ? "fade-out" : "slide-in-from-right fade-in"
              }`}
            style={{
              position: 'absolute',
              top: `${stackOffset}px`,
              right: 0,
              transform: message.isExiting
                ? undefined
                : `scale(${stackScale})`,
              zIndex: 1000 + (reversedMessages.length - reverseIndex),
              opacity: message.isExiting ? undefined : stackOpacity,
            }}
          >
            <article className="group relative overflow-hidden rounded-2xl border border-white/20 bg-white/20 backdrop-blur-2xl p-4 shadow-2xl shadow-blue-100/40 transition-all duration-300 hover:shadow-blue-200/60 dark:border-white/10 dark:bg-gray-900/20 dark:shadow-blue-900/20 max-w-sm">
              <div className="flex items-center gap-0">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-sm font-semibold text-white shadow-md">
                  {message.user[0]?.toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline justify-between gap-2">
                    <div className="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate leading-tight">
                      {message.user}
                    </div>
                    <div className="text-sm font-regular text-slate-800 dark:text-slate-100 truncate leading-tight">
                      {new Date(message.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                  </div>
                  <p className="mt-1.5 text-sm leading-relaxed text-slate-600 dark:text-slate-300 line-clamp-3">
                    {message.message}
                  </p>
                </div>
              </div>
              <div className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                <div className="absolute inset-[-30%] bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/15 blur-3xl" />
              </div>
            </article>
          </div>
        );
      })}
      </div>
    </div>
  );
}
