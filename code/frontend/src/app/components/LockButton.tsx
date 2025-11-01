"use client";

import { useState, useEffect } from "react";
import { Lock, X } from "lucide-react";

export default function LockButton() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [savedKey, setSavedKey] = useState<string | null>(null);

  // Get saved key from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("key");
    if (saved) {
      setSavedKey(saved);
    }
  }, []);

  const handleSavePassword = () => {
    if (!password.trim()) {
      return;
    }

    // Save to localStorage
    localStorage.setItem("key", password);
    
    setSavedKey(password);
    setPassword("");
    setIsModalOpen(false);
    
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent("key-updated"));
  };

  const handleClearPassword = () => {
    // Remove from localStorage
    localStorage.removeItem("key");
    
    setSavedKey(null);
    setPassword("");
    setIsModalOpen(false);
    
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent("key-updated"));
  };

  return (
    <>
      {/* Lock Button - Fixed at bottom */}
      <button
        onClick={() => setIsModalOpen(true)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-xl"
        style={{
          background: "linear-gradient(135deg, var(--theme-bubble-primary-from), var(--theme-bubble-primary-to))",
          color: "white",
        }}
        aria-label="Lock / Set Key"
      >
        <Lock className="w-6 h-6" />
        {savedKey && (
          <div
            className="absolute -top-1 -right-1 w-4 h-4 rounded-full border-2 border-white"
            style={{ backgroundColor: "var(--theme-accent-green)" }}
            title="Key is set"
          />
        )}
      </button>

      {/* Modal */}
      {isModalOpen && (
        <div
          className="fixed inset-0 z-[60] flex items-center justify-center p-4"
          style={{ backgroundColor: "rgba(0, 0, 0, 0.5)" }}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setIsModalOpen(false);
              setPassword("");
            }
          }}
        >
          <div
            className="relative backdrop-blur-xl rounded-2xl shadow-2xl border p-8 max-w-md w-full animate-in fade-in zoom-in-95 duration-300"
            style={{
              backgroundColor: "var(--theme-bg-primary)",
              borderColor: "var(--theme-bg-tertiary)",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1), 0 0 0 1px var(--theme-bg-tertiary)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => {
                setIsModalOpen(false);
                setPassword("");
              }}
              className="absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center transition-colors"
              style={{
                backgroundColor: "var(--theme-bg-secondary)",
                color: "var(--theme-fg-secondary)",
              }}
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Content */}
            <div className="space-y-6">
              <div className="space-y-2">
                <h2
                  className="text-2xl font-bold"
                  style={{ color: "var(--theme-fg-primary)" }}
                >
                  {savedKey ? "Update Key" : "Set Key"}
                </h2>
                <p
                  className="text-sm"
                  style={{ color: "var(--theme-fg-secondary)" }}
                >
                  Enter a password or code to save to local storage.
                </p>
              </div>

              {savedKey && (
                <div
                  className="px-4 py-3 rounded-xl backdrop-blur-sm"
                  style={{
                    backgroundColor: "rgba(16, 185, 129, 0.1)",
                    border: "1px solid rgba(16, 185, 129, 0.2)",
                  }}
                >
                  <p
                    className="text-sm font-medium"
                    style={{ color: "var(--theme-accent-green)" }}
                  >
                    ✓ Key is currently set
                  </p>
                </div>
              )}

              <div className="space-y-2">
                <label
                  htmlFor="password-input"
                  className="block text-sm font-semibold"
                  style={{ color: "var(--theme-fg-secondary)" }}
                >
                  Password / Code
                </label>
                <input
                  id="password-input"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleSavePassword();
                    } else if (e.key === "Escape") {
                      setIsModalOpen(false);
                      setPassword("");
                    }
                  }}
                  placeholder="Enter password or code..."
                  className="w-full px-4 py-3 rounded-xl border-2 transition-all duration-300"
                  style={{
                    backgroundColor: "var(--theme-bg-secondary)",
                    borderColor: "var(--theme-bg-tertiary)",
                    color: "var(--theme-fg-primary)",
                  }}
                  autoFocus
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleSavePassword}
                  disabled={!password.trim()}
                  className="flex-1 py-3 px-6 rounded-xl font-semibold text-white transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    background: password.trim()
                      ? "linear-gradient(135deg, var(--theme-bubble-primary-from), var(--theme-bubble-primary-to))"
                      : "linear-gradient(135deg, #94a3b8, #94a3b8)",
                    boxShadow: password.trim()
                      ? "0 10px 25px -5px rgba(99, 102, 241, 0.4), 0 0 0 1px rgba(99, 102, 241, 0.2)"
                      : "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                  }}
                >
                  {savedKey ? "Update Key" : "Save Key"}
                </button>
                {savedKey && (
                  <button
                    onClick={handleClearPassword}
                    className="px-6 py-3 rounded-xl font-semibold transition-all duration-300"
                    style={{
                      backgroundColor: "var(--theme-bg-secondary)",
                      color: "var(--theme-accent-red)",
                      border: "2px solid var(--theme-accent-red)",
                    }}
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

