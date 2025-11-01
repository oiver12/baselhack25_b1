import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { question } = body;

    if (!question || typeof question !== "string" || question.trim().length === 0) {
      return NextResponse.json(
        { error: "Question is required and must be a non-empty string" },
        { status: 400 }
      );
    }

    // Extract key query parameter from request URL
    const url = new URL(request.url);
    const key = url.searchParams.get("key");

    // Call Python backend API - matches baselhack25_backend/app/api/routes/questions.py
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    // Forward key query parameter to backend
    const backendEndpoint = `${backendUrl}/api/questions${key ? `?key=${encodeURIComponent(key)}` : ''}`;
    
    console.log(`Calling Python backend at ${backendEndpoint} with question:`, question.trim());
    
    const response = await fetch(backendEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: question.trim() }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Python backend error (${response.status}):`, errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.statusText}`, details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log("Python backend response:", data);
    
    // Verify response structure matches QuestionResponse schema
    if (!data.question_id) {
      console.error("Invalid response from Python backend:", data);
      return NextResponse.json(
        { error: "Invalid response from backend: missing question_id" },
        { status: 500 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Error calling Python backend:", error);
    return NextResponse.json(
      { error: "Failed to create question", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

