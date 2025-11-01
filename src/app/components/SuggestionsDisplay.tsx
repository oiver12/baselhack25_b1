"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import type {
  Suggestion,
  SuggestionsResponse,
  SuggestionOpinion,
} from "@/lib/types";
import { Star, TrendingDown, ThumbsUp, ThumbsDown } from "lucide-react";
import Image from "next/image";
import * as d3 from "d3-force";

interface BubblePosition {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

interface ChildBubble {
  id: string;
  type: "opinion" | "pros" | "cons";
  angle: number;
  data?: SuggestionOpinion | string[];
  size: number;
}

interface SuggestionBubbleData {
  suggestion: Suggestion;
  position: BubblePosition;
  children: ChildBubble[];
  radius: number;
  isHovered: boolean;
  isMoving: boolean; // Track if bubble is currently animated
}

interface HoveredBubbleState {
  type: "opinion" | "pros" | "cons";
  data: SuggestionOpinion | string[];
  position: { x: number; y: number };
}

interface D3Node {
  x: number;
  y: number;
  vx?: number;
  vy?: number;
  radius: number;
  data: SuggestionBubbleData;
}

export default function SuggestionsDisplay() {
  const [suggestions, setSuggestions] = useState<SuggestionsResponse>([]);
  const [hoveredBubble, setHoveredBubble] = useState<HoveredBubbleState | null>(
    null,
  );
  const [hoveredParent, setHoveredParent] = useState<string | null>(null);
  const [stage, setStage] = useState(0);
  const [bubbleCount, setBubbleCount] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const bubbleDataRef = useRef<Map<string, SuggestionBubbleData>>(new Map());
  const previousDataRef = useRef<Map<string, string>>(new Map());
  const [, setRenderTrigger] = useState(0);

  // Fetch suggestions every second, incrementing stage
  useEffect(() => {
    async function fetchSuggestions(currentStage: number) {
      try {
        const response = await fetch(`/api/suggestions?stage=${currentStage}`);
        const data: SuggestionsResponse = await response.json();
        setSuggestions(data);
      } catch (error) {
        console.error("Failed to fetch suggestions:", error);
      }
    }

    fetchSuggestions(stage);
    const interval = setInterval(() => {
      setStage((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [stage]);

  // Initialize and update bubble data when suggestions change
  useEffect(() => {
    if (!containerRef.current || suggestions.length === 0) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const newBubbleData = new Map<string, SuggestionBubbleData>();

    // Sort suggestions by size (largest first) for better packing
    const sortedSuggestions = [...suggestions].sort((a, b) => b.size - a.size);

    sortedSuggestions.forEach((suggestion, index) => {
      const existingBubble = bubbleDataRef.current.get(suggestion.title);

      // Calculate bubble radius based on size (0-1) -> 40-160px (highly exaggerated)
      // Scale down if screen is too small
      const baseRadius = 40 + suggestion.size * 120;
      const maxAllowedRadius = Math.min(width, height) * 0.15; // Max 15% of smallest dimension
      const radius = Math.min(baseRadius, maxAllowedRadius);

      // Calculate child bubbles with better spacing
      const children: ChildBubble[] = [];
      const totalChildren =
        suggestion.peopleOpinions.length +
        (suggestion.pros.length > 0 ? 1 : 0) +
        (suggestion.contra.length > 0 ? 1 : 0);

      let childIndex = 0;

      // Add opinion bubbles
      suggestion.peopleOpinions.forEach((opinion) => {
        children.push({
          id: `${suggestion.title}-opinion-${opinion.name}`,
          type: "opinion",
          angle: (childIndex / totalChildren) * Math.PI * 2 - Math.PI / 2, // Start from top
          data: opinion,
          size: 25,
        });
        childIndex++;
      });

      // Add pros bubble
      if (suggestion.pros.length > 0) {
        children.push({
          id: `${suggestion.title}-pros`,
          type: "pros",
          angle: (childIndex / totalChildren) * Math.PI * 2 - Math.PI / 2,
          data: suggestion.pros,
          size: 30,
        });
        childIndex++;
      }

      // Add cons bubble
      if (suggestion.contra.length > 0) {
        children.push({
          id: `${suggestion.title}-cons`,
          type: "cons",
          angle: (childIndex / totalChildren) * Math.PI * 2 - Math.PI / 2,
          data: suggestion.contra,
          size: 30,
        });
        childIndex++;
      }

      // Determine if this is new data
      const dataHash = JSON.stringify({
        opinions: suggestion.peopleOpinions.length,
        pros: suggestion.pros.length,
        cons: suggestion.contra.length,
        size: suggestion.size.toFixed(2),
      });
      const previousHash = previousDataRef.current.get(suggestion.title);

      if (previousHash !== dataHash) {
        previousDataRef.current.set(suggestion.title, dataHash);
      }

      // Position calculation - use existing position or create new one with randomness
      let position: BubblePosition;
      if (existingBubble) {
        // Keep existing position
        position = existingBubble.position;
      } else {
        // Calculate the full radius including child bubbles
        const childDistance = 50;
        const maxChildSize = 30;
        const fullRadius = radius + childDistance + maxChildSize + 10;

        // Add randomness to initial position
        const randomDistance = Math.random() * 100 + 50; // Random offset 50-150px

        // New bubble - place in circular pattern with randomness
        if (index === 0) {
          // First bubble in center with small random offset
          position = {
            x: width / 2 + (Math.random() - 0.5) * 40,
            y: height / 2 + (Math.random() - 0.5) * 40,
            vx: 0,
            vy: 0,
          };
        } else {
          // Place new bubbles in expanding circles with randomness
          const ring = Math.floor(Math.log2(index + 1));
          const posInRing = index - (Math.pow(2, ring) - 1);
          const bubblesInRing = Math.pow(2, ring);
          const baseAngle = (posInRing / bubblesInRing) * Math.PI * 2;
          // Add random angle variation
          const angle = baseAngle + (Math.random() - 0.5) * 0.5;

          const avgFullRadius =
            (fullRadius + (40 + 0.5 * 120 + 50 + 30 + 10)) / 2;
          const baseDistance = (ring + 1) * avgFullRadius * 4.0;
          // Add random distance variation
          const distance = baseDistance + (Math.random() - 0.5) * avgFullRadius;

          let x =
            width / 2 +
            Math.cos(angle) * distance +
            (Math.random() - 0.5) * randomDistance;
          let y =
            height / 2 +
            Math.sin(angle) * distance +
            (Math.random() - 0.5) * randomDistance;

          // Clamp to ensure bubble stays fully visible
          x = Math.max(fullRadius, Math.min(width - fullRadius, x));
          y = Math.max(fullRadius, Math.min(height - fullRadius, y));

          position = {
            x,
            y,
            vx: 0,
            vy: 0,
          };
        }
      }

      const bubbleData = {
        suggestion,
        position,
        children,
        radius,
        isHovered: existingBubble?.isHovered || false,
        isMoving: !existingBubble, // New bubbles start as moving
      };

      newBubbleData.set(suggestion.title, bubbleData);
    });

    bubbleDataRef.current = newBubbleData;
    setBubbleCount(newBubbleData.size);
    setRenderTrigger((prev) => prev + 1);
  }, [suggestions]);

  // Advanced D3-Force physics simulation - PREVENTS ALL OVERLAPS
  // biome-ignore lint/correctness/useExhaustiveDependencies: We want to restart simulation when bubble count changes
  useEffect(() => {
    if (!containerRef.current || bubbleDataRef.current.size === 0) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Constants for child bubble spacing
    const childDistance = 50;
    const maxChildSize = 30;
    const padding = 15; // Extra padding between bubbles

    // Convert bubbles to d3 nodes
    const bubbles = Array.from(bubbleDataRef.current.values());
    const nodes: D3Node[] = bubbles.map((bubble) => ({
      ...bubble.position,
      radius: bubble.radius + childDistance + maxChildSize + padding, // Full extent + padding
      data: bubble,
    }));

    // Custom force to strongly repel overlapping nodes
    const separationForce = () => {
      return () => {
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            const nodeA = nodes[i];
            const nodeB = nodes[j];

            // Skip if either is hovered
            if (nodeA.data.isHovered || nodeB.data.isHovered) continue;

            const dx = nodeB.x - nodeA.x;
            const dy = nodeB.y - nodeA.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const minDistance = nodeA.radius + nodeB.radius;

            // If overlapping or too close, push apart (gentler force for faster settling)
            if (distance < minDistance) {
              const force = ((minDistance - distance) / distance) * 0.2;
              const fx = dx * force;
              const fy = dy * force;

              nodeA.vx = (nodeA.vx || 0) - fx;
              nodeA.vy = (nodeA.vy || 0) - fy;
              nodeB.vx = (nodeB.vx || 0) + fx;
              nodeB.vy = (nodeB.vy || 0) + fy;
            }
          }
        }
      };
    };

    // Create d3 force simulation with MAXIMUM collision prevention
    const simulation = d3
      .forceSimulation<D3Node>(nodes)
      // PRIMARY COLLISION FORCE - strongest settings
      .force(
        "collide",
        d3
          .forceCollide<D3Node>()
          .radius((d) => d.radius) // Use full radius
          .strength(1.0) // Maximum strength
          .iterations(5), // More iterations for precision
      )
      // CUSTOM SEPARATION FORCE - extra repulsion
      .force("separation", separationForce())
      // MANY-BODY FORCE - nodes repel each other
      .force(
        "charge",
        d3
          .forceManyBody<D3Node>()
          .strength((d) => -d.radius * 8) // Slightly reduced from 10 to prevent over-pushing
          .distanceMin(10)
          .distanceMax(400),
      )
      // CENTER FORCE - very gentle pull to center
      .force("center", d3.forceCenter(width / 2, height / 2).strength(0.003))
      // X FORCE - keep within horizontal bounds
      .force("x", d3.forceX<D3Node>(width / 2).strength(0.02))
      // Y FORCE - keep within vertical bounds
      .force("y", d3.forceY<D3Node>(height / 2).strength(0.02))
      // Very strong velocity decay for rapid settling
      .velocityDecay(0.7)
      // Very fast alpha decay - simulation settles in ~50 ticks
      .alphaDecay(0.1)
      // Minimal alpha target - simulation essentially stops
      .alphaTarget(0);

    // Update positions on each tick
    simulation.on("tick", () => {
      nodes.forEach((node) => {
        const bubble = node.data;

        // Skip physics for hovered bubbles
        if (bubble.isHovered) {
          // Reset node position to bubble's frozen position
          node.x = bubble.position.x;
          node.y = bubble.position.y;
          node.vx = 0;
          node.vy = 0;
          return;
        }

        // Check if nearby bubble is hovered - freeze if close
        const nearbyHovered = bubbles.some((other) => {
          if (!other.isHovered) return false;
          const dx = node.x - other.position.x;
          const dy = node.y - other.position.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          return (
            dist <
            node.radius +
              (other.radius + childDistance + maxChildSize + padding) +
              100
          );
        });

        if (nearbyHovered) {
          node.x = bubble.position.x;
          node.y = bubble.position.y;
          node.vx = 0;
          node.vy = 0;
          return;
        }

        // Clamp to bounds BEFORE updating bubble position
        const fullRadius =
          bubble.radius + childDistance + maxChildSize + padding;
        node.x = Math.max(fullRadius, Math.min(width - fullRadius, node.x));
        node.y = Math.max(fullRadius, Math.min(height - fullRadius, node.y));

        // Update bubble position from d3 simulation
        bubble.position.x = node.x;
        bubble.position.y = node.y;
        bubble.position.vx = node.vx ?? 0;
        bubble.position.vy = node.vy ?? 0;

        // Track movement for animation - very low threshold for rapid visual settling
        const speed = Math.sqrt(
          bubble.position.vx * bubble.position.vx +
            bubble.position.vy * bubble.position.vy,
        );
        bubble.isMoving = speed > 0.05; // Very low threshold - animations stop almost immediately
      });

      setRenderTrigger((prev) => prev + 1);
    });

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [bubbleCount]); // Re-run when number of bubbles changes

  const handleParentHover = useCallback(
    (title: string, isHovering: boolean) => {
      const bubble = bubbleDataRef.current.get(title);
      if (bubble) {
        bubble.isHovered = isHovering;
        setHoveredParent(isHovering ? title : null);
        setRenderTrigger((prev) => prev + 1);
      }
    },
    [],
  );

  const handleChildBubbleHover = useCallback(
    (child: ChildBubble, event: React.MouseEvent) => {
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;

      setHoveredBubble({
        type: child.type,
        data: child.data as SuggestionOpinion | string[],
        position: {
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
        },
      });
    },
    [],
  );

  const handleChildBubbleLeave = useCallback(() => {
    setHoveredBubble(null);
  }, []);

  if (suggestions.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div 
            className="w-16 h-16 border-4 rounded-full animate-spin"
            style={{
              borderColor: "var(--theme-loading-border)",
              borderTopColor: "var(--theme-loading-border-active)",
            }}
          />
          <div 
            className="text-lg font-medium"
            style={{ color: "var(--theme-fg-secondary)" }}
          >
            Loading suggestions...
          </div>
        </div>
      </div>
    );
  }

  const bubbleData = Array.from(bubbleDataRef.current.values());

  return (
    <div
      ref={containerRef}
      className="w-full h-full relative overflow-hidden rounded-3xl shadow-2xl"
      style={{
        background: "linear-gradient(to bottom right, var(--theme-bg-secondary), var(--theme-bg-primary), var(--theme-bg-secondary))",
      }}
    >
      {/* Ambient background effects */}
      <div className="absolute inset-0 opacity-30 pointer-events-none">
        <div 
          className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl animate-pulse"
          style={{ 
            backgroundColor: "var(--theme-accent-blue)",
            opacity: "0.2",
          }}
        />
        <div
          className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full blur-3xl animate-pulse"
          style={{ 
            animationDelay: "1s",
            backgroundColor: "var(--theme-accent-purple)",
            opacity: "0.2",
          }}
        />
        <div
          className="absolute top-1/2 right-1/3 w-80 h-80 rounded-full blur-3xl animate-pulse"
          style={{ 
            animationDelay: "2s",
            backgroundColor: "var(--theme-accent-pink)",
            opacity: "0.2",
          }}
        />
      </div>

      {/* biome-ignore lint/a11y/noSvgWithoutTitle: aria-label provides accessible name */}
      <svg
        className="w-full h-full relative z-10"
        aria-label="Suggestion bubbles visualization"
      >
        <defs>
          {/* Modern gradients */}
          <linearGradient
            id="gradient-blue"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
          >
            <stop offset="0%" stopColor="var(--theme-bubble-primary-from)" stopOpacity="1" />
            <stop offset="50%" stopColor="var(--theme-bubble-primary-via)" stopOpacity="1" />
            <stop offset="100%" stopColor="var(--theme-bubble-primary-to)" stopOpacity="1" />
          </linearGradient>
          <linearGradient
            id="gradient-green"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
          >
            <stop offset="0%" stopColor="var(--theme-bubble-pros-from)" stopOpacity="1" />
            <stop offset="100%" stopColor="var(--theme-bubble-pros-to)" stopOpacity="1" />
          </linearGradient>
          <linearGradient id="gradient-red" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--theme-bubble-cons-from)" stopOpacity="1" />
            <stop offset="100%" stopColor="var(--theme-bubble-cons-to)" stopOpacity="1" />
          </linearGradient>
          <linearGradient
            id="gradient-opinion"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
          >
            <stop offset="0%" stopColor="var(--theme-bubble-opinion-from)" stopOpacity="1" />
            <stop offset="100%" stopColor="var(--theme-bubble-opinion-to)" stopOpacity="1" />
          </linearGradient>
          <linearGradient id="glass-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="var(--theme-glass-white)" stopOpacity="0.8" />
            <stop offset="100%" stopColor="var(--theme-glass-white)" stopOpacity="0" />
          </linearGradient>

          {/* Glow filters */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="soft-glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {bubbleData.map((bubble) => {
          const { suggestion, position, children, radius, isMoving } = bubble;
          const isParentHovered = hoveredParent === suggestion.title;
          const childDistance = radius + 50;

          return (
            <g key={suggestion.title}>
              {/* Animated glow ring when moving - fancy effect! */}
              {isMoving && (
                <>
                  <circle
                    cx={position.x}
                    cy={position.y}
                    r={radius + childDistance + 80}
                    fill="none"
                    stroke="var(--theme-bubble-primary-from)"
                    strokeWidth="3"
                    opacity="0.2"
                    className="animate-pulse"
                  >
                    <animate
                      attributeName="r"
                      values={`${radius + childDistance + 60};${radius + childDistance + 90};${radius + childDistance + 60}`}
                      dur="2s"
                      repeatCount="indefinite"
                    />
                    <animate
                      attributeName="opacity"
                      values="0.3;0.1;0.3"
                      dur="2s"
                      repeatCount="indefinite"
                    />
                  </circle>
                  <circle
                    cx={position.x}
                    cy={position.y}
                    r={radius + 15}
                    fill="none"
                    stroke="var(--theme-glass-white)"
                    strokeWidth="2"
                    opacity="0.4"
                    style={{ stroke: "var(--theme-glass-white)" }}
                  >
                    <animate
                      attributeName="r"
                      values={`${radius + 10};${radius + 20};${radius + 10}`}
                      dur="1.5s"
                      repeatCount="indefinite"
                    />
                    <animate
                      attributeName="opacity"
                      values="0.5;0.2;0.5"
                      dur="1.5s"
                      repeatCount="indefinite"
                    />
                  </circle>
                </>
              )}

              {/* Outer glow ring when hovered */}
              {isParentHovered && (
                <circle
                  cx={position.x}
                  cy={position.y}
                  r={radius + childDistance + 60}
                  fill="none"
                  stroke="var(--theme-bubble-primary-from)"
                  strokeWidth="2"
                  opacity="0.15"
                  className="animate-pulse"
                >
                  <title>Suggestion group boundary</title>
                </circle>
              )}

              {/* Connection area - subtle background circle */}
              {isParentHovered && (
                <circle
                  cx={position.x}
                  cy={position.y}
                  r={radius + childDistance}
                  fill="var(--theme-glass-white)"
                  fillOpacity="0.05"
                  className="transition-all duration-300"
                />
              )}

              {/* Lines connecting parent to children - enhanced */}
              {children.map((child) => {
                const childX =
                  position.x + Math.cos(child.angle) * childDistance;
                const childY =
                  position.y + Math.sin(child.angle) * childDistance;

                return (
                  <line
                    key={child.id}
                    x1={position.x}
                    y1={position.y}
                    x2={childX}
                    y2={childY}
                    stroke="var(--theme-bubble-primary-from)"
                    strokeWidth={isParentHovered ? "3" : "2"}
                    opacity={isParentHovered ? "0.5" : "0.2"}
                    className="transition-all duration-300"
                    strokeDasharray={isParentHovered ? "0" : "5,5"}
                  />
                );
              })}

              {/* Main suggestion bubble */}
              <g className="transition-all duration-300">
                {/* Invisible larger hover area */}
                {/* biome-ignore lint/a11y/noStaticElementInteractions: SVG circle used for visual graph interaction */}
                <circle
                  cx={position.x}
                  cy={position.y}
                  r={radius + 10}
                  fill="transparent"
                  className="cursor-pointer"
                  onMouseEnter={() => handleParentHover(suggestion.title, true)}
                  onMouseLeave={() =>
                    handleParentHover(suggestion.title, false)
                  }
                  aria-label={suggestion.title}
                />

                {/* Outer ring */}
                <circle
                  cx={position.x}
                  cy={position.y}
                  r={radius + 6}
                  fill="var(--theme-glass-white)"
                  fillOpacity="0.3"
                  className="pointer-events-none"
                  filter={isParentHovered ? "url(#glow)" : ""}
                />

                {/* Main bubble */}
                <circle
                  cx={position.x}
                  cy={position.y}
                  r={radius}
                  fill="url(#gradient-blue)"
                  className={`transition-all duration-300 pointer-events-none ${isParentHovered ? "drop-shadow-2xl" : "drop-shadow-lg"} ${isMoving ? "drop-shadow-2xl" : ""}`}
                  filter={isParentHovered || isMoving ? "url(#soft-glow)" : ""}
                  style={{
                    transform: isParentHovered ? "scale(1.05)" : "scale(1)",
                    transformOrigin: `${position.x}px ${position.y}px`,
                  }}
                  opacity={isMoving ? "0.95" : "1"}
                />

                {/* Glass effect overlay */}
                <circle
                  cx={position.x}
                  cy={position.y}
                  r={radius}
                  fill="url(#glass-gradient)"
                  opacity="0.3"
                  className="pointer-events-none"
                />

                <foreignObject
                  x={position.x - radius}
                  y={position.y - radius}
                  width={radius * 2}
                  height={radius * 2}
                  className="pointer-events-none"
                >
                  <div className="w-full h-full flex items-center justify-center p-6">
                    <div
                      className="text-center font-bold leading-snug break-words drop-shadow-md"
                      style={{
                        fontSize: `${Math.max(12, Math.min(24, radius * 0.25 - suggestion.title.length * 0.15))}px`,
                        maxHeight: `${radius * 1.4}px`,
                        color: "var(--theme-glass-white)",
                      }}
                    >
                      {suggestion.title}
                    </div>
                  </div>
                </foreignObject>

                {/* Size indicator - small badge positioned outside bubble */}
                <g>
                  <circle
                    cx={position.x}
                    cy={position.y + radius + 15}
                    r={18}
                    fill="var(--theme-glass-white)"
                    fillOpacity="0.25"
                  >
                    <title>
                      Suggestion strength: {Math.round(suggestion.size * 100)}%
                    </title>
                  </circle>
                  <foreignObject
                    x={position.x - 18}
                    y={position.y + radius - 3}
                    width={36}
                    height={36}
                    className="pointer-events-none"
                  >
                    <div className="w-full h-full flex items-center justify-center">
                      <span 
                        className="text-xs font-bold drop-shadow"
                        style={{ color: "var(--theme-glass-white)" }}
                      >
                        {Math.round(suggestion.size * 100)}%
                      </span>
                    </div>
                  </foreignObject>
                </g>
              </g>

              {/* Child bubbles - enhanced */}
              {children.map((child) => {
                const childX =
                  position.x + Math.cos(child.angle) * childDistance;
                const childY =
                  position.y + Math.sin(child.angle) * childDistance;

                let gradient = "url(#gradient-opinion)";
                if (child.type === "pros") gradient = "url(#gradient-green)";
                if (child.type === "cons") gradient = "url(#gradient-red)";

                return (
                  <g
                    key={child.id}
                    className="transition-all duration-300"
                    style={{
                      opacity: isParentHovered ? 1 : 0.7,
                    }}
                  >
                    {/* Invisible larger hover area */}
                    {/* biome-ignore lint/a11y/noStaticElementInteractions: SVG circle used for visual graph interaction */}
                    <circle
                      cx={childX}
                      cy={childY}
                      r={child.size + 10}
                      fill="transparent"
                      className="cursor-pointer"
                      onMouseEnter={(e) => {
                        handleParentHover(suggestion.title, true);
                        handleChildBubbleHover(child, e);
                      }}
                      onMouseLeave={() => {
                        handleChildBubbleLeave();
                        handleParentHover(suggestion.title, false);
                      }}
                      aria-label={child.type}
                    />

                    {/* Outer ring for child */}
                    <circle
                      cx={childX}
                      cy={childY}
                      r={child.size + 4}
                      fill="var(--theme-glass-white)"
                      fillOpacity="0.3"
                      className="pointer-events-none"
                    />

                    {/* Child bubble */}
                    <circle
                      cx={childX}
                      cy={childY}
                      r={child.size}
                      fill={gradient}
                      className="drop-shadow-lg pointer-events-none transition-all"
                      filter="url(#soft-glow)"
                    />

                    {/* Glass overlay */}
                    <circle
                      cx={childX}
                      cy={childY}
                      r={child.size}
                      fill="var(--theme-glass-white)"
                      opacity="0.2"
                      className="pointer-events-none"
                    />

                    {/* Profile image for opinions */}
                    {child.type === "opinion" &&
                      child.data &&
                      typeof child.data === "object" &&
                      "profilePicUrl" in child.data && (
                        <foreignObject
                          x={childX - child.size}
                          y={childY - child.size}
                          width={child.size * 2}
                          height={child.size * 2}
                          className="pointer-events-none"
                        >
                          <div className="w-full h-full flex items-center justify-center p-1">
                            <div className="relative w-full h-full">
                              <Image
                                src={child.data.profilePicUrl}
                                alt={child.data.name}
                                width={child.size * 2}
                                height={child.size * 2}
                                className="rounded-full w-full h-full object-cover ring-2 ring-white/50"
                                unoptimized
                              />
                              {child.data.classification ===
                                "sophisticated" && (
                                <div 
                                  className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center shadow-lg"
                                  style={{ backgroundColor: "var(--theme-accent-yellow)" }}
                                >
                                  <Star className="w-2.5 h-2.5 text-white fill-white" />
                                </div>
                              )}
                              {child.data.classification === "simple" && (
                                <div 
                                  className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center shadow-lg"
                                  style={{ backgroundColor: "var(--theme-accent-red)" }}
                                >
                                  <TrendingDown className="w-2.5 h-2.5 text-white" />
                                </div>
                              )}
                            </div>
                          </div>
                        </foreignObject>
                      )}

                    {child.type === "pros" && (
                      <foreignObject
                        x={childX - child.size}
                        y={childY - child.size}
                        width={child.size * 2}
                        height={child.size * 2}
                        className="pointer-events-none"
                      >
                        <div className="w-full h-full flex items-center justify-center">
                          <ThumbsUp className="w-4 h-4 text-white drop-shadow-lg" />
                        </div>
                      </foreignObject>
                    )}

                    {child.type === "cons" && (
                      <foreignObject
                        x={childX - child.size}
                        y={childY - child.size}
                        width={child.size * 2}
                        height={child.size * 2}
                        className="pointer-events-none"
                      >
                        <div className="w-full h-full flex items-center justify-center">
                          <ThumbsDown className="w-4 h-4 text-white drop-shadow-lg" />
                        </div>
                      </foreignObject>
                    )}
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>

      {/* Hover tooltip - modern card */}
      {hoveredBubble && (
        <div
          className="absolute z-50 pointer-events-none"
          style={{
            left: `${hoveredBubble.position.x + 30}px`,
            top: `${hoveredBubble.position.y}px`,
            transform: "translateY(-50%)",
          }}
        >
          <div 
            className="backdrop-blur-xl rounded-2xl shadow-2xl border p-5 max-w-sm animate-in fade-in zoom-in-95 duration-200"
            style={{
              backgroundColor: "var(--theme-message-bg)",
              borderColor: "var(--theme-message-border)",
            }}
          >
            {hoveredBubble.type === "opinion" &&
              typeof hoveredBubble.data === "object" &&
              "name" in hoveredBubble.data && (
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <Image
                        src={hoveredBubble.data.profilePicUrl}
                        alt={hoveredBubble.data.name}
                        width={48}
                        height={48}
                        className="rounded-full ring-2 ring-indigo-400/50"
                        unoptimized
                      />
                      <div 
                        className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center"
                        style={{ backgroundColor: "var(--theme-bg-primary)" }}
                      >
                        {hoveredBubble.data.classification ===
                          "sophisticated" && (
                          <Star 
                            className="w-3 h-3 fill-yellow-500" 
                            style={{ color: "var(--theme-accent-yellow)" }}
                          />
                        )}
                        {hoveredBubble.data.classification === "simple" && (
                          <TrendingDown 
                            className="w-3 h-3" 
                            style={{ color: "var(--theme-accent-red)" }}
                          />
                        )}
                      </div>
                    </div>
                    <div>
                      <div 
                        className="font-bold"
                        style={{ color: "var(--theme-fg-primary)" }}
                      >
                        {hoveredBubble.data.name}
                      </div>
                      <div 
                        className="text-xs capitalize"
                        style={{ color: "var(--theme-fg-secondary)" }}
                      >
                        {hoveredBubble.data.classification} opinion
                      </div>
                    </div>
                  </div>
                  <p 
                    className="text-sm leading-relaxed"
                    style={{ color: "var(--theme-fg-secondary)" }}
                  >
                    "{hoveredBubble.data.message}"
                  </p>
                </div>
              )}

            {hoveredBubble.type === "pros" &&
              Array.isArray(hoveredBubble.data) && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-8 h-8 rounded-lg bg-gradient-to-br flex items-center justify-center"
                      style={{
                        background: `linear-gradient(to bottom right, var(--theme-bubble-pros-from), var(--theme-bubble-pros-to))`,
                      }}
                    >
                      <ThumbsUp className="w-4 h-4 text-white" />
                    </div>
                    <div 
                      className="font-bold text-lg"
                      style={{ color: "var(--theme-accent-green)" }}
                    >
                      Advantages
                    </div>
                  </div>
                  <ul className="space-y-2">
                    {hoveredBubble.data.map((pro: string) => (
                      <li
                        key={`pro-${pro.substring(0, 20)}`}
                        className="flex items-start gap-2 text-sm"
                        style={{ color: "var(--theme-fg-secondary)" }}
                      >
                        <span 
                          className="font-bold mt-0.5"
                          style={{ color: "var(--theme-accent-green)" }}
                        >
                          ✓
                        </span>
                        <span>{pro}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            {hoveredBubble.type === "cons" &&
              Array.isArray(hoveredBubble.data) && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-8 h-8 rounded-lg bg-gradient-to-br flex items-center justify-center"
                      style={{
                        background: `linear-gradient(to bottom right, var(--theme-bubble-cons-from), var(--theme-bubble-cons-to))`,
                      }}
                    >
                      <ThumbsDown className="w-4 h-4 text-white" />
                    </div>
                    <div 
                      className="font-bold text-lg"
                      style={{ color: "var(--theme-accent-red)" }}
                    >
                      Challenges
                    </div>
                  </div>
                  <ul className="space-y-2">
                    {hoveredBubble.data.map((con: string) => (
                      <li
                        key={`con-${con.substring(0, 20)}`}
                        className="flex items-start gap-2 text-sm"
                        style={{ color: "var(--theme-fg-secondary)" }}
                      >
                        <span 
                          className="font-bold mt-0.5"
                          style={{ color: "var(--theme-accent-red)" }}
                        >
                          ✗
                        </span>
                        <span>{con}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
          </div>
        </div>
      )}
    </div>
  );
}
