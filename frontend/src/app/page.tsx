import QuestionForm from "./components/QuestionForm";

export default function Home() {
  return (
    <div 
      className="min-h-screen relative overflow-hidden"
      style={{
        background: `linear-gradient(135deg, var(--theme-bg-secondary) 0%, var(--theme-bg-primary) 50%, var(--theme-bg-secondary) 100%)`,
      }}
    >
      {/* Animated background gradient orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute top-1/4 -left-1/4 w-[600px] h-[600px] rounded-full blur-3xl opacity-30 animate-pulse"
          style={{
            background: `radial-gradient(circle, var(--theme-accent-blue), transparent 70%)`,
            animation: "pulse 8s ease-in-out infinite",
            animationDelay: "0s",
          }}
        />
        <div 
          className="absolute bottom-1/4 -right-1/4 w-[500px] h-[500px] rounded-full blur-3xl opacity-25 animate-pulse"
          style={{
            background: `radial-gradient(circle, var(--theme-accent-purple), transparent 70%)`,
            animation: "pulse 10s ease-in-out infinite",
            animationDelay: "2s",
          }}
        />
        <div 
          className="absolute top-1/2 right-1/3 w-[400px] h-[400px] rounded-full blur-3xl opacity-20 animate-pulse"
          style={{
            background: `radial-gradient(circle, var(--theme-accent-pink), transparent 70%)`,
            animation: "pulse 12s ease-in-out infinite",
            animationDelay: "4s",
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10">
        <QuestionForm />
      </div>
    </div>
  );
}
