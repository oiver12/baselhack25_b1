"use client";

import { Check, X } from "lucide-react";
import type { ConsensusSolution } from "@/lib/types";

interface SolutionCardProps {
  solution: ConsensusSolution;
  isBest?: boolean;
}

export default function SolutionCard({ solution, isBest = false }: SolutionCardProps) {
  return (
    <div 
      className={`rounded-2xl shadow-2xl border backdrop-blur-xl p-6 transition-all duration-300 print:shadow-none print:border-2 ${
        isBest ? "ring-4 ring-offset-4 scale-105 print:scale-100" : ""
      }`}
      style={{
        backgroundColor: isBest ? "#fef3c7" : "white",
        borderColor: isBest ? "#f59e0b" : "#e5e7eb",
        borderWidth: isBest ? "3px" : "1px",
        boxShadow: isBest 
          ? "0 25px 50px -12px rgba(245, 158, 11, 0.4), 0 10px 15px -3px rgba(245, 158, 11, 0.2)" 
          : "0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)",
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
      
      {isBest && (
        <div className="absolute -top-3 right-4 bg-yellow-500 text-white px-3 py-1 rounded-full text-xs font-bold print:bg-yellow-400 print:text-black">
          ⭐ BEST SOLUTION
        </div>
      )}
      
      <div className="relative space-y-5">
        {/* Header */}
        <div>
          <h3 
            className={`text-xl font-bold mb-2 ${isBest ? "text-amber-700" : "text-black print:text-black"}`}
            style={{ color: isBest ? "#92400e" : "#000000" }}
          >
            {solution.title}
          </h3>
          <p 
            className="text-sm text-gray-700 print:text-black"
            style={{ color: "#374151" }}
          >
            {solution.description}
          </p>
        </div>

        {/* Pros */}
        <div className="space-y-2">
          <h4 
            className="text-sm font-semibold flex items-center gap-2"
            style={{ color: "var(--theme-accent-green)" }}
          >
            <Check className="w-4 h-4" />
            Advantages
          </h4>
          <ul className="space-y-2 pl-6">
            {solution.pros.map((pro, index) => (
                <li 
                key={index}
                className="text-sm list-disc text-gray-700 print:text-black"
                style={{ color: "#374151" }}
              >
                {pro}
              </li>
            ))}
          </ul>
        </div>

        {/* Cons */}
        <div className="space-y-2">
          <h4 
            className="text-sm font-semibold flex items-center gap-2"
            style={{ color: "var(--theme-accent-red)" }}
          >
            <X className="w-4 h-4" />
            Challenges
          </h4>
          <ul className="space-y-2 pl-6">
            {solution.cons.map((con, index) => (
              <li 
                key={index}
                className="text-sm list-disc text-gray-700 print:text-black"
                style={{ color: "#374151" }}
              >
                {con}
              </li>
            ))}
          </ul>
        </div>

        {/* Approval progress bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span 
              className="text-xs font-medium text-gray-600 print:text-black"
              style={{ color: "#4b5563" }}
            >
              Approval Rate
            </span>
            <span 
              className={`text-sm font-bold ${isBest ? "text-amber-700" : "text-black print:text-black"}`}
              style={{ color: isBest ? "#92400e" : "#000000" }}
            >
              {solution.approvalPercentage}%
            </span>
          </div>
          <div 
            className="h-3 rounded-full overflow-hidden print:border print:border-gray-300"
            style={{ backgroundColor: "#e5e7eb" }}
          >
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${solution.approvalPercentage}%`,
                backgroundColor: isBest ? "#f59e0b" : "var(--theme-accent-blue)",
                backgroundImage: isBest 
                  ? "linear-gradient(90deg, #f59e0b, #d97706)" 
                  : "linear-gradient(90deg, var(--theme-accent-blue), var(--theme-accent-purple))",
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

