import { NextResponse } from "next/server";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ questionId: string }> }
) {
  try {
    const { questionId } = await params;

    if (!questionId) {
      return NextResponse.json(
        { error: "Question ID is required" },
        { status: 400 }
      );
    }

    // Call Python backend API - matches baselhack25_backend/app/api/routes/dashboard.py
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const backendEndpoint = `${backendUrl}/api/dashboard/${questionId}`;
    
    console.log(`Calling Python backend dashboard at ${backendEndpoint}`);
    
    const response = await fetch(backendEndpoint, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: "Question not found" },
          { status: 404 }
        );
      }
      const errorText = await response.text();
      console.error(`Python backend error (${response.status}):`, errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.statusText}`, details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log("Python backend dashboard response:", data);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error calling Python backend dashboard:", error);
    return NextResponse.json(
      { error: "Failed to fetch dashboard data", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

