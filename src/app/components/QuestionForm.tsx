"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, ArrowRight, Loader2 } from "lucide-react";

export default function QuestionForm() {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFocused, setIsFocused] = useState(false);
  const router = useRouter();

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] px-4 py-12">
      <div className="w-full max-w-3xl">
        {/* Hero Section */}
        <div className="text-center mb-12 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4 shadow-lg backdrop-blur-sm"
            style={{
              background: "linear-gradient(135deg, var(--theme-bubble-primary-from), var(--theme-bubble-primary-to))",
            }}
          >
            <Sparkles className="w-10 h-10 text-white" strokeWidth={2.5} />
          </div>
          <h1 
            className="text-5xl md:text-6xl font-bold tracking-tight leading-tight"
            style={{ color: "var(--theme-fg-primary)" }}
          >
            Start a New
            <span 
              className="block bg-gradient-to-r bg-clip-text text-transparent mt-2"
              style={{
                backgroundImage: "linear-gradient(to right, var(--theme-bubble-primary-from), var(--theme-bubble-primary-to), var(--theme-accent-pink))",
              }}
            >
              Discussion
            </span>
          </h1>
          <p 
            className="text-xl md:text-2xl max-w-2xl mx-auto leading-relaxed"
            style={{ color: "var(--theme-fg-secondary)" }}
          >
            Ask a question and watch real-time consensus emerge through intelligent conversation mapping
          </p>
        </div>

        {/* Form Card */}
        <div 
          className="relative backdrop-blur-xl rounded-3xl p-8 md:p-12 shadow-2xl border transition-all duration-500"
          style={{
            backgroundColor: "var(--theme-bg-primary)",
            borderColor: "var(--theme-bg-tertiary)",
            boxShadow: isFocused 
              ? "0 25px 50px -12px rgba(99, 102, 241, 0.15), 0 0 0 1px rgba(99, 102, 241, 0.05)" 
              : "0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02)",
          }}
        >
          {/* Ambient glow effect */}
          <div 
            className="absolute inset-0 rounded-3xl opacity-0 transition-opacity duration-500 pointer-events-none"
            style={{
              background: "radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.08), transparent 70%)",
              opacity: isFocused ? 1 : 0,
            }}
          />

          <form onSubmit={(e) => e.preventDefault()} className="relative space-y-8">
            <div className="space-y-3">
              <label
                htmlFor="question"
                className="block text-sm font-semibold tracking-wide uppercase"
                style={{ color: "var(--theme-fg-secondary)", letterSpacing: "0.1em" }}
              >
                Your Question
              </label>
              <div className="relative">
                <textarea
                  id="question"
                  value={question}
                  onChange={(e) => {
                    setQuestion(e.target.value);
                    setError(null);
                  }}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  placeholder="e.g., How should we improve the city's public transportation system to better serve all residents?"
                  rows={6}
                  className="w-full px-6 py-4 rounded-xl border-2 resize-none transition-all duration-300 font-medium placeholder:font-normal"
                  style={{
                    backgroundColor: "var(--theme-bg-secondary)",
                    borderColor: isFocused ? "var(--theme-accent-indigo)" : "var(--theme-bg-tertiary)",
                    color: "var(--theme-fg-primary)",
                    boxShadow: isFocused 
                      ? "0 0 0 4px rgba(99, 102, 241, 0.08), 0 4px 6px -1px rgba(0, 0, 0, 0.05)" 
                      : "0 1px 3px 0 rgba(0, 0, 0, 0.05)",
                  }}
                  disabled={isLoading}
                />
                <div 
                  className="absolute bottom-4 right-4 text-xs font-medium opacity-60 transition-opacity"
                  style={{ color: "var(--theme-fg-tertiary)" }}
                >
                  {question.length} / 500
                </div>
              </div>
            </div>

            {error && (
              <div
                className="flex items-start gap-3 px-4 py-3.5 rounded-xl backdrop-blur-sm animate-in fade-in slide-in-from-top-2"
                style={{
                  backgroundColor: "rgba(239, 68, 68, 0.08)",
                  border: "1px solid rgba(239, 68, 68, 0.2)",
                }}
              >
                <div className="flex-shrink-0 mt-0.5">
                  <div 
                    className="w-5 h-5 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: "rgba(239, 68, 68, 0.15)" }}
                  >
                    <span className="text-red-500 text-xs font-bold">!</span>
                  </div>
                </div>
                <p 
                  className="text-sm font-medium flex-1"
                  style={{ color: "var(--theme-accent-red)" }}
                >
                  {error}
                </p>
              </div>
            )}

            <button
              type="button"
              disabled={isLoading || !question.trim()}
              onClick={async (e) => {
                e.preventDefault();
                if (!question.trim()) {
                  setError("Please enter a question");
                  return;
                }
                setIsLoading(true);
                setError(null);
                try {
                  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
                  const response = await fetch(`${backendUrl}/api/questions`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: question.trim() }),
                  });
                  if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || errorData.detail || `Failed: ${response.statusText}`);
                  }
                  const data = await response.json();
                  if (data.question_id) {
                    router.push(`/dashboard/${data.question_id}`);
                  } else {
                    throw new Error("No question_id in response");
                  }
                } catch (err) {
                  setError(err instanceof Error ? err.message : "Failed to create question");
                  setIsLoading(false);
                }
              }}
              className="group relative w-full py-4 px-8 rounded-xl font-semibold text-white transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
              style={{
                background: isLoading || !question.trim()
                  ? "linear-gradient(to right, #94a3b8, #94a3b8)"
                  : "linear-gradient(135deg, var(--theme-bubble-primary-from), var(--theme-bubble-primary-to))",
                boxShadow: isLoading || !question.trim()
                  ? "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
                  : "0 10px 25px -5px rgba(99, 102, 241, 0.4), 0 0 0 1px rgba(99, 102, 241, 0.2)",
              }}
            >
              {/* Button shine effect */}
              {!isLoading && question.trim() && (
                <div 
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                  style={{
                    background: "linear-gradient(135deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%)",
                    backgroundSize: "200% 100%",
                    animation: "shimmer 3s infinite",
                  }}
                />
              )}
              
              <span className="relative flex items-center justify-center gap-3">
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Creating Discussion...</span>
                  </>
                ) : (
                  <>
                    <span>Start Discussion</span>
                    <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </span>
            </button>
          </form>
        </div>

        {/* Feature hints */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          {[
            { icon: "💬", text: "Real-time consensus" },
            { icon: "🎯", text: "Visual insights" },
            { icon: "⚡", text: "Instant feedback" },
          ].map((feature, i) => (
            <div 
              key={i}
              className="flex flex-col items-center gap-2 px-4 py-3 rounded-xl backdrop-blur-sm transition-all duration-300 hover:scale-105"
              style={{
                backgroundColor: "var(--theme-bg-secondary)",
              }}
            >
              <span className="text-2xl">{feature.icon}</span>
              <span 
                className="text-sm font-medium"
                style={{ color: "var(--theme-fg-secondary)" }}
              >
                {feature.text}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

