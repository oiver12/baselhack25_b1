"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, Share2, Check, FileText } from "lucide-react";
import { useState, useEffect } from "react";
import Link from "next/link";

interface DashboardHeaderProps {
  questionId: string;
}

export default function DashboardHeader({ questionId }: DashboardHeaderProps) {
  const router = useRouter();
  const [questionText, setQuestionText] = useState<string>("");
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchQuestion() {
      try {
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
        const response = await fetch(`${backendUrl}/api/question_and_ids`);
        if (response.ok) {
          const data = await response.json();
          // Find the question with matching question_id
          const questionInfo = data.find((item: { question_id: string; question: string }) => 
            item.question_id === questionId
          );
          if (questionInfo) {
            setQuestionText(questionInfo.question || "");
          }
        }
      } catch (error) {
        console.error("Failed to fetch question:", error);
      } finally {
        setIsLoading(false);
      }
    }

    if (questionId) {
      fetchQuestion();
    }
  }, [questionId]);

  const handleShare = async () => {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  return (
    <header 
      className="sticky top-0 z-50 w-full border-b backdrop-blur-xl"
      style={{
        backgroundColor: "var(--theme-bg-primary)",
        borderColor: "var(--theme-bg-tertiary)",
        opacity: 0.95,
      }}
    >
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between gap-4">
          {/* Back button and question */}
          <div className="flex items-center gap-4 flex-1 min-w-0">
            <button
              onClick={() => router.push("/")}
              className="flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95"
              style={{
                backgroundColor: "var(--theme-bg-secondary)",
                color: "var(--theme-fg-primary)",
              }}
              aria-label="Back to home"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            
            <div className="flex-1 min-w-0">
              {isLoading ? (
                <div 
                  className="h-5 w-48 rounded animate-pulse"
                  style={{ backgroundColor: "var(--theme-bg-tertiary)" }}
                />
              ) : (
                <h1 
                  className="text-sm md:text-base font-semibold truncate"
                  style={{ color: "var(--theme-fg-primary)" }}
                  title={questionText}
                >
                  {questionText || "Loading..."}
                </h1>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {/* View Report button */}
            <Link
              href={`/dashboard/${questionId}/report`}
              className="flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 font-medium text-sm"
              style={{
                backgroundColor: "var(--theme-bg-secondary)",
                color: "var(--theme-fg-primary)",
              }}
              aria-label="View Report"
            >
              <FileText className="w-4 h-4" />
              <span className="hidden sm:inline">Report</span>
            </Link>

            {/* Share button */}
            <button
              onClick={handleShare}
              className="flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 font-medium text-sm"
              style={{
                backgroundColor: copied 
                  ? "var(--theme-accent-green)" 
                  : "var(--theme-bg-secondary)",
                color: copied 
                  ? "white" 
                  : "var(--theme-fg-primary)",
              }}
              aria-label={copied ? "Copied!" : "Share"}
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Share2 className="w-4 h-4" />
                  <span className="hidden sm:inline">Share</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

