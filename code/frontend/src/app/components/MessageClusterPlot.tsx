"use client";

import Image from "next/image";
import { ScatterChart, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { MessagePoint } from "@/lib/types";

interface MessageClusterPlotProps {
  messagePoints: MessagePoint[];
}

const ACCENT_COLORS = [
  "var(--theme-accent-blue)",
  "var(--theme-accent-green)",
  "var(--theme-accent-purple)",
  "var(--theme-accent-pink)",
  "var(--theme-accent-red)",
  "var(--theme-accent-yellow)",
  "var(--theme-accent-emerald)",
  "var(--theme-accent-sky)",
];

function getClusterColor(cluster: string | undefined, index: number): string {
  if (!cluster) return "var(--theme-fg-tertiary)";
  
  // Generate a hash from the cluster name for consistent coloring
  let hash = 0;
  for (let i = 0; i < cluster.length; i++) {
    hash = ((hash << 5) - hash) + cluster.charCodeAt(i);
    hash = hash & hash; // Convert to 32bit integer
  }
  const colorIndex = Math.abs(hash) % ACCENT_COLORS.length;
  return ACCENT_COLORS[colorIndex];
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (active && payload && payload[0]) {
    const point = payload[0].payload as MessagePoint;
    return (
      <div
        className="backdrop-blur-xl rounded-2xl shadow-2xl border p-4"
        style={{
          backgroundColor: "white",
          borderColor: "#e5e7eb",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)",
        }}
      >
        <div className="flex items-start gap-3">
          <div className="relative shrink-0">
            <Image
              src={point.profilePicUrl}
              alt={point.user}
              width={48}
              height={48}
              className="rounded-xl shadow-lg ring-2 ring-indigo-400/30"
              unoptimized
            />
          </div>
          <div className="flex-1 min-w-0">
            <div
              className="font-bold text-sm mb-1"
              style={{ color: "#171717" }}
            >
              {point.user}
            </div>
            <p
              className="text-xs leading-relaxed italic"
              style={{ color: "#404040" }}
            >
              "{point.message}"
            </p>
            {point.cluster && (
              <div className="flex items-center gap-2 mt-2">
                <span
                  className="text-xs"
                  style={{ color: "#737373" }}
                >
                  {point.cluster.replace(/_/g, " ")}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
  return null;
}

export default function MessageClusterPlot({ messagePoints }: MessageClusterPlotProps) {
  // Get unique clusters from the data
  const uniqueClusters = Array.from(new Set(messagePoints.map(p => p.cluster).filter(Boolean)));
  
  return (
    <div
      className="relative rounded-2xl shadow-2xl border backdrop-blur-xl p-6 print:bg-white print:shadow-none print:border-2 print:border-gray-300 print:backdrop-blur-none print:break-inside-avoid"
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

      <div className="relative">
        <h3
          className="text-xl font-bold mb-4"
          style={{ color: "#000000" }}
        >
          Message Clusters
        </h3>
        <p
          className="text-sm mb-6 print:hidden"
          style={{ color: "#4b5563" }}
        >
          Each point represents a message. Hover to see details.
        </p>

        {/* Legend */}
        {uniqueClusters.length > 0 && (
          <div className="flex flex-wrap gap-4 mb-4 text-xs print:gap-3">
            {uniqueClusters.map((clusterName) => {
              const clusterLabel = clusterName!.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
              const color = getClusterColor(clusterName, 0);
              return (
                <div key={clusterName} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full print:w-2 print:h-2"
                    style={{ backgroundColor: color }}
                  />
                  <span style={{ color: "#4b5563" }}>
                    {clusterLabel}
                  </span>
                </div>
              );
            })}
          </div>
        )}

        {/* Scatter Plot */}
        <div className="relative w-full" style={{ height: "500px", minHeight: "500px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart
              margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            >
              <XAxis
                type="number"
                dataKey="x"
                domain={["auto", "auto"]}
                hide
              />
              <YAxis
                type="number"
                dataKey="y"
                domain={["auto", "auto"]}
                hide
              />
              <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: "3 3" }} />
              <Scatter data={messagePoints} fill="#8884d8" isAnimationActive={false}>
                {messagePoints.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={getClusterColor(entry.cluster, index)}
                  />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
