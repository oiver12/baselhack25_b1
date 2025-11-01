"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { defaultTheme, darkTheme, type Theme } from "./theme";

type ThemeName = "light" | "dark" | "custom";

interface ThemeContextValue {
  theme: Theme;
  themeName: ThemeName;
  setTheme: (theme: Theme, name?: ThemeName) => void;
  applyTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [themeName, setThemeName] = useState<ThemeName>("dark");
  const [theme, setThemeState] = useState<Theme>(darkTheme);

  const applyTheme = () => {
    const root = document.documentElement;
    const isDark = themeName === "dark";
    
    // Background
    root.style.setProperty("--theme-bg-primary", theme.background.primary);
    root.style.setProperty("--theme-bg-secondary", theme.background.secondary);
    root.style.setProperty("--theme-bg-tertiary", theme.background.tertiary);
    
    // Foreground
    root.style.setProperty("--theme-fg-primary", theme.foreground.primary);
    root.style.setProperty("--theme-fg-secondary", theme.foreground.secondary);
    root.style.setProperty("--theme-fg-tertiary", theme.foreground.tertiary);
    
    // Bubbles
    root.style.setProperty("--theme-bubble-primary-from", theme.bubbles.primary.from);
    root.style.setProperty("--theme-bubble-primary-via", theme.bubbles.primary.via);
    root.style.setProperty("--theme-bubble-primary-to", theme.bubbles.primary.to);
    root.style.setProperty("--theme-bubble-opinion-from", theme.bubbles.opinion.from);
    root.style.setProperty("--theme-bubble-opinion-to", theme.bubbles.opinion.to);
    root.style.setProperty("--theme-bubble-pros-from", theme.bubbles.pros.from);
    root.style.setProperty("--theme-bubble-pros-to", theme.bubbles.pros.to);
    root.style.setProperty("--theme-bubble-cons-from", theme.bubbles.cons.from);
    root.style.setProperty("--theme-bubble-cons-to", theme.bubbles.cons.to);
    
    // Accents
    root.style.setProperty("--theme-accent-blue", theme.accents.blue);
    root.style.setProperty("--theme-accent-purple", theme.accents.purple);
    root.style.setProperty("--theme-accent-pink", theme.accents.pink);
    root.style.setProperty("--theme-accent-green", theme.accents.green);
    root.style.setProperty("--theme-accent-red", theme.accents.red);
    root.style.setProperty("--theme-accent-yellow", theme.accents.yellow);
    root.style.setProperty("--theme-accent-emerald", theme.accents.emerald);
    root.style.setProperty("--theme-accent-sky", theme.accents.sky);
    root.style.setProperty("--theme-accent-indigo", theme.accents.indigo);
    root.style.setProperty("--theme-accent-amber", theme.accents.amber);
    root.style.setProperty("--theme-accent-orange", theme.accents.orange);
    root.style.setProperty("--theme-accent-cyan", theme.accents.cyan);
    
    // Badges - apply appropriate variant based on theme
    root.style.setProperty("--theme-badge-sophisticated-bg", isDark ? theme.badges.sophisticated.backgroundDark : theme.badges.sophisticated.background);
    root.style.setProperty("--theme-badge-sophisticated-text", isDark ? theme.badges.sophisticated.textDark : theme.badges.sophisticated.text);
    root.style.setProperty("--theme-badge-sophisticated-bg-dark", theme.badges.sophisticated.backgroundDark);
    root.style.setProperty("--theme-badge-sophisticated-text-dark", theme.badges.sophisticated.textDark);
    root.style.setProperty("--theme-badge-simple-bg", isDark ? theme.badges.simple.backgroundDark : theme.badges.simple.background);
    root.style.setProperty("--theme-badge-simple-text", isDark ? theme.badges.simple.textDark : theme.badges.simple.text);
    root.style.setProperty("--theme-badge-simple-bg-dark", theme.badges.simple.backgroundDark);
    root.style.setProperty("--theme-badge-simple-text-dark", theme.badges.simple.textDark);
    root.style.setProperty("--theme-badge-neutral-bg", isDark ? theme.badges.neutral.backgroundDark : theme.badges.neutral.background);
    root.style.setProperty("--theme-badge-neutral-text", isDark ? theme.badges.neutral.textDark : theme.badges.neutral.text);
    root.style.setProperty("--theme-badge-neutral-bg-dark", theme.badges.neutral.backgroundDark);
    root.style.setProperty("--theme-badge-neutral-text-dark", theme.badges.neutral.textDark);
    
    // Messages - apply appropriate variant based on theme
    root.style.setProperty("--theme-message-bg", isDark ? theme.messages.backgroundDark : theme.messages.background);
    root.style.setProperty("--theme-message-bg-dark", theme.messages.backgroundDark);
    root.style.setProperty("--theme-message-border", isDark ? theme.messages.borderDark : theme.messages.border);
    root.style.setProperty("--theme-message-border-dark", theme.messages.borderDark);
    root.style.setProperty("--theme-message-shadow", isDark ? theme.messages.shadowDark : theme.messages.shadow);
    root.style.setProperty("--theme-message-shadow-dark", theme.messages.shadowDark);
    root.style.setProperty("--theme-message-text", isDark ? theme.messages.textDark : theme.messages.text);
    root.style.setProperty("--theme-message-text-dark", theme.messages.textDark);
    root.style.setProperty("--theme-message-text-secondary", isDark ? theme.messages.textSecondaryDark : theme.messages.textSecondary);
    root.style.setProperty("--theme-message-text-secondary-dark", theme.messages.textSecondaryDark);
    
    // Loading - apply appropriate variant based on theme
    root.style.setProperty("--theme-loading-border", isDark ? theme.loading.borderDark : theme.loading.border);
    root.style.setProperty("--theme-loading-border-dark", theme.loading.borderDark);
    root.style.setProperty("--theme-loading-border-active", isDark ? theme.loading.borderActiveDark : theme.loading.borderActive);
    root.style.setProperty("--theme-loading-border-active-dark", theme.loading.borderActiveDark);
    
    // Glass
    root.style.setProperty("--theme-glass-white", theme.glass.white);
    root.style.setProperty("--theme-glass-overlay", theme.glass.overlay);
    
    // Card gradients
    theme.cardGradients.forEach((gradient, index) => {
      root.style.setProperty(`--theme-card-gradient-${index}-from`, gradient[0]);
      root.style.setProperty(`--theme-card-gradient-${index}-via`, gradient[1]);
      root.style.setProperty(`--theme-card-gradient-${index}-to`, gradient[2]);
    });
    
    // Accent rings
    const accentRingColors = [
      theme.accents.sky,
      theme.accents.purple,
      theme.accents.emerald,
      theme.accents.amber,
      theme.accents.pink,
      theme.accents.cyan,
    ];
    accentRingColors.forEach((color, index) => {
      const rgba = hexToRgba(color, index < 3 ? 0.3 : 0.25);
      root.style.setProperty(`--theme-accent-ring-${index}`, rgba);
    });
  };

  const setTheme = (newTheme: Theme, name: ThemeName = "custom") => {
    setThemeState(newTheme);
    setThemeName(name);
  };

  // Apply theme on mount and when theme changes
  useEffect(() => {
    applyTheme();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme, themeName]);

  // Detect system preference
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e: MediaQueryListEvent) => {
      if (themeName === "light" || themeName === "dark") {
        setTheme(e.matches ? darkTheme : defaultTheme, e.matches ? "dark" : "light");
      }
    };

    // Check system preference on mount
    const prefersDark = mediaQuery.matches;
    if (themeName === "light") {
      setTheme(defaultTheme, "light");
    } else if (themeName === "dark") {
      setTheme(darkTheme, "dark");
    } else {
      setTheme(prefersDark ? darkTheme : defaultTheme, prefersDark ? "dark" : "light");
    }

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, themeName, setTheme, applyTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}

// Helper to convert hex to rgba
function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

