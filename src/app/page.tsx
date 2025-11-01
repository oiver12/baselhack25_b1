import MessageStream from "./components/MessageStream";
import SuggestionsDisplay from "./components/SuggestionsDisplay";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 via-white to-zinc-50 dark:from-zinc-950 dark:via-black dark:to-zinc-950">
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
