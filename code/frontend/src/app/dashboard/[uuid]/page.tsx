import MessageStream from "../../components/MessageStream";
import SuggestionsDisplay from "../../components/SuggestionsDisplay";
import DashboardHeader from "../../components/DashboardHeader";

interface DashboardPageProps {
  params: {
    uuid: string;
  };
}

export default async function DashboardPage({ params }: DashboardPageProps) {
  const { uuid } = await params;

  return (
    <div 
      className="min-h-screen relative flex flex-col"
      style={{
        background: `linear-gradient(135deg, var(--theme-bg-secondary) 0%, var(--theme-bg-primary) 25%, var(--theme-bg-secondary) 50%, var(--theme-bg-primary) 75%, var(--theme-bg-secondary) 100%)`,
      }}
    >
      {/* Header - Overlay on top */}
      <div className="absolute top-0 left-0 right-0 z-50">
        <DashboardHeader questionId={uuid} />
      </div>

      {/* Subtle background pattern */}
      <div className="absolute inset-0 opacity-[0.015] pointer-events-none"
        style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, var(--theme-fg-primary) 1px, transparent 0)`,
          backgroundSize: "40px 40px",
        }}
      />

      {/* Full screen canvas */}
      <div className="relative z-10 w-full h-screen overflow-hidden">
        <SuggestionsDisplay questionId={uuid} />
      </div>
      
      {/* Toast notifications */}
      <MessageStream uuid={uuid} />
    </div>
  );
}
