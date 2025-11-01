import MessageStream from "./components/MessageStream";
import SuggestionsDisplay from "./components/SuggestionsDisplay";

export default function Home() {
  return (
    <div 
      className="min-h-screen"
      style={{
        background: `linear-gradient(to bottom right, var(--theme-bg-secondary), var(--theme-bg-primary), var(--theme-bg-secondary))`,
      }}
    >
      <div className="container mx-auto px-4 py-8">
        <div className="h-[calc(100vh-4rem)]">
          {/* Main Content - Suggestions */}
          <div className="h-full overflow-hidden">
            <SuggestionsDisplay />
          </div>
        </div>
      </div>
      {/* Toast notifications */}
      <MessageStream />
    </div>
  );
}
