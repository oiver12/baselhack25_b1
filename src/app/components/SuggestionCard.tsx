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

const palette = [
  "from-sky-400 via-sky-500 to-blue-600",
  "from-fuchsia-400 via-purple-500 to-indigo-600",
  "from-emerald-400 via-teal-500 to-cyan-500",
  "from-amber-400 via-orange-500 to-rose-500",
  "from-pink-500 via-rose-500 to-red-500",
  "from-cyan-400 via-blue-500 to-indigo-500",
];

const accentRings = [
  "bg-sky-200/30",
  "bg-purple-200/25",
  "bg-emerald-200/30",
  "bg-amber-200/25",
  "bg-pink-200/25",
  "bg-cyan-200/25",
];

const rotations = [
  "-rotate-6",
  "-rotate-2",
  "rotate-1",
  "rotate-3",
  "-rotate-1",
];

const classificationBadges: Record<
  Suggestion["peopleOpinions"][number]["classification"],
  { label: string; className: string }
> = {
  sophisticated: {
    label: "Deep dive",
    className:
      "bg-emerald-100/80 text-emerald-800 dark:bg-emerald-400/20 dark:text-emerald-200",
  },
  simple: {
    label: "Quick take",
    className:
      "bg-sky-100/80 text-sky-700 dark:bg-sky-400/20 dark:text-sky-200",
  },
  neutral: {
    label: "Balanced",
    className:
      "bg-slate-100/80 text-slate-700 dark:bg-slate-400/20 dark:text-slate-200",
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

  const gradient = palette[index % palette.length];
  const accent = accentRings[index % accentRings.length];
  const rotation = rotations[index % rotations.length];

  const bubbleStyle: CSSProperties = {
    padding: `${paddingY}rem ${paddingX}rem`,
    boxShadow: `0 ${glowStrength}px ${glowStrength * 2}px -${glowStrength / 1.6}px rgba(59, 130, 246, ${0.22 + weight * 0.35})`,
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
          className={`absolute inset-0 blur-3xl ${accent}`}
          style={{ opacity: 0.35 + weight * 0.5 }}
        />
        <div
          className={`relative inline-flex items-center gap-4 rounded-full bg-gradient-to-br ${gradient} px-8 py-4 shadow-xl shadow-black/10 backdrop-blur transition-all duration-500 hover:-translate-y-1 hover:rotate-0 hover:shadow-2xl dark:shadow-black/30 ${rotation}`}
          style={bubbleStyle}
        >
          <span
            className="font-semibold leading-none tracking-tight text-white drop-shadow-xl"
            style={titleStyle}
          >
            {suggestion.title}
          </span>
          <span className="hidden rounded-full bg-white/15 px-3 py-1 text-xs font-medium uppercase tracking-[0.35em] text-white/90 sm:inline-flex">
            {(suggestion.size * 100).toFixed(0)}% momentum
          </span>
          <div className="absolute -bottom-5 left-8 flex items-center gap-1">
            {displayedOpinions.map((opinion, i) => (
              <div
                key={opinion.name}
                className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full border border-white/60 bg-white/90 text-xs font-semibold uppercase text-slate-700 shadow-sm backdrop-blur"
                style={{ marginLeft: i === 0 ? 0 : -14 * i }}
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
              <div className="flex h-9 w-9 items-center justify-center rounded-full border border-white/60 bg-white/30 text-xs font-semibold text-white">
                +{remainingCount}
              </div>
            )}
          </div>
        </div>
        <div className="pointer-events-none absolute inset-x-10 -bottom-16 flex justify-between text-[11px] uppercase tracking-[0.32em] text-white/70">
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
              className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${badge.className}`}
            >
              <span className="rounded-full bg-white/60 px-2 py-0.5 text-[10px] uppercase tracking-[0.25em] text-slate-600 dark:bg-white/20 dark:text-white/80">
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
