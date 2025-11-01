"use client";

import { useMemo, useRef, useEffect, useState } from "react";
import type { SuggestionsResponse, SuggestionOpinion } from "@/lib/types";
import { 
  Users, 
  MessageSquare, 
  TrendingUp, 
  BarChart3,
  Star,
  TrendingDown,
  Circle
} from "lucide-react";

interface AnalyticsDashboardProps {
  suggestions: SuggestionsResponse;
  questionText?: string;
  containerRef?: React.RefObject<HTMLDivElement | null>;
}

interface AnalyticsData {
  totalSuggestions: number;
  totalParticipants: number;
  totalOpinions: number;
  averageSize: number;
  totalPros: number;
  totalCons: number;
  classificationBreakdown: {
    sophisticated: number;
    simple: number;
    neutral: number;
  };
  sizeDistribution: {
    large: number; // > 0.7
    medium: number; // 0.3 - 0.7
    small: number; // < 0.3
  };
}

export default function AnalyticsDashboard({ suggestions, questionText = "How should we improve the city's public transportation system?", containerRef }: AnalyticsDashboardProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [panelDimensions, setPanelDimensions] = useState({ width: 0, height: 0, x: 0, y: 0 });

  // Update panel dimensions for exclusion zone
  useEffect(() => {
    if (!panelRef.current || !containerRef?.current) return;

    const updateDimensions = () => {
      const panelRect = panelRef.current?.getBoundingClientRect();
      const containerRect = containerRef.current?.getBoundingClientRect();
      
      if (panelRect && containerRect) {
        setPanelDimensions({
          width: panelRect.width,
          height: panelRect.height,
          x: panelRect.left - containerRect.left,
          y: panelRect.top - containerRect.top,
        });
      }
    };

    updateDimensions();
    const resizeObserver = new ResizeObserver(updateDimensions);
    resizeObserver.observe(panelRef.current);
    resizeObserver.observe(containerRef.current);

    return () => resizeObserver.disconnect();
  }, [containerRef]);

  // Expose dimensions for parent component
  useEffect(() => {
    if (containerRef?.current) {
      // Store in a data attribute that the physics simulation can read
      const container = containerRef.current;
      container.setAttribute('data-analytics-exclusion', JSON.stringify(panelDimensions));
    }
  }, [panelDimensions, containerRef]);

  const analytics = useMemo<AnalyticsData>(() => {
    const allOpinions: SuggestionOpinion[] = suggestions.flatMap(
      (s) => s.peopleOpinions
    );
    
    const uniqueParticipants = new Set(
      allOpinions.map((o) => o.name)
    );

    const classificationBreakdown = {
      sophisticated: allOpinions.filter((o) => o.classification === "sophisticated").length,
      simple: allOpinions.filter((o) => o.classification === "simple").length,
      neutral: allOpinions.filter((o) => o.classification === "neutral").length,
    };

    const sizes = suggestions.map((s) => s.size);
    const averageSize = sizes.length > 0 
      ? sizes.reduce((a, b) => a + b, 0) / sizes.length 
      : 0;

    const sizeDistribution = {
      large: suggestions.filter((s) => s.size > 0.7).length,
      medium: suggestions.filter((s) => s.size >= 0.3 && s.size <= 0.7).length,
      small: suggestions.filter((s) => s.size < 0.3).length,
    };

    return {
      totalSuggestions: suggestions.length,
      totalParticipants: uniqueParticipants.size,
      totalOpinions: allOpinions.length,
      averageSize,
      totalPros: suggestions.reduce((sum, s) => sum + s.pros.length, 0),
      totalCons: suggestions.reduce((sum, s) => sum + s.contra.length, 0),
      classificationBreakdown,
      sizeDistribution,
    };
  }, [suggestions]);

  if (suggestions.length === 0) {
    return null;
  }

  return (
    <div 
      ref={panelRef}
      className="absolute bottom-6 left-6 z-40 w-80 md:w-96 rounded-2xl shadow-2xl border backdrop-blur-xl"
      style={{
        backgroundColor: "var(--theme-bg-primary)",
        borderColor: "var(--theme-bg-tertiary)",
        boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)",
        opacity: 0.95,
      }}
    >
      {/* Blurred background overlay */}
      <div 
        className="absolute inset-0 rounded-2xl -z-10 backdrop-blur-2xl"
        style={{
          backgroundColor: "var(--theme-bg-primary)",
          opacity: 0.8,
        }}
      />
      
      {/* Header */}
      <div 
        className="p-5 border-b"
        style={{ borderColor: "var(--theme-bg-tertiary)" }}
      >
        <div className="flex items-center gap-2 mb-2">
          <BarChart3 
            className="w-5 h-5" 
            style={{ color: "var(--theme-accent-blue)" }}
          />
          <h2 
            className="text-lg font-bold"
            style={{ color: "var(--theme-fg-primary)" }}
          >
            Analytics
          </h2>
        </div>
        <p 
          className="text-sm line-clamp-2 mt-2"
          style={{ color: "var(--theme-fg-secondary)" }}
          title={questionText}
        >
          {questionText}
        </p>
      </div>

      {/* Content */}
      <div className="p-5 space-y-6 max-h-[calc(100vh-20rem)] overflow-y-auto">
            {/* Overview Stats */}
            <div className="grid grid-cols-2 gap-3">
              <div 
                className="p-4 rounded-xl"
                style={{ backgroundColor: "var(--theme-bg-secondary)" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <MessageSquare 
                    className="w-4 h-4" 
                    style={{ color: "var(--theme-accent-blue)" }}
                  />
                  <span 
                    className="text-xs font-medium uppercase tracking-wide"
                    style={{ color: "var(--theme-fg-tertiary)" }}
                  >
                    Suggestions
                  </span>
                </div>
                <div 
                  className="text-2xl font-bold"
                  style={{ color: "var(--theme-fg-primary)" }}
                >
                  {analytics.totalSuggestions}
                </div>
              </div>

              <div 
                className="p-4 rounded-xl"
                style={{ backgroundColor: "var(--theme-bg-secondary)" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Users 
                    className="w-4 h-4" 
                    style={{ color: "var(--theme-accent-green)" }}
                  />
                  <span 
                    className="text-xs font-medium uppercase tracking-wide"
                    style={{ color: "var(--theme-fg-tertiary)" }}
                  >
                    Participants
                  </span>
                </div>
                <div 
                  className="text-2xl font-bold"
                  style={{ color: "var(--theme-fg-primary)" }}
                >
                  {analytics.totalParticipants}
                </div>
              </div>

              <div 
                className="p-4 rounded-xl"
                style={{ backgroundColor: "var(--theme-bg-secondary)" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <MessageSquare 
                    className="w-4 h-4" 
                    style={{ color: "var(--theme-accent-purple)" }}
                  />
                  <span 
                    className="text-xs font-medium uppercase tracking-wide"
                    style={{ color: "var(--theme-fg-tertiary)" }}
                  >
                    Opinions
                  </span>
                </div>
                <div 
                  className="text-2xl font-bold"
                  style={{ color: "var(--theme-fg-primary)" }}
                >
                  {analytics.totalOpinions}
                </div>
              </div>

              <div 
                className="p-4 rounded-xl"
                style={{ backgroundColor: "var(--theme-bg-secondary)" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp 
                    className="w-4 h-4" 
                    style={{ color: "var(--theme-accent-pink)" }}
                  />
                  <span 
                    className="text-xs font-medium uppercase tracking-wide"
                    style={{ color: "var(--theme-fg-tertiary)" }}
                  >
                    Avg Size
                  </span>
                </div>
                <div 
                  className="text-2xl font-bold"
                  style={{ color: "var(--theme-fg-primary)" }}
                >
                  {Math.round(analytics.averageSize * 100)}%
                </div>
              </div>
            </div>

            {/* Pros & Cons */}
            <div className="grid grid-cols-2 gap-3">
              <div 
                className="p-4 rounded-xl"
                style={{ backgroundColor: "var(--theme-bg-secondary)" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Circle 
                    className="w-3 h-3 fill-current" 
                    style={{ color: "var(--theme-accent-green)" }}
                  />
                  <span 
                    className="text-xs font-medium uppercase tracking-wide"
                    style={{ color: "var(--theme-fg-tertiary)" }}
                  >
                    Pros
                  </span>
                </div>
                <div 
                  className="text-xl font-bold"
                  style={{ color: "var(--theme-accent-green)" }}
                >
                  {analytics.totalPros}
                </div>
              </div>

              <div 
                className="p-4 rounded-xl"
                style={{ backgroundColor: "var(--theme-bg-secondary)" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Circle 
                    className="w-3 h-3 fill-current" 
                    style={{ color: "var(--theme-accent-red)" }}
                  />
                  <span 
                    className="text-xs font-medium uppercase tracking-wide"
                    style={{ color: "var(--theme-fg-tertiary)" }}
                  >
                    Cons
                  </span>
                </div>
                <div 
                  className="text-xl font-bold"
                  style={{ color: "var(--theme-accent-red)" }}
                >
                  {analytics.totalCons}
                </div>
              </div>
            </div>

            {/* Classification Breakdown */}
            <div>
              <h3 
                className="text-sm font-semibold mb-3"
                style={{ color: "var(--theme-fg-secondary)" }}
              >
                Opinion Types
              </h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Star 
                      className="w-4 h-4" 
                      style={{ color: "var(--theme-accent-yellow)" }}
                    />
                    <span 
                      className="text-sm"
                      style={{ color: "var(--theme-fg-primary)" }}
                    >
                      Sophisticated
                    </span>
                  </div>
                  <span 
                    className="text-sm font-bold"
                    style={{ color: "var(--theme-fg-primary)" }}
                  >
                    {analytics.classificationBreakdown.sophisticated}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingDown 
                      className="w-4 h-4" 
                      style={{ color: "var(--theme-accent-red)" }}
                    />
                    <span 
                      className="text-sm"
                      style={{ color: "var(--theme-fg-primary)" }}
                    >
                      Simple
                    </span>
                  </div>
                  <span 
                    className="text-sm font-bold"
                    style={{ color: "var(--theme-fg-primary)" }}
                  >
                    {analytics.classificationBreakdown.simple}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Circle 
                      className="w-4 h-4" 
                      style={{ color: "var(--theme-fg-tertiary)" }}
                    />
                    <span 
                      className="text-sm"
                      style={{ color: "var(--theme-fg-primary)" }}
                    >
                      Neutral
                    </span>
                  </div>
                  <span 
                    className="text-sm font-bold"
                    style={{ color: "var(--theme-fg-primary)" }}
                  >
                    {analytics.classificationBreakdown.neutral}
                  </span>
                </div>
              </div>
            </div>

            {/* Size Distribution */}
            <div>
              <h3 
                className="text-sm font-semibold mb-3"
                style={{ color: "var(--theme-fg-secondary)" }}
              >
                Size Distribution
              </h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span 
                    className="text-sm"
                    style={{ color: "var(--theme-fg-primary)" }}
                  >
                    Large (&gt;70%)
                  </span>
                  <span 
                    className="text-sm font-bold"
                    style={{ color: "var(--theme-accent-green)" }}
                  >
                    {analytics.sizeDistribution.large}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span 
                    className="text-sm"
                    style={{ color: "var(--theme-fg-primary)" }}
                  >
                    Medium (30-70%)
                  </span>
                  <span 
                    className="text-sm font-bold"
                    style={{ color: "var(--theme-accent-blue)" }}
                  >
                    {analytics.sizeDistribution.medium}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span 
                    className="text-sm"
                    style={{ color: "var(--theme-fg-primary)" }}
                  >
                    Small (&lt;30%)
                  </span>
                  <span 
                    className="text-sm font-bold"
                    style={{ color: "var(--theme-fg-tertiary)" }}
                  >
                    {analytics.sizeDistribution.small}
                  </span>
                </div>
              </div>
            </div>
          </div>
    </div>
  );
}

