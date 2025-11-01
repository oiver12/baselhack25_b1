"use client";

import { Download } from "lucide-react";

export default function PrintButton() {
  return (
    <button
      onClick={() => window.print()}
      className="flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 font-medium text-sm"
      style={{
        backgroundColor: "var(--theme-bg-secondary)",
        color: "var(--theme-fg-primary)",
      }}
      aria-label="Print Report"
    >
      <Download className="w-4 h-4" />
      <span>Print / Save as PDF</span>
    </button>
  );
}

