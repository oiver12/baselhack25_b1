"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import type {
  Suggestion,
  SuggestionsResponse,
  SuggestionOpinion,
} from "@/lib/types";
import { Star } from "lucide-react";
import Image from "next/image";
import * as d3 from "d3-force";
import * as d3Drag from "d3-drag";
import * as d3Select from "d3-selection";
import AnalyticsDashboard from "./AnalyticsDashboard";

// Toggle between mock and real backend
const USE_MOCK_BACKEND = true;

interface BubblePosition {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

interface ChildBubble {
  id: string;
  type: "opinion";
  angle: number;
  data: SuggestionOpinion;
  size: number;
}

interface SuggestionBubbleData {
  suggestion: Suggestion;
  position: BubblePosition;
  children: ChildBubble[];
  radius: number;
  isHovered: boolean;
  isMoving: boolean; // Track if bubble is currently animated
  isNew: boolean; // Track if bubble was just added (for fade-in)
}

interface HoveredBubbleState {
  type: "opinion";
  data: SuggestionOpinion;
  position: { x: number; y: number };
}

interface D3Node {
  x: number;
  y: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
  actualRadius: number; // For collisions - just the bubble radius
  fullRadius: number; // For bounds/positioning - includes children
  data: SuggestionBubbleData;
}

interface ChildCollisionNode {
  x: number;
  y: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
  radius: number; // Actual child bubble size (25-30px)
  parentNode: D3Node; // Reference to parent
  childId: string;
  idealAngle: number;
  idealDistance: number;
}

interface ChildD3Node {
  x: number;
  y: number;
  fx?: number | null;
  fy?: number | null;
  parentTitle: string;
  childId: string;
  idealAngle: number;
  idealDistance: number;
}

interface SuggestionsDisplayProps {
  questionId: string;
}

export default function SuggestionsDisplay({ questionId }: SuggestionsDisplayProps) {
  const [suggestions, setSuggestions] = useState<SuggestionsResponse>([]);
  const [questionText, setQuestionText] = useState<string>("");
  const [hoveredBubble, setHoveredBubble] = useState<HoveredBubbleState | null>(
    null,
  );
  const [hoveredParent, setHoveredParent] = useState<string | null>(null);
  const [bubbleCount, setBubbleCount] = useState(0);
  const [stage, setStage] = useState(0); // Local state for stage, starts at 0
  const containerRef = useRef<HTMLDivElement>(null);
  const bubbleDataRef = useRef<Map<string, SuggestionBubbleData>>(new Map());
  const previousDataRef = useRef<Map<string, string>>(new Map());
  const [, setRenderTrigger] = useState(0);
  const simulationRef = useRef<d3.Simulation<D3Node, undefined> | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const draggedBubbleRef = useRef<{ type: "parent" | "child"; id: string; parentTitle?: string } | null>(null);
  const childDragSpringForceRef = useRef<{ parentNode: D3Node; childX: number; childY: number; strength: number } | null>(null);
  const [draggedBubbleId, setDraggedBubbleId] = useState<string | null>(null);

  // Auto-increment stage parameter every 2 seconds
  useEffect(() => {
    if (!USE_MOCK_BACKEND) return; // Only auto-increment for mock backend
    
    const interval = setInterval(() => {
      setStage((prevStage) => prevStage + 1);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // Fetch question text
  useEffect(() => {
    if (!questionId) return;

    async function fetchQuestion() {
      try {
        if (USE_MOCK_BACKEND) {
          // Use mock question for mock backend
          setQuestionText("How should we improve the city's public transportation system to better serve all residents?");
        } else {
          const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
          const response = await fetch(`${backendUrl}/api/questions/${questionId}`);
          if (response.ok) {
            const data = await response.json();
            setQuestionText(data.question || "");
          }
        }
      } catch (error) {
        console.error("Failed to fetch question:", error);
      }
    }

    fetchQuestion();
  }, [questionId]);

  // Fetch suggestions from Python backend every second
  useEffect(() => {
    if (!questionId) return;

    async function fetchSuggestions() {
      try {
        if (USE_MOCK_BACKEND) {
          // Use mock backend - Next.js API route
          const response = await fetch(`/api/suggestions?stage=${stage}`);
          if (!response.ok) {
            throw new Error(`Mock backend failed: ${response.statusText}`);
          }
          const data: SuggestionsResponse = await response.json();
          setSuggestions(data || []);
        } else {
          // Use real backend
          const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
          
          // Call messages endpoint first (ignore output, just needs to be called)
          await fetch(`${backendUrl}/api/messages`).catch(() => {
            // Ignore errors from messages endpoint
          });
          
          // Call Python backend directly - baselhack25_backend/app/api/routes/dashboard.py
          const response = await fetch(`${backendUrl}/api/dashboard/${questionId}`);
          if (!response.ok) {
            if (response.status === 404) {
              console.log("Question not found yet, waiting...");
              return;
            }
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || errorData.detail || `Failed: ${response.statusText}`);
          }
          const data: SuggestionsResponse = await response.json();
          setSuggestions(data || []);
        }
      } catch (error) {
        console.error("Failed to fetch suggestions:", error);
      }
    }

    fetchSuggestions();
    const interval = setInterval(fetchSuggestions, 1000);

    return () => clearInterval(interval);
  }, [questionId, stage]);

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
      const totalChildren = suggestion.peopleOpinions.length;

      // Create a consistent random starting angle for this specific suggestion
      // Use a hash of the title to get a deterministic but varied starting angle
      const titleHash = suggestion.title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
      // Vary starting angle from -90° to 270° (full circle rotation)
      const baseStartAngle = (titleHash % 360) * (Math.PI / 180) - Math.PI / 2;
      
      // Add some randomness to spacing between children (not perfectly even)
      const spacingVariation = 0.2; // 20% variation in spacing

      let childIndex = 0;

      // Helper function to get deterministic spacing offset based on child ID
      const getSpacingOffset = (childId: string, index: number) => {
        const idHash = childId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        const normalized = (idHash % 100) / 100; // 0-1
        return (normalized - 0.5) * spacingVariation * (Math.PI * 2 / totalChildren);
      };

      // Add opinion bubbles
      suggestion.peopleOpinions.forEach((opinion) => {
        const childId = `${suggestion.title}-opinion-${opinion.name}`;
        const baseAngle = (childIndex / totalChildren) * Math.PI * 2;
        const spacingOffset = getSpacingOffset(childId, childIndex);
        children.push({
          id: childId,
          type: "opinion",
          angle: baseAngle + baseStartAngle + spacingOffset,
          data: opinion,
          size: 25,
        });
        childIndex++;
      });

      // Determine if this is new data
      const dataHash = JSON.stringify({
        opinions: suggestion.peopleOpinions.length,
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

        // Header exclusion zone for initial placement - ensure full bubble radius is below header
        const headerExclusionHeight = 130; // Header height + extra padding to account for bubble radii

        // New bubble - place in circular pattern with randomness
        if (index === 0) {
          // First bubble in center with small random offset, but below header (center + radius)
          position = {
            x: width / 2 + (Math.random() - 0.5) * 40,
            y: Math.max(height / 2 + (Math.random() - 0.5) * 40, headerExclusionHeight + fullRadius),
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

          // Clamp to ensure bubble stays fully visible and below header (bubble center must be headerHeight + fullRadius from top)
          x = Math.max(fullRadius, Math.min(width - fullRadius, x));
          y = Math.max(headerExclusionHeight + fullRadius, Math.min(height - fullRadius, y));

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
        isNew: !existingBubble, // Track if this is a new bubble for fade-in
      };

      newBubbleData.set(suggestion.title, bubbleData);
    });

    bubbleDataRef.current = newBubbleData;
    setBubbleCount(newBubbleData.size);
    setRenderTrigger((prev) => prev + 1);

    // Mark new bubbles as "no longer new" after fade-in completes
    setTimeout(() => {
      bubbleDataRef.current.forEach((bubble) => {
        if (bubble.isNew) {
          bubble.isNew = false;
        }
      });
      setRenderTrigger((prev) => prev + 1);
    }, 600);
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

    // Get analytics exclusion zone from container
    let exclusionZone: { x: number; y: number; width: number; height: number } | null = null;
    try {
      const exclusionData = container.getAttribute('data-analytics-exclusion');
      if (exclusionData) {
        const parsed = JSON.parse(exclusionData);
        if (parsed.width > 0 && parsed.height > 0) {
          // Add padding around analytics panel
          const exclusionPadding = 30;
          exclusionZone = {
            x: parsed.x - exclusionPadding,
            y: parsed.y - exclusionPadding,
            width: parsed.width + exclusionPadding * 2,
            height: parsed.height + exclusionPadding * 2,
          };
        }
      }
    } catch (e) {
      // Ignore parse errors
    }

    // Header exclusion zone - prevent bubbles from going into header area
    // Make it larger to account for full bubble radius
    const headerHeight = 80; // Approximate header height with padding
    const headerExclusionZone = {
      x: 0,
      y: 0,
      width: width,
      height: headerHeight + 50, // Extra padding to account for bubble radii
    };

    // Convert bubbles to d3 nodes
    const bubbles = Array.from(bubbleDataRef.current.values());
    const nodes: D3Node[] = bubbles.map((bubble) => ({
      ...bubble.position,
      actualRadius: bubble.radius, // For collisions - just the bubble
      fullRadius: bubble.radius + childDistance + maxChildSize + padding, // For bounds/positioning
      data: bubble,
    }));

    // Create collision nodes for child bubbles
    const childNodes: ChildCollisionNode[] = [];
    bubbles.forEach((bubble) => {
      const parentNode = nodes.find((n) => n.data.suggestion.title === bubble.suggestion.title);
      if (!parentNode) return;

      bubble.children.forEach((child) => {
        const childX = parentNode.x + Math.cos(child.angle) * (bubble.radius + 50);
        const childY = parentNode.y + Math.sin(child.angle) * (bubble.radius + 50);
        
        childNodes.push({
          x: childX,
          y: childY,
          vx: 0,
          vy: 0,
          radius: child.size, // Actual child bubble size
          parentNode,
          childId: child.id,
          idealAngle: child.angle,
          idealDistance: bubble.radius + 50,
        });
      });
    });

    // Custom force to strongly repel overlapping nodes (parent-parent collisions)
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
            const minDistance = nodeA.actualRadius + nodeB.actualRadius;

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

    // Custom force for child-parent collisions
    const childParentCollisionForce = () => {
      return () => {
        childNodes.forEach((childNode) => {
          const parent = childNode.parentNode;
          
          // Skip if parent is hovered or fixed
          if (parent.data.isHovered || parent.fx !== null || parent.fy !== null) return;

          const dx = childNode.x - parent.x;
          const dy = childNode.y - parent.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          const minDistance = childNode.radius + parent.actualRadius + 5; // Small threshold to allow orbiting

          if (distance < minDistance) {
            const force = ((minDistance - distance) / distance) * 0.3;
            const fx = dx * force;
            const fy = dy * force;

            // Push parent away (child position is updated from parent)
            parent.vx = (parent.vx || 0) - fx * 0.5;
            parent.vy = (parent.vy || 0) - fy * 0.5;
          }
        });
      };
    };

    // Custom force for child-child collisions
    const childChildCollisionForce = () => {
      return () => {
        for (let i = 0; i < childNodes.length; i++) {
          for (let j = i + 1; j < childNodes.length; j++) {
            const childA = childNodes[i];
            const childB = childNodes[j];

            // Skip if they have the same parent (they're managed by parent position)
            if (childA.parentNode === childB.parentNode) continue;

            const dx = childB.x - childA.x;
            const dy = childB.y - childA.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const minDistance = childA.radius + childB.radius;

            if (distance < minDistance) {
              const force = ((minDistance - distance) / distance) * 0.15;
              const fx = dx * force;
              const fy = dy * force;

              // Push parents away
              childA.parentNode.vx = (childA.parentNode.vx || 0) - fx * 0.3;
              childA.parentNode.vy = (childA.parentNode.vy || 0) - fy * 0.3;
              childB.parentNode.vx = (childB.parentNode.vx || 0) + fx * 0.3;
              childB.parentNode.vy = (childB.parentNode.vy || 0) + fy * 0.3;
            }
          }
        }
      };
    };

    // Custom force for child-other-parent collisions
    // Ensures child bubbles don't overlap with other parent bubbles using actual hitboxes
    const childOtherParentCollisionForce = () => {
      return () => {
        childNodes.forEach((childNode) => {
          nodes.forEach((otherParent) => {
            // Skip if it's the child's own parent (handled by childParentCollisionForce)
            if (otherParent === childNode.parentNode) return;
            
            // Skip if either parent is hovered or fixed (being dragged)
            if (
              childNode.parentNode.data.isHovered ||
              childNode.parentNode.fx !== null ||
              childNode.parentNode.fy !== null ||
              otherParent.data.isHovered ||
              otherParent.fx !== null ||
              otherParent.fy !== null
            ) {
              return;
            }

            // Check collision between child and other parent using actual radii
            const dx = childNode.x - otherParent.x;
            const dy = childNode.y - otherParent.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const minDistance = childNode.radius + otherParent.actualRadius;

            if (distance < minDistance) {
              // Calculate repulsion force
              const force = ((minDistance - distance) / distance) * 0.25;
              const fx = dx * force;
              const fy = dy * force;

              // Push both parent bubbles away from each other
              // Child's parent moves away from other parent
              childNode.parentNode.vx = (childNode.parentNode.vx || 0) - fx * 0.5;
              childNode.parentNode.vy = (childNode.parentNode.vy || 0) - fy * 0.5;
              
              // Other parent moves away from child
              otherParent.vx = (otherParent.vx || 0) + fx * 0.5;
              otherParent.vy = (otherParent.vy || 0) + fy * 0.5;
            }
          });
        });
      };
    };

    // Custom spring force for child bubble dragging
    const childDragSpringForce = () => {
      return () => {
        const spring = childDragSpringForceRef.current;
        if (!spring) return;
        
        const { parentNode, childX, childY, strength } = spring;
        
        // Only apply if parent is not fixed
        if (parentNode.fx === null && parentNode.fy === null) {
          const dx = childX - parentNode.x;
          const dy = childY - parentNode.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance > 0) {
            // Apply spring force toward child position
            const force = distance * strength;
            parentNode.vx = (parentNode.vx || 0) + (dx / distance) * force;
            parentNode.vy = (parentNode.vy || 0) + (dy / distance) * force;
          }
        }
      };
    };

    // Create d3 force simulation with precise collision prevention
    const simulation = d3
      .forceSimulation<D3Node>(nodes)
      // PRIMARY COLLISION FORCE - use actual radius for collisions
      .force(
        "collide",
        d3
          .forceCollide<D3Node>()
          .radius((d) => d.actualRadius) // Use actual bubble radius, not extended
          .strength(1.0) // Maximum strength
          .iterations(5), // More iterations for precision
      )
      // CUSTOM SEPARATION FORCE - extra repulsion between parents
      .force("separation", separationForce())
      // CHILD-PARENT COLLISION - prevent children from overlapping their own parent
      .force("childParentCollision", childParentCollisionForce())
      // CHILD-OTHER-PARENT COLLISION - prevent children from overlapping other parents
      .force("childOtherParentCollision", childOtherParentCollisionForce())
      // CHILD-CHILD COLLISION - prevent children from overlapping each other
      .force("childChildCollision", childChildCollisionForce())
      // SPRING FORCE - for child bubble dragging (only active when child is dragged)
      .force("childDragSpring", childDragSpringForce())
      // MANY-BODY FORCE - nodes repel each other based on actual radius
      .force(
        "charge",
        d3
          .forceManyBody<D3Node>()
          .strength((d) => -d.actualRadius * 8) // Scale with actual radius
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

    // Store simulation reference for drag handlers
    simulationRef.current = simulation;

    // Update positions on each tick
    simulation.on("tick", () => {
      nodes.forEach((node) => {
        const bubble = node.data;

        // Skip physics for hovered or dragged bubbles
        const isBeingDragged = draggedBubbleRef.current?.type === "parent" && 
          draggedBubbleRef.current.id === bubble.suggestion.title;
        if (bubble.isHovered && !isBeingDragged) {
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
          const otherNode = nodes.find((n) => n.data.suggestion.title === other.suggestion.title);
          if (!otherNode) return false;
          return (
            dist <
            node.actualRadius +
              otherNode.actualRadius +
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

        // Clamp to bounds BEFORE updating bubble position (use full radius for bounds)
        node.x = Math.max(node.fullRadius, Math.min(width - node.fullRadius, node.x));
        node.y = Math.max(node.fullRadius, Math.min(height - node.fullRadius, node.y));

        // Push away from header exclusion zone (rectangle-based collision)
        const headerExclusionBottom = headerExclusionZone.y + headerExclusionZone.height;
        // Check if bubble center is within header zone, or if bubble overlaps header rectangle
        if (node.y - node.actualRadius < headerExclusionBottom) {
          // Calculate overlap with header rectangle
          const overlap = headerExclusionBottom - (node.y - node.actualRadius);
          if (overlap > 0) {
            // Strong push force to move bubble down
            const pushForce = overlap * 0.5;
            node.vy = (node.vy || 0) + pushForce;
            // Clamp position to keep bubble center + radius fully below header
            node.y = Math.max(headerExclusionBottom + node.actualRadius + 10, node.y);
          }
        }

        // Push away from analytics exclusion zone (precise rectangle-based collision)
        if (exclusionZone) {
          // Check if bubble circle overlaps with rectangle
          // Find closest point on rectangle to bubble center
          const closestX = Math.max(exclusionZone.x, Math.min(node.x, exclusionZone.x + exclusionZone.width));
          const closestY = Math.max(exclusionZone.y, Math.min(node.y, exclusionZone.y + exclusionZone.height));
          
          const dx = node.x - closestX;
          const dy = node.y - closestY;
          const distSq = dx * dx + dy * dy;
          const minDistSq = node.actualRadius * node.actualRadius;
          
          if (distSq < minDistSq) {
            // Bubble overlaps rectangle - push away from closest point
            const dist = Math.sqrt(distSq);
            if (dist > 0) {
              const pushForce = ((node.actualRadius - dist) / dist) * 0.5;
              node.vx = (node.vx || 0) + (dx / dist) * pushForce;
              node.vy = (node.vy || 0) + (dy / dist) * pushForce;
              
              // Clamp to keep outside rectangle
              const minDist = node.actualRadius + 5;
              node.x = closestX + (dx / dist) * minDist;
              node.y = closestY + (dy / dist) * minDist;
            } else {
              // Center is inside rectangle, push toward center of container
              const containerCenterX = width / 2;
              const containerCenterY = height / 2;
              const pushX = (containerCenterX - node.x) * 0.1;
              const pushY = (containerCenterY - node.y) * 0.1;
              node.vx = (node.vx || 0) + pushX;
              node.vy = (node.vy || 0) + pushY;
            }
          }
        }

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

      // Update child node positions based on parent positions and angles
      childNodes.forEach((childNode) => {
        const parent = childNode.parentNode;
        const bubble = bubbleDataRef.current.get(parent.data.suggestion.title);
        if (!bubble) return;

        // Find the child data to get current angle
        const child = bubble.children.find((c) => c.id === childNode.childId);
        if (!child) return;

        // Calculate child position based on parent position and angle
        const childDistance = bubble.radius + 50;
        childNode.x = parent.x + Math.cos(child.angle) * childDistance;
        childNode.y = parent.y + Math.sin(child.angle) * childDistance;
      });

      setRenderTrigger((prev) => prev + 1);
    });

    // Cleanup
    return () => {
      simulation.stop();
      simulationRef.current = null;
    };
  }, [bubbleCount]); // Re-run when number of bubbles changes

  // Parent bubble drag handlers
  const parentDragStarted = useCallback((event: d3Drag.D3DragEvent<SVGCircleElement, unknown, D3Node>) => {
    const node = event.subject;
    if (!node) return;

    // Fix position during drag
    node.fx = node.x;
    node.fy = node.y;
    
    // Track which bubble is being dragged
    draggedBubbleRef.current = { type: "parent", id: node.data.suggestion.title };
    setDraggedBubbleId(node.data.suggestion.title);

    // Restart simulation if needed
    if (simulationRef.current && !event.active) {
      simulationRef.current.alphaTarget(0.3).restart();
    }
  }, []);

  const parentDragging = useCallback((event: d3Drag.D3DragEvent<SVGCircleElement, unknown, D3Node>) => {
    const node = event.subject;
    if (!node || !containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;
    const bubble = node.data;

    // Clamp to bounds (use full radius for bounds)
    let newX = Math.max(node.fullRadius, Math.min(width - node.fullRadius, event.x));
    let newY = Math.max(node.fullRadius, Math.min(height - node.fullRadius, event.y));

    // Clamp to header exclusion zone (use actual radius for collision check)
    const headerHeight = 80;
    const headerExclusionBottom = headerHeight + 50;
    if (newY - node.actualRadius < headerExclusionBottom) {
      newY = Math.max(headerExclusionBottom + node.actualRadius + 10, newY);
    }

    // Clamp to analytics exclusion zone (rectangle-based collision)
    try {
      const exclusionData = container.getAttribute('data-analytics-exclusion');
      if (exclusionData) {
        const parsed = JSON.parse(exclusionData);
        if (parsed.width > 0 && parsed.height > 0) {
          const exclusionPadding = 30;
          const exclusionZone = {
            x: parsed.x - exclusionPadding,
            y: parsed.y - exclusionPadding,
            width: parsed.width + exclusionPadding * 2,
            height: parsed.height + exclusionPadding * 2,
          };

          // Find closest point on rectangle to bubble center
          const closestX = Math.max(exclusionZone.x, Math.min(newX, exclusionZone.x + exclusionZone.width));
          const closestY = Math.max(exclusionZone.y, Math.min(newY, exclusionZone.y + exclusionZone.height));
          
          const dx = newX - closestX;
          const dy = newY - closestY;
          const distSq = dx * dx + dy * dy;
          const minDistSq = node.actualRadius * node.actualRadius;
          
          if (distSq < minDistSq) {
            // Push away from rectangle
            const dist = Math.sqrt(distSq);
            if (dist > 0) {
              const minDist = node.actualRadius + 5;
              newX = closestX + (dx / dist) * minDist;
              newY = closestY + (dy / dist) * minDist;
            } else {
              // Center is inside rectangle, push toward center of container
              const containerCenterX = width / 2;
              const containerCenterY = height / 2;
              newX = containerCenterX + (containerCenterX - newX) * 0.5;
              newY = containerCenterY + (containerCenterY - newY) * 0.5;
            }
          }
        }
      }
    } catch (e) {
      // Ignore parse errors
    }

    // Update position
    node.fx = newX;
    node.fy = newY;
    bubble.position.x = newX;
    bubble.position.y = newY;

    // Recalculate child positions maintaining angles
    const childDistance = bubble.radius + 50;
    bubble.children.forEach((child) => {
      const childX = newX + Math.cos(child.angle) * childDistance;
      const childY = newY + Math.sin(child.angle) * childDistance;
      // Child positions will be updated in render
    });

    setRenderTrigger((prev) => prev + 1);
  }, []);

  const parentDragEnded = useCallback((event: d3Drag.D3DragEvent<SVGCircleElement, unknown, D3Node>) => {
    const node = event.subject;
    if (!node) return;

    // Release physics constraint
    node.fx = null;
    node.fy = null;

    // Let simulation settle
    if (simulationRef.current) {
      simulationRef.current.alphaTarget(0);
    }

    // Clear drag state
    draggedBubbleRef.current = null;
    setDraggedBubbleId(null);
  }, []);

  // Child bubble drag handlers
  const childDragStarted = useCallback((event: d3Drag.D3DragEvent<SVGCircleElement, unknown, { parentTitle: string; childId: string; childX: number; childY: number; idealAngle: number; idealDistance: number }>) => {
    const data = event.subject;
    if (!data || !simulationRef.current) return;

    // Find the parent node
    const nodes = simulationRef.current.nodes();
    const parentNode = nodes.find((n) => n.data.suggestion.title === data.parentTitle);
    if (!parentNode) return;

    // Store initial child position
    const childX = data.childX;
    const childY = data.childY;

    // Track which child is being dragged
    draggedBubbleRef.current = { 
      type: "child", 
      id: data.childId,
      parentTitle: data.parentTitle 
    };
    setDraggedBubbleId(data.childId);

    // Set up spring force to pull parent toward child
    childDragSpringForceRef.current = {
      parentNode,
      childX,
      childY,
      strength: 0.15, // Spring constant
    };

    // Restart simulation if needed
    if (!event.active) {
      simulationRef.current.alphaTarget(0.3).restart();
    }
  }, []);

  const childDragging = useCallback((event: d3Drag.D3DragEvent<SVGCircleElement, unknown, { parentTitle: string; childId: string; childX: number; childY: number; idealAngle: number; idealDistance: number }>) => {
    const data = event.subject;
    if (!data || !childDragSpringForceRef.current || !containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Clamp to bounds (child bubbles are smaller, so use smaller radius)
    const childRadius = 30;
    let newX = Math.max(childRadius, Math.min(width - childRadius, event.x));
    let newY = Math.max(childRadius, Math.min(height - childRadius, event.y));

    // Update child position in spring force
    childDragSpringForceRef.current.childX = newX;
    childDragSpringForceRef.current.childY = newY;

    // Update stored position for rendering
    data.childX = newX;
    data.childY = newY;

    setRenderTrigger((prev) => prev + 1);
  }, []);

  const childDragEnded = useCallback((event: d3Drag.D3DragEvent<SVGCircleElement, unknown, { parentTitle: string; childId: string; childX: number; childY: number; idealAngle: number; idealDistance: number }>) => {
    // Remove spring force
    childDragSpringForceRef.current = null;

    // Let simulation settle
    if (simulationRef.current) {
      simulationRef.current.alphaTarget(0);
    }

    // Clear drag state
    draggedBubbleRef.current = null;
    setDraggedBubbleId(null);
  }, []);

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
        data: child.data,
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

  // Attach drag behaviors to SVG circles
  useEffect(() => {
    if (!svgRef.current || bubbleCount === 0 || !simulationRef.current) return;

    const svg = d3Select.select(svgRef.current);

    // Create parent drag behavior
    const parentDrag = d3Drag.drag<SVGCircleElement, unknown>()
      .subject((event) => {
        // Find the parent node that corresponds to this circle
        // Traverse up the DOM tree to find the circle with data-parent-bubble
        let target = event.sourceEvent.target as Element;
        let parentTitle: string | null = null;
        
        // Traverse up to find the circle element with data-parent-bubble attribute
        while (target && target !== svgRef.current) {
          parentTitle = target.getAttribute("data-parent-bubble");
          if (parentTitle) break;
          target = target.parentElement as Element;
        }
        
        if (!parentTitle) return null;
        
        const nodes = simulationRef.current?.nodes() || [];
        return nodes.find((n) => n.data.suggestion.title === parentTitle) || null;
      })
      .on("start", parentDragStarted as (event: d3Drag.D3DragEvent<SVGCircleElement, unknown, D3Node>) => void)
      .on("drag", parentDragging as (event: d3Drag.D3DragEvent<SVGCircleElement, unknown, D3Node>) => void)
      .on("end", parentDragEnded as (event: d3Drag.D3DragEvent<SVGCircleElement, unknown, D3Node>) => void);

    // Create child drag behavior
    const childDrag = d3Drag.drag<SVGCircleElement, unknown>()
      .subject((event) => {
        // Extract child bubble data from data attributes
        // Traverse up the DOM tree to find the circle with data-child-bubble
        let target = event.sourceEvent.target as Element;
        let childId: string | null = null;
        let parentTitle: string | null = null;
        
        // Traverse up to find the circle element with data-child-bubble attribute
        while (target && target !== svgRef.current) {
          childId = target.getAttribute("data-child-bubble");
          if (childId) {
            parentTitle = target.getAttribute("data-child-parent");
            const childX = parseFloat(target.getAttribute("data-child-x") || "0");
            const childY = parseFloat(target.getAttribute("data-child-y") || "0");
            const idealAngle = parseFloat(target.getAttribute("data-child-angle") || "0");
            const idealDistance = parseFloat(target.getAttribute("data-child-distance") || "0");
            
            if (parentTitle) {
              return {
                parentTitle,
                childId,
                childX,
                childY,
                idealAngle,
                idealDistance,
              };
            }
            break;
          }
          target = target.parentElement as Element;
        }
        
        return null;
      })
      .on("start", childDragStarted as (event: d3Drag.D3DragEvent<SVGCircleElement, unknown, { parentTitle: string; childId: string; childX: number; childY: number; idealAngle: number; idealDistance: number }>) => void)
      .on("drag", childDragging as (event: d3Drag.D3DragEvent<SVGCircleElement, unknown, { parentTitle: string; childId: string; childX: number; childY: number; idealAngle: number; idealDistance: number }>) => void)
      .on("end", childDragEnded as (event: d3Drag.D3DragEvent<SVGCircleElement, unknown, { parentTitle: string; childId: string; childX: number; childY: number; idealAngle: number; idealDistance: number }>) => void);

    // Apply drag behaviors
    svg.selectAll<SVGCircleElement, unknown>("circle[data-parent-bubble]")
      .call(parentDrag);

    svg.selectAll<SVGCircleElement, unknown>("circle[data-child-bubble]")
      .call(childDrag);

    // Cleanup
    return () => {
      svg.selectAll<SVGCircleElement, unknown>("circle[data-parent-bubble]")
        .on(".drag", null);
      svg.selectAll<SVGCircleElement, unknown>("circle[data-child-bubble]")
        .on(".drag", null);
    };
  }, [bubbleCount, parentDragStarted, parentDragging, parentDragEnded, childDragStarted, childDragging, childDragEnded]);

  if (suggestions.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-6">
          <div className="relative">
            <div 
              className="w-20 h-20 border-4 rounded-full animate-spin"
              style={{
                borderColor: "var(--theme-loading-border)",
                borderTopColor: "var(--theme-loading-border-active)",
                borderRightColor: "var(--theme-loading-border-active)",
              }}
            />
            <div 
              className="absolute inset-0 w-20 h-20 rounded-full animate-ping opacity-20"
              style={{
                backgroundColor: "var(--theme-loading-border-active)",
              }}
            />
          </div>
          <div className="text-center space-y-2">
            <div 
              className="text-xl font-semibold"
              style={{ color: "var(--theme-fg-primary)" }}
            >
              Analyzing responses...
            </div>
            <div 
              className="text-sm opacity-70"
              style={{ color: "var(--theme-fg-secondary)" }}
            >
              Building consensus visualization
            </div>
          </div>
        </div>
      </div>
    );
  }

  const bubbleData = Array.from(bubbleDataRef.current.values());

  return (
    <div
      ref={containerRef}
      className="w-full h-full relative overflow-hidden"
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
        ref={svgRef}
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
          const { suggestion, position, children, radius, isMoving, isNew } = bubble;
          const isParentHovered = hoveredParent === suggestion.title;
          const childDistance = radius + 50;

          return (
            <g 
              key={suggestion.title}
              style={{
                opacity: isNew ? 0 : 1,
                animation: isNew ? 'fadeInBubble 0.6s ease-out forwards' : undefined,
              }}
            >
              {/* Animated glow ring when moving - subtle effect */}
              {isMoving && (
                <>
                  <circle
                    cx={position.x}
                    cy={position.y}
                    r={radius + childDistance + 80}
                    fill="none"
                    stroke="var(--theme-bubble-primary-from)"
                    strokeWidth="2"
                    opacity="0.1"
                    className="animate-pulse"
                    style={{ animationDuration: '3s', animationTimingFunction: 'ease-in-out' }}
                  >
                    <animate
                      attributeName="r"
                      values={`${radius + childDistance + 60};${radius + childDistance + 85};${radius + childDistance + 60}`}
                      dur="3s"
                      repeatCount="indefinite"
                    />
                    <animate
                      attributeName="opacity"
                      values="0.15;0.05;0.15"
                      dur="3s"
                      repeatCount="indefinite"
                    />
                  </circle>
                  <circle
                    cx={position.x}
                    cy={position.y}
                    r={radius + 15}
                    fill="none"
                    stroke="var(--theme-glass-white)"
                    strokeWidth="1.5"
                    opacity="0.25"
                    style={{ stroke: "var(--theme-glass-white)" }}
                  >
                    <animate
                      attributeName="r"
                      values={`${radius + 10};${radius + 18};${radius + 10}`}
                      dur="2s"
                      repeatCount="indefinite"
                    />
                    <animate
                      attributeName="opacity"
                      values="0.3;0.15;0.3"
                      dur="2s"
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

              {/* Lines connecting parent to children - stretchy connections */}
              {children.map((child, i) => {
                // Calculate actual child position (may be dragged)
                let childX: number;
                let childY: number;
                const isChildDragged = draggedBubbleRef.current?.type === "child" && 
                  draggedBubbleRef.current.id === child.id;
                
                if (isChildDragged && childDragSpringForceRef.current) {
                  // Use actual dragged position
                  childX = childDragSpringForceRef.current.childX;
                  childY = childDragSpringForceRef.current.childY;
                } else {
                  // Use angle-based position
                  childX = position.x + Math.cos(child.angle) * childDistance;
                  childY = position.y + Math.sin(child.angle) * childDistance;
                }

                // Calculate stretch ratio
                const idealDistance = childDistance;
                const actualDistance = Math.sqrt(
                  Math.pow(childX - position.x, 2) + Math.pow(childY - position.y, 2)
                );
                const stretchRatio = actualDistance / idealDistance;

                // Update line properties based on stretch
                const baseStrokeWidth = isParentHovered ? 3 : 2;
                const strokeWidth = baseStrokeWidth + (stretchRatio > 1 ? (stretchRatio - 1) * 2 : 0);
                const opacity = isParentHovered 
                  ? Math.min(0.7, 0.5 + (stretchRatio > 1 ? (stretchRatio - 1) * 0.2 : 0))
                  : Math.min(0.4, 0.2 + (stretchRatio > 1 ? (stretchRatio - 1) * 0.1 : 0));

                return (
                  <line
                    key={`${child.id}-${i}`}
                    x1={position.x}
                    y1={position.y}
                    x2={childX}
                    y2={childY}
                    stroke="var(--theme-bubble-primary-from)"
                    strokeWidth={strokeWidth}
                    opacity={opacity}
                    className="transition-all duration-300"
                    strokeDasharray={isParentHovered ? "0" : "5,5"}
                  />
                );
              })}

              {/* Main suggestion bubble */}
              <g className="transition-all duration-300">
                {/* Invisible larger hover area - only if not being dragged */}
                {draggedBubbleId !== suggestion.title && (
                  /* biome-ignore lint/a11y/noStaticElementInteractions: SVG circle used for visual graph interaction */
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
                )}

                {/* Outer ring */}
                <circle
                  cx={position.x}
                  cy={position.y}
                  r={radius}
                  fill="var(--theme-glass-white)"
                  fillOpacity="0.3"
                  className="pointer-events-none"
                  filter={isParentHovered ? "url(#glow)" : ""}
                />

                {/* Main bubble */}
                <circle
                  data-parent-bubble={suggestion.title}
                  cx={position.x}
                  cy={position.y}
                  r={radius}
                  fill="url(#gradient-blue)"
                  className={`transition-all duration-300 ${isParentHovered ? "drop-shadow-2xl" : "drop-shadow-lg"} ${draggedBubbleId === suggestion.title ? "cursor-grabbing" : "cursor-pointer"}`}
                  filter={isParentHovered ? "url(#soft-glow)" : ""}
                  style={{
                    transform: isParentHovered ? "scale(1.05)" : "scale(1)",
                    transformOrigin: `${position.x}px ${position.y}px`,
                    opacity: draggedBubbleId === suggestion.title ? 0.9 : 1,
                    pointerEvents: "auto",
                  }}
                  onMouseEnter={() => {
                    if (draggedBubbleId !== suggestion.title) {
                      handleParentHover(suggestion.title, true);
                    }
                  }}
                  onMouseLeave={() => {
                    if (draggedBubbleId !== suggestion.title) {
                      handleParentHover(suggestion.title, false);
                    }
                  }}
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
              {children.map((child, i) => {
                // Calculate actual child position (may be dragged)
                let childX: number;
                let childY: number;
                const isChildDragged = draggedBubbleRef.current?.type === "child" && 
                  draggedBubbleRef.current.id === child.id;
                
                if (isChildDragged && childDragSpringForceRef.current) {
                  // Use actual dragged position
                  childX = childDragSpringForceRef.current.childX;
                  childY = childDragSpringForceRef.current.childY;
                } else {
                  // Use angle-based position
                  childX = position.x + Math.cos(child.angle) * childDistance;
                  childY = position.y + Math.sin(child.angle) * childDistance;
                }

                const gradient = "url(#gradient-opinion)";

                return (
                  <g
                    key={`${child.id}-${i}`}
                    className="transition-all duration-300"
                    style={{
                      opacity: isParentHovered ? 1 : 0.7,
                    }}
                  >
                    {/* Invisible larger hover area - only if not being dragged */}
                    {draggedBubbleId !== child.id && (
                      /* biome-ignore lint/a11y/noStaticElementInteractions: SVG circle used for visual graph interaction */
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
                    )}

                    {/* Outer ring for child */}
                    <circle
                      cx={childX}
                      cy={childY}
                      r={child.size}
                      fill="var(--theme-glass-white)"
                      fillOpacity="0.3"
                      className="pointer-events-none"
                    />

                    {/* Child bubble - draggable */}
                    <circle
                      data-child-bubble={child.id}
                      data-child-parent={suggestion.title}
                      data-child-x={childX}
                      data-child-y={childY}
                      data-child-angle={child.angle}
                      data-child-distance={childDistance}
                      cx={childX}
                      cy={childY}
                      r={child.size}
                      fill={gradient}
                      className={`drop-shadow-lg transition-all ${draggedBubbleId === child.id ? "cursor-grabbing" : "cursor-pointer"}`}
                      filter="url(#soft-glow)"
                      style={{
                        opacity: draggedBubbleId === child.id ? 0.9 : undefined,
                        pointerEvents: draggedBubbleId === child.id ? "all" : "auto",
                      }}
                      onMouseEnter={(e) => {
                        if (draggedBubbleId !== child.id) {
                          handleParentHover(suggestion.title, true);
                          handleChildBubbleHover(child, e);
                        }
                      }}
                      onMouseLeave={() => {
                        if (draggedBubbleId !== child.id) {
                          handleChildBubbleLeave();
                          handleParentHover(suggestion.title, false);
                        }
                      }}
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
                    {child.type === "opinion" && (
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
                            {/* Star for excellent messages - top right */}
                            {child.data.isExcellent && (
                              <div 
                                className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center shadow-lg"
                                style={{ backgroundColor: "var(--theme-accent-yellow)" }}
                              >
                                <Star className="w-2.5 h-2.5 text-white fill-white" />
                              </div>
                            )}
                            {/* Plus/Minus indicator - bottom right */}
                            {child.data.classification === "good" && (
                              <div 
                                className="absolute -bottom-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center shadow-lg text-white font-bold text-xs"
                                style={{ backgroundColor: "var(--theme-accent-green)" }}
                              >
                                +
                              </div>
                            )}
                            {child.data.classification === "bad" && (
                              <div 
                                className="absolute -bottom-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center shadow-lg text-white font-bold text-xs"
                                style={{ backgroundColor: "var(--theme-accent-red)" }}
                              >
                                −
                              </div>
                            )}
                          </div>
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

      {/* Analytics Dashboard */}
      <AnalyticsDashboard 
        suggestions={suggestions} 
        questionText={questionText}
        containerRef={containerRef}
      />

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
            className="backdrop-blur-xl rounded-2xl shadow-2xl border p-6 max-w-sm animate-in fade-in zoom-in-95 duration-300"
            style={{
              backgroundColor: "var(--theme-bg-primary)",
              borderColor: "var(--theme-bg-tertiary)",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1), 0 0 0 1px var(--theme-bg-tertiary)",
            }}
          >
            {/* Subtle gradient overlay */}
            <div 
              className="absolute inset-0 rounded-2xl opacity-50 pointer-events-none"
              style={{
                background: "linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(168, 85, 247, 0.05), transparent)",
              }}
            />
            <div className="relative">
            {hoveredBubble.type === "opinion" && (
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="relative shrink-0">
                    <Image
                      src={hoveredBubble.data.profilePicUrl}
                      alt={hoveredBubble.data.name}
                      width={56}
                      height={56}
                      className="rounded-xl shadow-lg ring-2 ring-indigo-400/30"
                      unoptimized
                    />
                    {/* Star for excellent messages */}
                    {hoveredBubble.data.isExcellent && (
                      <div 
                        className="absolute -top-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center shadow-md border-2 border-white"
                        style={{ backgroundColor: "var(--theme-accent-yellow)" }}
                      >
                        <Star 
                          className="w-3.5 h-3.5 fill-white text-white" 
                        />
                      </div>
                    )}
                    {/* Plus/Minus indicator */}
                    {hoveredBubble.data.classification === "good" && (
                      <div 
                        className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center shadow-md border-2 border-white text-white font-bold text-sm"
                        style={{ backgroundColor: "var(--theme-accent-green)" }}
                      >
                        +
                      </div>
                    )}
                    {hoveredBubble.data.classification === "bad" && (
                      <div 
                        className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center shadow-md border-2 border-white text-white font-bold text-sm"
                        style={{ backgroundColor: "var(--theme-accent-red)" }}
                      >
                        −
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0 pt-1">
                    <div 
                      className="font-bold text-base mb-1"
                      style={{ color: "var(--theme-fg-primary)" }}
                    >
                      {hoveredBubble.data.name}
                      {hoveredBubble.data.isExcellent && (
                        <span className="ml-2">⭐</span>
                      )}
                    </div>
                    <div 
                      className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold capitalize"
                      style={{ 
                        backgroundColor: hoveredBubble.data.classification === "good" 
                          ? "rgba(16, 185, 129, 0.1)" 
                          : hoveredBubble.data.classification === "bad"
                          ? "rgba(239, 68, 68, 0.1)"
                          : "rgba(100, 100, 100, 0.1)",
                        color: hoveredBubble.data.classification === "good"
                          ? "var(--theme-accent-green)"
                          : hoveredBubble.data.classification === "bad"
                          ? "var(--theme-accent-red)"
                          : "var(--theme-fg-tertiary)",
                      }}
                    >
                      {hoveredBubble.data.classification} opinion
                    </div>
                  </div>
                </div>
                <div 
                  className="relative pl-4 border-l-2"
                  style={{
                    borderColor: "var(--theme-bg-tertiary)",
                  }}
                >
                  <p 
                    className="text-sm leading-relaxed italic"
                    style={{ color: "var(--theme-fg-secondary)" }}
                  >
                    "{hoveredBubble.data.message}"
                  </p>
                </div>
              </div>
            )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
