"use client";

import { useEffect, useState } from "react";
import type { Message } from "@/lib/types";

interface ToastMessage extends Message {
  id: string;
  timestamp: number;
  isExiting?: boolean;
  groupId?: number; // Group ID for messages that appear at the same time
}

const MAX_TOAST_DURATION = 8000; // 8 seconds
const MAX_VISIBLE_TOASTS = 5;
const EXIT_ANIMATION_DURATION = 300; // 300ms for fade out
const SIMULTANEOUS_THRESHOLD = 500; // Messages within 500ms are considered simultaneous
const MESSAGE_DELAY = 0; // Delay in ms before displaying messages, even when pending/connecting

interface MessageStreamProps {
  uuid: string;
}

export default function MessageStream({ uuid }: MessageStreamProps) {
  const [messages, setMessages] = useState<ToastMessage[]>([]);

  useEffect(() => {
    // Get backend URL from environment variable or use default
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    
    // Convert HTTP/HTTPS URL to WebSocket URL
    const wsBaseUrl = backendUrl
      .replace(/^http:/, "ws:")
      .replace(/^https:/, "wss:");
    
    // Construct WebSocket URL: ws://localhost:8000/ws/{uuid}
    // Backend route is registered with prefix "/ws" and endpoint "/{question_id}"
    const wsUrl = `${wsBaseUrl}/ws/${uuid}`;
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    let isManualClose = false;
    const maxReconnectDelay = 30000; // 30 seconds max delay
    let reconnectAttempts = 0;
    
    // Message queue for messages received while websocket is pending/connecting
    interface QueuedMessage {
      data: any;
      receivedAt: number;
    }
    const messageQueue: QueuedMessage[] = [];
    
    // Function to process a message with delay
    const processMessage = (data: any, receivedAt: number) => {
      // Always apply MESSAGE_DELAY before displaying, even if message was queued
      // This ensures consistent delay behavior regardless of connection state
      const delay = MESSAGE_DELAY;
      
      setTimeout(() => {
        if (data.type === "message") {
          const now = Date.now();
          const messageId = `${now}-${Math.random().toString(16).slice(2)}`;

          setMessages((prev) => {
            // Check if this message arrives at the same time as the last one
            const lastMessage = prev[prev.length - 1];
            const isSimultaneous =
              lastMessage &&
              now - lastMessage.timestamp < SIMULTANEOUS_THRESHOLD;

            // Use the same group ID if simultaneous, otherwise get next group ID
            let groupId: number;
            if (isSimultaneous && lastMessage.groupId !== undefined) {
              groupId = lastMessage.groupId;
            } else {
              // Get the highest group ID from existing messages and add 1
              const maxGroupId = prev.reduce(
                (max, msg) => Math.max(max, msg.groupId ?? -1),
                -1,
              );
              groupId = maxGroupId + 1;
            }

            const newMessage: ToastMessage = {
              id: messageId,
              user: data.user,
              message: data.message,
              profilePicUrl: data.profilePicUrl,
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
      }, delay);
    };
    
    // Function to process queued messages when connection is ready
    const processQueue = () => {
      while (messageQueue.length > 0) {
        const queued = messageQueue.shift();
        if (queued) {
          processMessage(queued.data, queued.receivedAt);
        }
      }
    };

    const connect = () => {
      if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
        return; // Already connecting or connected
      }

      try {
        ws = new WebSocket(wsUrl);
        console.log(`Connecting to WebSocket: ${wsUrl}`);

        ws.onopen = () => {
          console.log("WebSocket connected successfully");
          reconnectAttempts = 0; // Reset reconnect attempts on successful connection
          // Process any messages that were queued while connecting
          processQueue();
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            const receivedAt = Date.now();

            if (data.type === "connected") {
              console.log("WebSocket connection confirmed:", data.message);
              return;
            }

            if (data.type === "initial") {
              console.log(`Initial state: ${data.message_count} messages`);
              return;
            }

            // Check if websocket is in a pending/connecting state or not fully open
            const isPending = !ws || ws.readyState !== WebSocket.OPEN;
            
            if (data.type === "message") {
              if (isPending) {
                // Queue the message if websocket is not fully open
                console.log("WebSocket pending, queueing message");
                messageQueue.push({ data, receivedAt });
              } else {
                // Process immediately with delay if connection is open
                processMessage(data, receivedAt);
              }
            }
          } catch (err) {
            console.error("Error parsing WebSocket message:", err);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          console.error("WebSocket URL was:", wsUrl);
        };

        ws.onclose = (event) => {
          console.log("WebSocket closed:", event.code, event.reason);
          
          if (isManualClose) {
            return; // Don't reconnect if manually closed
          }

          if (event.code !== 1000) {
            console.warn(`WebSocket closed unexpectedly with code ${event.code}: ${event.reason || "No reason provided"}`);
            
            // Attempt to reconnect with exponential backoff
            reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts - 1), maxReconnectDelay);
            console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts})...`);
            
            reconnectTimeout = setTimeout(() => {
              connect();
            }, delay);
          }
        };
      } catch (error) {
        console.error("Failed to create WebSocket connection:", error);
      }
    };

    // Initial connection
    connect();

    return () => {
      isManualClose = true;
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws) {
        if (
          ws.readyState === WebSocket.OPEN ||
          ws.readyState === WebSocket.CONNECTING
        ) {
          ws.close();
        }
      }
    };
  }, [uuid]);

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
              className={`pointer-events-auto transition-all duration-300 ${
                message.isExiting ? "fade-out" : "slide-in-from-right fade-in"
              }`}
              style={{
                position: "absolute",
                top: `${stackOffset}px`,
                right: 0,
                transform: message.isExiting
                  ? undefined
                  : `scale(${stackScale})`,
                zIndex: 1000 + (reversedMessages.length - reverseIndex),
                opacity: message.isExiting ? undefined : stackOpacity,
              }}
            >
              <article 
                className="group relative overflow-hidden rounded-2xl border backdrop-blur-xl p-5 shadow-2xl transition-all duration-300 w-80 md:w-96"
                style={{
                  borderColor: "rgba(255, 255, 255, 0.18)",
                  backgroundColor: "rgba(17, 24, 39, 0.6)",
                  boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.1)",
                }}
              >
                {/* Subtle gradient overlay */}
                <div 
                  className="absolute inset-0 opacity-50 pointer-events-none"
                  style={{
                    background: "linear-gradient(135deg, rgba(99, 102, 241, 0.03), rgba(168, 85, 247, 0.03), transparent)",
                  }}
                />
                
                <div className="relative flex items-start gap-3">
                  <div className="relative shrink-0">
                    {message.profilePicUrl ? (
                      <img
                        src={message.profilePicUrl}
                        alt={message.user}
                        className="h-12 w-12 rounded-xl object-cover shadow-lg ring-2 ring-white/50"
                      />
                    ) : (
                      <div 
                        className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br text-base font-bold text-white shadow-lg ring-2 ring-white/50"
                        style={{
                          background: `linear-gradient(135deg, var(--theme-accent-blue), var(--theme-accent-purple))`,
                        }}
                      >
                        {message.user[0]?.toUpperCase()}
                      </div>
                    )}
                    {/* Online indicator */}
                    <div 
                      className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-white"
                      style={{ backgroundColor: "var(--theme-accent-green)" }}
                    />
                  </div>
                  
                  <div className="flex-1 min-w-0 pt-0.5">
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <div 
                        className="text-sm font-bold truncate"
                        style={{ color: "var(--theme-message-text)" }}
                      >
                        {message.user}
                      </div>
                      <div 
                        className="text-xs font-medium shrink-0 opacity-70"
                        style={{ color: "var(--theme-message-text-secondary)" }}
                      >
                        {new Date(message.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                    </div>
                    <p 
                      className="text-sm leading-relaxed line-clamp-3 font-medium"
                      style={{ color: "var(--theme-message-text-secondary)" }}
                    >
                      {message.message}
                    </p>
                  </div>
                </div>
                
                {/* Enhanced hover glow */}
                <div className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-100 rounded-2xl">
                  <div 
                    className="absolute inset-[-20%] bg-gradient-to-br via-transparent blur-2xl rounded-full"
                    style={{
                      background: `linear-gradient(135deg, var(--theme-accent-blue), var(--theme-accent-purple))`,
                      opacity: 0.15,
                    }}
                  />
                </div>
              </article>
            </div>
          );
        })}
      </div>
    </div>
  );
}
