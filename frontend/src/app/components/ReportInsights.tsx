"use client";

import { useMemo } from "react";
import { 
  Users, 
  MessageSquare, 
  TrendingUp, 
  BarChart3,
  Star,
  Circle
} from "lucide-react";
import type { MessagePoint } from "@/lib/types";

interface ReportInsightsProps {
  messagePoints: MessagePoint[];
}

export default function ReportInsights({ messagePoints }: ReportInsightsProps) {
  const insights = useMemo(() => {
    const uniqueUsers = new Set(messagePoints.map(p => p.user));
    
    const classificationBreakdown = {
      good: messagePoints.filter(p => p.classification === "good").length,
      bad: messagePoints.filter(p => p.classification === "bad").length,
      neutral: messagePoints.filter(p => p.classification === "neutral").length,
    };

    const clusterBreakdown = messagePoints.reduce((acc, point) => {
      if (point.cluster) {
        acc[point.cluster] = (acc[point.cluster] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);

    const topClusters = Object.entries(clusterBreakdown)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([name, count]) => ({
        name: name.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase()),
        count,
        percentage: Math.round((count / messagePoints.length) * 100),
      }));

    return {
      totalMessages: messagePoints.length,
      totalParticipants: uniqueUsers.size,
      classificationBreakdown,
      topClusters,
    };
  }, [messagePoints]);

  return (
    <div 
      className="rounded-2xl shadow-2xl border backdrop-blur-xl p-6 print:bg-white print:shadow-none print:border-2 print:border-gray-300 print:backdrop-blur-none print:break-inside-avoid"
      style={{
        backgroundColor: "white",
        borderColor: "#e5e7eb",
        boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)",
      }}
    >
      {/* Blurred background overlay - hidden when printing */}
      <div 
        className="absolute inset-0 rounded-2xl -z-10 backdrop-blur-2xl print:hidden"
        style={{
          backgroundColor: "white",
          opacity: 0.8,
        }}
      />
      
      <div className="relative space-y-6">
        {/* Header */}
        <div className="flex items-center gap-2">
          <BarChart3 
            className="w-5 h-5" 
            style={{ color: "var(--theme-accent-blue)" }}
          />
          <h3 
            className="text-xl font-bold text-black print:text-black"
            style={{ color: "#000000" }}
          >
            Key Insights
          </h3>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div 
            className="p-4 rounded-xl print:bg-gray-50 print:border print:border-gray-200"
            style={{ backgroundColor: "#f9fafb" }}
          >
            <div className="flex items-center gap-2 mb-2">
              <MessageSquare 
                className="w-4 h-4" 
                style={{ color: "var(--theme-accent-blue)" }}
              />
              <span 
                className="text-xs font-medium uppercase tracking-wide"
                style={{ color: "#4b5563" }}
              >
                Messages
              </span>
            </div>
                <div 
                  className="text-2xl font-bold text-black print:text-black"
                  style={{ color: "#000000" }}
                >
                  {insights.totalMessages}
                </div>
          </div>

          <div 
            className="p-4 rounded-xl print:bg-gray-50 print:border print:border-gray-200"
            style={{ backgroundColor: "#f9fafb" }}
          >
            <div className="flex items-center gap-2 mb-2">
              <Users 
                className="w-4 h-4" 
                style={{ color: "var(--theme-accent-green)" }}
              />
              <span 
                className="text-xs font-medium uppercase tracking-wide"
                style={{ color: "#4b5563" }}
              >
                Participants
              </span>
            </div>
                <div 
                  className="text-2xl font-bold text-black print:text-black"
                  style={{ color: "#000000" }}
                >
                  {insights.totalParticipants}
                </div>
          </div>
        </div>

        {/* Opinion Types */}
        <div>
          <h4 
            className="text-sm font-semibold mb-3"
            style={{ color: "#1f2937" }}
          >
            Opinion Distribution
          </h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Circle 
                  className="w-3 h-3 fill-current" 
                  style={{ color: "var(--theme-accent-green)" }}
                />
                <span 
                  className="text-sm"
                  style={{ color: "#1f2937" }}
                >
                  Positive
                </span>
              </div>
                    <span 
                      className="text-sm font-bold text-black print:text-black"
                      style={{ color: "#000000" }}
                    >
                      {insights.classificationBreakdown.good}
                    </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Circle 
                  className="w-3 h-3 fill-current" 
                  style={{ color: "var(--theme-accent-red)" }}
                />
                <span 
                  className="text-sm"
                  style={{ color: "#1f2937" }}
                >
                  Negative
                </span>
              </div>
                    <span 
                      className="text-sm font-bold text-black print:text-black"
                      style={{ color: "#000000" }}
                    >
                      {insights.classificationBreakdown.bad}
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
                  style={{ color: "#1f2937" }}
                >
                  Neutral
                </span>
              </div>
                    <span 
                      className="text-sm font-bold text-black print:text-black"
                      style={{ color: "#000000" }}
                    >
                      {insights.classificationBreakdown.neutral}
                    </span>
            </div>
          </div>
        </div>

        {/* Top Clusters */}
        <div>
          <h4 
            className="text-sm font-semibold mb-3 flex items-center gap-2"
            style={{ color: "#1f2937" }}
          >
            <TrendingUp className="w-4 h-4" />
            Top Discussion Themes
          </h4>
          <div className="space-y-2">
            {insights.topClusters.map((cluster, index) => (
              <div 
                key={cluster.name}
                className="flex items-center justify-between p-3 rounded-xl print:bg-gray-50 print:border print:border-gray-200"
                style={{ backgroundColor: "#f9fafb" }}
              >
                <div className="flex items-center gap-3">
                  <div 
                    className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm"
                    style={{
                      backgroundColor: `var(--theme-accent-${["blue", "purple", "pink"][index % 3]})`,
                      color: "white",
                    }}
                  >
                    {index + 1}
                  </div>
                  <div>
                    <div 
                      className="text-sm font-semibold"
                      style={{ color: "#1f2937" }}
                    >
                      {cluster.name}
                    </div>
                    <div 
                      className="text-xs"
                      style={{ color: "#4b5563" }}
                    >
                      {cluster.count} messages
                    </div>
                  </div>
                </div>
                <div 
                  className="text-lg font-bold"
                  style={{ color: "var(--theme-accent-blue)" }}
                >
                  {cluster.percentage}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

