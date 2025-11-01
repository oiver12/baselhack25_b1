/**
 * Theme configuration for the application
 * All colors are defined here and can be customized
 */

export interface Theme {
  // Background colors
  background: {
    primary: string;
    secondary: string;
    tertiary: string;
  };

  // Foreground/text colors
  foreground: {
    primary: string;
    secondary: string;
    tertiary: string;
  };

  // Bubble colors
  bubbles: {
    primary: {
      from: string;
      via: string;
      to: string;
    };
    opinion: {
      from: string;
      to: string;
    };
    pros: {
      from: string;
      to: string;
    };
    cons: {
      from: string;
      to: string;
    };
  };

  // Suggestion card gradients
  cardGradients: string[][];

  // Accent colors
  accents: {
    blue: string;
    purple: string;
    pink: string;
    green: string;
    red: string;
    yellow: string;
    emerald: string;
    sky: string;
    indigo: string;
    amber: string;
    orange: string;
    cyan: string;
  };

  // Classification badge colors
  badges: {
    sophisticated: {
      background: string;
      text: string;
      backgroundDark: string;
      textDark: string;
    };
    simple: {
      background: string;
      text: string;
      backgroundDark: string;
      textDark: string;
    };
    neutral: {
      background: string;
      text: string;
      backgroundDark: string;
      textDark: string;
    };
  };

  // Message/Toast colors
  messages: {
    background: string;
    backgroundDark: string;
    border: string;
    borderDark: string;
    shadow: string;
    shadowDark: string;
    text: string;
    textDark: string;
    textSecondary: string;
    textSecondaryDark: string;
  };

  // Loading spinner colors
  loading: {
    border: string;
    borderDark: string;
    borderActive: string;
    borderActiveDark: string;
  };

  // Glass/overlay effects
  glass: {
    white: string;
    overlay: string;
  };
}

// Default theme
export const defaultTheme: Theme = {
  background: {
    primary: "#ffffff",
    secondary: "#fafafa",
    tertiary: "#f5f5f5",
  },
  foreground: {
    primary: "#171717",
    secondary: "#404040",
    tertiary: "#737373",
  },
  bubbles: {
    primary: {
      from: "#6366f1",
      via: "#8b5cf6",
      to: "#a855f7",
    },
    opinion: {
      from: "#818cf8",
      to: "#6366f1",
    },
    pros: {
      from: "#10b981",
      to: "#059669",
    },
    cons: {
      from: "#f43f5e",
      to: "#e11d48",
    },
  },
  cardGradients: [
    ["#0ea5e9", "#3b82f6", "#2563eb"], // sky-400, sky-500, blue-600
    ["#a855f7", "#a855f7", "#4f46e5"], // fuchsia-400, purple-500, indigo-600
    ["#34d399", "#14b8a6", "#06b6d4"], // emerald-400, teal-500, cyan-500
    ["#fbbf24", "#f97316", "#f43f5e"], // amber-400, orange-500, rose-500
    ["#ec4899", "#f43f5e", "#ef4444"], // pink-500, rose-500, red-500
    ["#22d3ee", "#3b82f6", "#4f46e5"], // cyan-400, blue-500, indigo-500
  ],
  accents: {
    blue: "#3b82f6",
    purple: "#a855f7",
    pink: "#ec4899",
    green: "#10b981",
    red: "#ef4444",
    yellow: "#fbbf24",
    emerald: "#10b981",
    sky: "#0ea5e9",
    indigo: "#6366f1",
    amber: "#fbbf24",
    orange: "#f97316",
    cyan: "#06b6d4",
  },
  badges: {
    sophisticated: {
      background: "rgba(16, 185, 129, 0.8)",
      text: "#065f46",
      backgroundDark: "rgba(16, 185, 129, 0.2)",
      textDark: "#a7f3d0",
    },
    simple: {
      background: "rgba(14, 165, 233, 0.8)",
      text: "#0c4a6e",
      backgroundDark: "rgba(14, 165, 233, 0.2)",
      textDark: "#bae6fd",
    },
    neutral: {
      background: "rgba(148, 163, 184, 0.8)",
      text: "#334155",
      backgroundDark: "rgba(148, 163, 184, 0.2)",
      textDark: "#cbd5e1",
    },
  },
  messages: {
    background: "rgba(255, 255, 255, 0.2)",
    backgroundDark: "rgba(17, 24, 39, 0.2)",
    border: "rgba(255, 255, 255, 0.2)",
    borderDark: "rgba(255, 255, 255, 0.1)",
    shadow: "rgba(59, 130, 246, 0.4)",
    shadowDark: "rgba(59, 130, 246, 0.2)",
    text: "#1e293b",
    textDark: "#f1f5f9",
    textSecondary: "#475569",
    textSecondaryDark: "#cbd5e1",
  },
  loading: {
    border: "#dbeafe",
    borderDark: "#1e3a8a",
    borderActive: "#3b82f6",
    borderActiveDark: "#60a5fa",
  },
  glass: {
    white: "#ffffff",
    overlay: "rgba(255, 255, 255, 0.8)",
  },
};

// Dark theme variant
export const darkTheme: Theme = {
  ...defaultTheme,
  background: {
    primary: "#0a0a0a",
    secondary: "#171717",
    tertiary: "#262626",
  },
  foreground: {
    primary: "#ededed",
    secondary: "#d4d4d4",
    tertiary: "#a3a3a3",
  },
};

// Helper function to convert theme to CSS variables
export function themeToCSSVariables(theme: Theme, prefix = "theme"): Record<string, string> {
  return {
    [`--${prefix}-bg-primary`]: theme.background.primary,
    [`--${prefix}-bg-secondary`]: theme.background.secondary,
    [`--${prefix}-bg-tertiary`]: theme.background.tertiary,
    [`--${prefix}-fg-primary`]: theme.foreground.primary,
    [`--${prefix}-fg-secondary`]: theme.foreground.secondary,
    [`--${prefix}-fg-tertiary`]: theme.foreground.tertiary,
    [`--${prefix}-bubble-primary-from`]: theme.bubbles.primary.from,
    [`--${prefix}-bubble-primary-via`]: theme.bubbles.primary.via,
    [`--${prefix}-bubble-primary-to`]: theme.bubbles.primary.to,
    [`--${prefix}-bubble-opinion-from`]: theme.bubbles.opinion.from,
    [`--${prefix}-bubble-opinion-to`]: theme.bubbles.opinion.to,
    [`--${prefix}-bubble-pros-from`]: theme.bubbles.pros.from,
    [`--${prefix}-bubble-pros-to`]: theme.bubbles.pros.to,
    [`--${prefix}-bubble-cons-from`]: theme.bubbles.cons.from,
    [`--${prefix}-bubble-cons-to`]: theme.bubbles.cons.to,
    [`--${prefix}-accent-blue`]: theme.accents.blue,
    [`--${prefix}-accent-purple`]: theme.accents.purple,
    [`--${prefix}-accent-pink`]: theme.accents.pink,
    [`--${prefix}-accent-green`]: theme.accents.green,
    [`--${prefix}-accent-red`]: theme.accents.red,
    [`--${prefix}-accent-yellow`]: theme.accents.yellow,
    [`--${prefix}-accent-emerald`]: theme.accents.emerald,
    [`--${prefix}-accent-sky`]: theme.accents.sky,
    [`--${prefix}-accent-indigo`]: theme.accents.indigo,
    [`--${prefix}-accent-amber`]: theme.accents.amber,
    [`--${prefix}-accent-orange`]: theme.accents.orange,
    [`--${prefix}-accent-cyan`]: theme.accents.cyan,
    [`--${prefix}-badge-sophisticated-bg`]: theme.badges.sophisticated.background,
    [`--${prefix}-badge-sophisticated-text`]: theme.badges.sophisticated.text,
    [`--${prefix}-badge-sophisticated-bg-dark`]: theme.badges.sophisticated.backgroundDark,
    [`--${prefix}-badge-sophisticated-text-dark`]: theme.badges.sophisticated.textDark,
    [`--${prefix}-badge-simple-bg`]: theme.badges.simple.background,
    [`--${prefix}-badge-simple-text`]: theme.badges.simple.text,
    [`--${prefix}-badge-simple-bg-dark`]: theme.badges.simple.backgroundDark,
    [`--${prefix}-badge-simple-text-dark`]: theme.badges.simple.textDark,
    [`--${prefix}-badge-neutral-bg`]: theme.badges.neutral.background,
    [`--${prefix}-badge-neutral-text`]: theme.badges.neutral.text,
    [`--${prefix}-badge-neutral-bg-dark`]: theme.badges.neutral.backgroundDark,
    [`--${prefix}-badge-neutral-text-dark`]: theme.badges.neutral.textDark,
    [`--${prefix}-message-bg`]: theme.messages.background,
    [`--${prefix}-message-bg-dark`]: theme.messages.backgroundDark,
    [`--${prefix}-message-border`]: theme.messages.border,
    [`--${prefix}-message-border-dark`]: theme.messages.borderDark,
    [`--${prefix}-message-shadow`]: theme.messages.shadow,
    [`--${prefix}-message-shadow-dark`]: theme.messages.shadowDark,
    [`--${prefix}-message-text`]: theme.messages.text,
    [`--${prefix}-message-text-dark`]: theme.messages.textDark,
    [`--${prefix}-message-text-secondary`]: theme.messages.textSecondary,
    [`--${prefix}-message-text-secondary-dark`]: theme.messages.textSecondaryDark,
    [`--${prefix}-loading-border`]: theme.loading.border,
    [`--${prefix}-loading-border-dark`]: theme.loading.borderDark,
    [`--${prefix}-loading-border-active`]: theme.loading.borderActive,
    [`--${prefix}-loading-border-active-dark`]: theme.loading.borderActiveDark,
    [`--${prefix}-glass-white`]: theme.glass.white,
    [`--${prefix}-glass-overlay`]: theme.glass.overlay,
  };
}

