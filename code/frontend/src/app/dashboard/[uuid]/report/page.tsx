import { ArrowLeft, Calendar } from "lucide-react";
import Link from "next/link";
import ConsensusSummary from "@/app/components/ConsensusSummary";
import MessageClusterPlot from "@/app/components/MessageClusterPlot";
import SolutionCard from "@/app/components/SolutionCard";
import ReportInsights from "@/app/components/ReportInsights";
import PrintButton from "@/app/components/PrintButton";
import ClusterExperts from "@/app/components/ClusterExperts";
import { mockReportData } from "@/lib/mockReportData";

interface ReportPageProps {
  params: Promise<{
    uuid: string;
  }>;
  searchParams: Promise<{
    uuid: string;
  }>;
}

interface ReportApiResponse {
  question: string;
  results: Array<{
    message_id: string;
    x: number;
    y: number;
    message: string;
    name: string;
    profile_pic_url: string;
    two_word_summary?: string;
    classification?: string;
    is_excellent?: boolean;
  }>;
  summary: {
    summary: string;
    description?: string;
    points: Array<{
      title: string;
      pros: string[];
      cons: string[];
      approval_rating: number;
    }>;
  };
  noble_messages?: Record<
    string,
    {
      cluster: string;
      message_content: string;
      username: string;
      bulletpoint: string[];
      profile_pic_url: string;
      cluster_label: string;
    }
  >;
}

export default async function ReportPage({
  params,
  searchParams,
}: ReportPageProps) {
  const { uuid } = await params;
  const { uuid: key } = await searchParams;

  // Fetch report data from backend API
  const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
  let reportData = mockReportData;
  let apiData: ReportApiResponse | null = null;

  try {
    const response = await fetch(
      `${backendUrl}/api/report/${uuid}?key=${key}`,
      {
        cache: "no-store",
      }
    );
    console.log(response);
    if (response.status === 401) {
      return (
        <div className="min-h-screen flex flex-col justify-center items-center bg-white">
          <h1 className="text-4xl font-bold text-red-600 mb-4">
            401 Unauthorized
          </h1>
          <p className="text-lg text-gray-700 mb-2">
            You are not authorized to view this report.
          </p>
        </div>
      );
    }
    if (response.ok) {
      apiData = await response.json();

      // Transform API data to match our ReportData structure
      reportData = {
        question: apiData!.question,
        summary: apiData!.summary.description || apiData!.summary.summary,
        opinions: apiData!.summary.points.map(
          (point) =>
            `${point.title}: ${Math.round(
              point.approval_rating * 100
            )}% approval rating`
        ),
        messagePoints: apiData!.results.map((result) => ({
          id: result.message_id,
          x: result.x,
          y: result.y,
          message: result.message,
          user: result.name,
          profilePicUrl: result.profile_pic_url,
          cluster: result.two_word_summary,
          classification: result.classification as
            | "positive"
            | "neutral"
            | "negative"
            | undefined,
        })),
        solutions: apiData!.summary.points.map((point, idx) => ({
          id: `solution-${idx + 1}`,
          title: point.title,
          description: point.title,
          pros: point.pros,
          cons: point.cons,
          approvalPercentage: Math.round(point.approval_rating * 100),
        })),
      };
    }
  } catch (error) {
    // Silently fall back to mock data on error
    // INSERT_YOUR_CODE
    console.error(error);
  }

  // Find the best solution (highest approval rating)
  const sortedSolutions = [...reportData.solutions].sort(
    (a, b) => b.approvalPercentage - a.approvalPercentage
  );
  const bestSolution = sortedSolutions[0];

  // Always highlight the solution with the highest approval rating
  const bestSolutionId = bestSolution?.id || null;

  return (
    <div
      className="min-h-screen relative flex flex-col bg-white print:bg-white"
      style={{
        background: "white",
      }}
    >
      {/* Subtle background pattern - hidden when printing */}
      <div
        className="absolute inset-0 opacity-[0.015] pointer-events-none print:hidden"
        style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, var(--theme-fg-primary) 1px, transparent 0)`,
          backgroundSize: "40px 40px",
        }}
      />

      {/* Header */}
      <header
        className="sticky top-0 z-50 w-full border-b backdrop-blur-xl print:static print:border-b-2 print:bg-white print:backdrop-blur-none"
        style={{
          backgroundColor: "white",
          borderColor: "#e5e7eb",
          opacity: 1,
        }}
      >
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between gap-4">
            <Link
              href={`/dashboard/${uuid}`}
              className="flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95"
              style={{
                backgroundColor: "var(--theme-bg-secondary)",
                color: "var(--theme-fg-primary)",
              }}
              aria-label="Back to dashboard"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>

            <h1
              className="flex-1 text-center text-lg md:text-xl font-bold text-black print:text-black"
              style={{ color: "#000000" }}
            >
              Consensus Report
            </h1>

            {/* Spacer for centering */}
            <div className="w-10" />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-10 container mx-auto px-4 py-8 max-w-7xl print:px-2 print:py-4">
        <div className="space-y-8">
          {/* Report Header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 print:hidden">
            <div className="flex items-center gap-3">
              <Calendar
                className="w-5 h-5"
                style={{ color: "var(--theme-accent-blue)" }}
              />
              <div>
                <p className="text-sm" style={{ color: "#6b7280" }}>
                  Generated on{" "}
                  {new Date().toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </div>
            </div>
            <PrintButton />
          </div>

          {/* Summary Section */}
          <ConsensusSummary
            question={reportData.question}
            summary={reportData.summary}
            opinions={reportData.opinions}
          />

          {/* Cluster Plot and Insights Side by Side */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Cluster Plot - takes 2 columns */}
            <div className="lg:col-span-2">
              <MessageClusterPlot messagePoints={reportData.messagePoints} />
            </div>

            {/* Insights - takes 1 column */}
            <div className="lg:col-span-1">
              <ReportInsights messagePoints={reportData.messagePoints} />
            </div>
          </div>

          {/* Cluster Experts Section */}
          {apiData?.noble_messages && (
            <ClusterExperts nobleMessages={apiData.noble_messages} />
          )}

          {/* Solutions Section */}
          <div>
            <h2
              className="text-2xl font-bold mb-6 text-black print:text-black"
              style={{ color: "#000000" }}
            >
              Proposed Solutions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 print:grid-cols-1">
              {reportData.solutions.map((solution) => (
                <SolutionCard
                  key={solution.id}
                  solution={solution}
                  isBest={solution.id === bestSolutionId}
                />
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
