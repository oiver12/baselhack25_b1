"use client";

interface ConsensusSummaryProps {
  question: string;
  summary: string;
  opinions: string[];
}

export default function ConsensusSummary({ question, summary, opinions }: ConsensusSummaryProps) {
  return (
    <div 
      className="rounded-2xl shadow-2xl border backdrop-blur-xl p-8 print:bg-white print:shadow-none print:border-2 print:border-gray-300 print:backdrop-blur-none"
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
        {/* Question */}
        <div>
          <h2 
            className="text-2xl font-bold mb-3 text-black print:text-black"
            style={{ color: "#000000" }}
          >
            Discussion Overview
          </h2>
          <p 
            className="text-lg font-medium italic text-gray-700 print:text-black"
            style={{ color: "#374151" }}
          >
            "{question}"
          </p>
        </div>

        {/* Summary */}
        <div 
          className="relative pl-4 border-l-2"
          style={{ borderColor: "var(--theme-accent-blue)" }}
        >
          <p 
            className="text-base leading-relaxed text-gray-800 print:text-black"
            style={{ color: "#1f2937" }}
          >
            {summary}
          </p>
        </div>

        {/* Opinions */}
        <div className="space-y-4">
          <h3 
            className="text-xl font-semibold text-black print:text-black"
            style={{ color: "#000000" }}
          >
            Key Perspectives
          </h3>
          <div className="space-y-3">
            {opinions.map((opinion, index) => (
              <div
                key={index}
                className="p-4 rounded-xl print:bg-gray-50 print:border print:border-gray-200"
                style={{ backgroundColor: "#f9fafb" }}
              >
                <p 
                  className="text-sm leading-relaxed text-gray-700 print:text-black"
                  style={{ color: "#374151" }}
                >
                  {opinion}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

