import { type NextRequest, NextResponse } from "next/server";
import type { Message } from "@/lib/types";

// Mock users and messages for webhook simulation
const mockUsers = [
  { name: "Alice", profilePicUrl: "https://i.pravatar.cc/150?img=1" },
  { name: "Bob", profilePicUrl: "https://i.pravatar.cc/150?img=12" },
  { name: "Charlie", profilePicUrl: "https://i.pravatar.cc/150?img=13" },
  { name: "Diana", profilePicUrl: "https://i.pravatar.cc/150?img=5" },
  { name: "Eve", profilePicUrl: "https://i.pravatar.cc/150?img=9" },
  { name: "Frank", profilePicUrl: "https://i.pravatar.cc/150?img=11" },
];
const mockMessages = [
  "Hey everyone! Great progress so far.",
  "What do you think about this approach?",
  "Let's discuss this in the next meeting.",
  "I've completed the initial setup.",
  "Can someone review this?",
  "That's a great idea!",
  "Should we consider another option?",
  "The deadline is approaching.",
  "Let's prioritize this feature.",
  "Thanks for the feedback!",
];

function getRandomElement<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

function generateRandomMessage(): Message {
  const user = getRandomElement(mockUsers);
  return {
    user: user.name,
    message: getRandomElement(mockMessages),
    profilePicUrl: user.profilePicUrl,
  };
}

// POST handler for webhook (for Discord integration later)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    // In the future, this will handle Discord webhook messages
    // For now, just acknowledge receipt
    return NextResponse.json({ received: true, data: body });
  } catch {
    return NextResponse.json(
      { error: "Invalid request body" },
      { status: 400 },
    );
  }
}

// GET handler that streams messages every 5 seconds using Server-Sent Events
export async function GET(request: NextRequest) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      // Send initial connection message
      const initialData = JSON.stringify({
        type: "connected",
        message: "Webhook stream started",
      });
      controller.enqueue(encoder.encode(`data: ${initialData}\n\n`));

      // Set up interval to send messages every 5 seconds
      const intervalId = setInterval(() => {
        const message = generateRandomMessage();
        const data = JSON.stringify({
          type: "message",
          ...message,
        });
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      }, 5000);

      // Clean up on close
      const cleanup = () => {
        clearInterval(intervalId);
        controller.close();
      };

      // Handle client disconnect
      request.signal.addEventListener("abort", () => {
        cleanup();
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
