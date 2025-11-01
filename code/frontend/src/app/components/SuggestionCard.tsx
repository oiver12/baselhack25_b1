"use client";

import { type CSSProperties, useEffect, useMemo, useState } from "react";
import type { Suggestion } from "@/lib/types";

interface SuggestionCardProps {
  suggestion: Suggestion;
  index: number;
  minSize: number;
  maxSize: number;
  minOpinions: number;
  maxOpinions: number;
}

// Get gradient colors from CSS variables
function getCardGradient(index: number): string {
  const gradientIndex = index % 6;
  return `linear-gradient(to bottom right, var(--theme-card-gradient-${gradientIndex}-from), var(--theme-card-gradient-${gradientIndex}-via), var(--theme-card-gradient-${gradientIndex}-to))`;
}

function getAccentRingColor(index: number): string {
  const ringIndex = index % 6;
  return `var(--theme-accent-ring-${ringIndex})`;
}

const rotations = [
  "-rotate-6",
  "-rotate-2",
  "rotate-1",
  "rotate-3",
  "-rotate-1",
];

const classificationBadges: Record<
  Suggestion["peopleOpinions"][number]["classification"],
  { label: string; style: CSSProperties }
> = {
  good: {
    label: "Deep dive",
    style: {
      backgroundColor: "var(--theme-badge-sophisticated-bg)",
      color: "var(--theme-badge-sophisticated-text)",
    },
  },
  bad: {
    label: "Quick take",
    style: {
      backgroundColor: "var(--theme-badge-simple-bg)",
      color: "var(--theme-badge-simple-text)",
    },
  },
  neutral: {
    label: "Balanced",
    style: {
      backgroundColor: "var(--theme-badge-neutral-bg)",
      color: "var(--theme-badge-neutral-text)",
    },
  },
};

function normalize(value: number, min: number, max: number) {
  if (max === min) return 0.5;
  return (value - min) / (max - min);
}

export default function SuggestionCard({
  suggestion,
  index,
  minSize,
  maxSize,
  minOpinions,
  maxOpinions,
}: SuggestionCardProps) {
  const [isVisible, setIsVisible] = useState(false);
  const opinionCount = suggestion.peopleOpinions.length;
  const displayedOpinions = useMemo(
    () => suggestion.peopleOpinions.slice(0, 3),
    [suggestion.peopleOpinions],
  );
  const remainingCount = Math.max(0, opinionCount - displayedOpinions.length);

  const sizeWeight = normalize(suggestion.size, minSize, maxSize);
  const opinionWeight = normalize(opinionCount, minOpinions, maxOpinions);
  const weight = Math.min(
    1,
    Math.max(0, sizeWeight * 0.65 + opinionWeight * 0.35),
  );

  const fontSizeRem = 1.3 + weight * 1.7;
  const paddingY = 0.9 + weight * 1.1;
  const paddingX = 1.8 + weight * 1.6;
  const glowStrength = 16 + weight * 32;
  const blurAmount = 12 + weight * 12;

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, index * 110);

    return () => clearTimeout(timer);
  }, [index]);

  const gradientStyle = getCardGradient(index);
  const accentRingColor = getAccentRingColor(index);
  const rotation = rotations[index % rotations.length];

  const bubbleStyle: CSSProperties = {
    padding: `${paddingY}rem ${paddingX}rem`,
    background: gradientStyle,
    boxShadow: `0 ${glowStrength}px ${glowStrength * 2}px -${glowStrength / 1.6}px var(--theme-accent-blue)`,
  };

  const titleStyle: CSSProperties = {
    fontSize: `${fontSizeRem}rem`,
    textShadow: `0 ${blurAmount}px ${blurAmount * 1.2}px rgba(15, 23, 42, 0.35)`,
  };

  const highlightPro = suggestion.pros[0];
  const highlightContra = suggestion.contra[0];

  return (
    <div
      className={`transition-all duration-700 ease-out ${
        isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
      }`}
      style={{ transitionDelay: `${index * 70}ms` }}
    >
      <div className="relative">
        <div
          className="absolute inset-0 blur-3xl"
          style={{ 
            backgroundColor: accentRingColor,
            opacity: 0.35 + weight * 0.5,
          }}
        />
        <div
          className={`relative inline-flex items-center gap-4 rounded-full px-8 py-4 shadow-xl shadow-black/10 backdrop-blur transition-all duration-500 hover:-translate-y-1 hover:rotate-0 hover:shadow-2xl dark:shadow-black/30 ${rotation}`}
          style={bubbleStyle}
        >
          <span
            className="font-semibold leading-none tracking-tight text-white drop-shadow-xl"
            style={titleStyle}
          >
            {suggestion.title}
          </span>
          <span 
            className="hidden rounded-full px-3 py-1 text-xs font-medium uppercase tracking-[0.35em] sm:inline-flex"
            style={{ 
              backgroundColor: "rgba(255, 255, 255, 0.15)",
              color: "rgba(255, 255, 255, 0.9)",
            }}
          >
            {(suggestion.size * 100).toFixed(0)}% momentum
          </span>
          <div className="absolute -bottom-5 left-8 flex items-center gap-1">
            {displayedOpinions.map((opinion, i) => (
              <div
                key={opinion.name}
                className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full border text-xs font-semibold uppercase shadow-sm backdrop-blur"
                style={{ 
                  marginLeft: i === 0 ? 0 : -14 * i,
                  borderColor: "rgba(255, 255, 255, 0.6)",
                  backgroundColor: "rgba(255, 255, 255, 0.9)",
                  color: "var(--theme-fg-primary)",
                }}
                title={opinion.name}
              >
                {opinion.profilePicUrl ? (
                  <img
                    src={opinion.profilePicUrl}
                    alt={opinion.name}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  opinion.name[0]?.toUpperCase()
                )}
              </div>
            ))}
            {remainingCount > 0 && (
              <div 
                className="flex h-9 w-9 items-center justify-center rounded-full border text-xs font-semibold text-white"
                style={{
                  borderColor: "rgba(255, 255, 255, 0.6)",
                  backgroundColor: "rgba(255, 255, 255, 0.3)",
                }}
              >
                +{remainingCount}
              </div>
            )}
          </div>
        </div>
        <div 
          className="pointer-events-none absolute inset-x-10 -bottom-16 flex justify-between text-[11px] uppercase tracking-[0.32em]"
          style={{ color: "rgba(255, 255, 255, 0.7)" }}
        >
          {highlightPro && <span>+ {highlightPro}</span>}
          {highlightContra && <span>- {highlightContra}</span>}
        </div>
      </div>
      <div className="mt-8 flex flex-wrap items-center gap-2">
        {displayedOpinions.map((opinion) => {
          const badge = classificationBadges[opinion.classification];
          return (
            <span
              key={`${opinion.name}-${opinion.classification}`}
              className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium"
              style={badge.style}
            >
              <span 
                className="rounded-full px-2 py-0.5 text-[10px] uppercase tracking-[0.25em]"
                style={{
                  backgroundColor: "rgba(255, 255, 255, 0.6)",
                  color: "var(--theme-fg-primary)",
                }}
              >
                {opinion.name}
              </span>
              {badge.label}
            </span>
          );
        })}
      </div>
    </div>
  );
}
