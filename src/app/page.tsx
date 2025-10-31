import SuggestionsDisplay from "./components/SuggestionsDisplay";
import MessageStream from "./components/MessageStream";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 via-white to-zinc-50 dark:from-zinc-950 dark:via-black dark:to-zinc-950">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-4rem)]">
          {/* Main Content - Suggestions */}
          <div className="lg:col-span-2 h-full overflow-hidden">
            <SuggestionsDisplay />
          </div>

          {/* Sidebar - Message Stream */}
          <div className="lg:col-span-1 h-full">
            <MessageStream />
          </div>
        </div>
      </div>
    </div>
  );
}
