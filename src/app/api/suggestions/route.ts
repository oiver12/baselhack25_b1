import { NextResponse } from "next/server";
import type { Suggestion, SuggestionsResponse } from "@/lib/types";

const baseSuggestions: SuggestionsResponse = [
  {
    title: "AI-powered local assistant",
    size: 0.95,
    pros: [
      "Personalized support for civic services",
      "Leverages existing open data",
      "Could integrate with existing chat platforms",
    ],
    contra: [
      "Requires robust privacy safeguards",
      "Needs multilingual support from day one",
    ],
    peopleOpinions: [
      {
        name: "Amelia",
        profilePicUrl: "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
        message:
          "Could triage citizen requests automatically and route them to the right department.",
        classification: "sophisticated",
      },
      {
        name: "Jonas",
        profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
        message:
          "Chat experience feels familiar to residents, especially if we integrate WhatsApp.",
        classification: "simple",
      },
      {
        name: "Priya",
        profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
        message:
          "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
        classification: "neutral",
      },
    ],
  },
  {
    title: "City-wide volunteer app",
    size: 0.65,
    pros: [
      "Connects NGOs with available volunteers",
      "Gamification keeps engagement high",
      "Useful push notifications for urgent needs",
    ],
    contra: [
      "Needs moderation to avoid spam",
      "Should integrate accessibility best practices",
    ],
    peopleOpinions: [
      {
        name: "Rafael",
        profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
        message: "Could integrate calendars to prevent overbooking.",
        classification: "sophisticated",
      },
      {
        name: "Yara",
        profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
        message: "I love the idea of city-wide push alerts.",
        classification: "simple",
      },
    ],
  },
  {
    title: "Pop-up mobility insights",
    size: 0.4,
    pros: [
      "Low hardware cost with e-ink displays",
      "Real-time adjustments based on traffic",
    ],
    contra: ["Weather-proofing might be expensive"],
    peopleOpinions: [
      {
        name: "Sara",
        profilePicUrl: "https://api.dicebear.com/7.x/adventurer/svg?seed=Sara",
        message:
          "Fits well with the smart-city narrative the city already tells.",
        classification: "sophisticated",
      },
      {
        name: "Ben",
        profilePicUrl: "https://api.dicebear.com/7.x/fun-emoji/svg?seed=Ben",
        message: "Would be fun to demo if we can prototype a working station.",
        classification: "simple",
      },
    ],
  },
  {
    title: "Participatory budgeting map",
    size: 0.25,
    pros: [
      "Highlights funded initiatives on an interactive map",
      "Helps citizens discover nearby projects",
    ],
    contra: ["Needs ongoing data upkeep from the city"],
    peopleOpinions: [
      {
        name: "Elena",
        profilePicUrl: "https://api.dicebear.com/7.x/big-smile/svg?seed=Elena",
        message:
          "Visual storytelling could drive more participation next year.",
        classification: "neutral",
      },
    ],
  },
];

function cloneSuggestion(suggestion: Suggestion): Suggestion {
  return {
    ...suggestion,
    pros: [...suggestion.pros],
    contra: [...suggestion.contra],
    peopleOpinions: suggestion.peopleOpinions.map((opinion) => ({
      ...opinion,
    })),
  };
}

type StageUpdate = {
  threshold: number;
  updates: Array<{
    title: string;
    sizeDelta?: number;
    addPros?: string[];
    addContra?: string[];
    addOpinions?: Suggestion["peopleOpinions"];
  }>;
};

const stagedUpdates: StageUpdate[] = [
  {
    threshold: 5,
    updates: [
      {
        title: "AI-powered local assistant",
        sizeDelta: 0.03,
        addPros: ["Could auto-generate service analytics dashboards"],
        addOpinions: [
          {
            name: "Nora",
            profilePicUrl:
              "https://api.dicebear.com/7.x/notionists/svg?seed=Nora",
            message:
              "Residents with disabilities need alternative channels if AI gets it wrong.",
            classification: "neutral",
          },
        ],
      },
      {
        title: "City-wide volunteer app",
        sizeDelta: 0.02,
        addOpinions: [
          {
            name: "Luis",
            profilePicUrl: "https://api.dicebear.com/7.x/thumbs/svg?seed=Luis",
            message: "Would a tier system for urgent vs. casual help work?",
            classification: "sophisticated",
          },
        ],
      },
    ],
  },
  {
    threshold: 10,
    updates: [
      {
        title: "AI-powered local assistant",
        sizeDelta: 0.02,
        addOpinions: [
          {
            name: "Mira",
            profilePicUrl:
              "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
            message: "Could we fine-tune it on past 311 tickets?",
            classification: "sophisticated",
          },
          {
            name: "Joel",
            profilePicUrl:
              "https://api.dicebear.com/7.x/pixel-art/svg?seed=Joel",
            message: "Needs a big red panic button that routes to a human.",
            classification: "simple",
          },
        ],
      },
      {
        title: "Pop-up mobility insights",
        sizeDelta: 0.03,
        addPros: ["Could share anonymized bike lane counts"],
        addOpinions: [
          {
            name: "Aiko",
            profilePicUrl: "https://api.dicebear.com/7.x/miniavs/svg?seed=Aiko",
            message:
              "Maybe sync with the city events calendar to highlight detours.",
            classification: "neutral",
          },
        ],
      },
    ],
  },
  {
    threshold: 15,
    updates: [
      {
        title: "Participatory budgeting map",
        sizeDelta: 0.05,
        addPros: ["Layer in impact metrics once projects finish"],
        addOpinions: [
          {
            name: "Farah",
            profilePicUrl: "https://api.dicebear.com/7.x/rings/svg?seed=Farah",
            message:
              "Could overlay votes to show how neighborhoods prioritised spending.",
            classification: "sophisticated",
          },
        ],
      },
      {
        title: "City-wide volunteer app",
        sizeDelta: 0.03,
        addContra: [
          "Need to reward long-term volunteers, not just short bursts",
        ],
        addOpinions: [
          {
            name: "Eli",
            profilePicUrl: "https://api.dicebear.com/7.x/croodles/svg?seed=Eli",
            message: "Points could be exchanged for local transit credits.",
            classification: "neutral",
          },
        ],
      },
    ],
  },
];

let requestCount = 0;
const currentSuggestions: SuggestionsResponse =
  baseSuggestions.map(cloneSuggestion);
let lastAppliedStageIndex = -1;

function applyUpdate(
  target: Suggestion,
  update: StageUpdate["updates"][number],
) {
  if (typeof update.sizeDelta === "number") {
    target.size = Math.min(1, Math.max(0, target.size + update.sizeDelta));
  }

  if (update.addPros) {
    update.addPros.forEach((pro) => {
      if (!target.pros.includes(pro)) {
        target.pros.push(pro);
      }
    });
  }

  if (update.addContra) {
    update.addContra.forEach((contra) => {
      if (!target.contra.includes(contra)) {
        target.contra.push(contra);
      }
    });
  }

  if (update.addOpinions) {
    update.addOpinions.forEach((newOpinion) => {
      const alreadyExists = target.peopleOpinions.some(
        (opinion) =>
          opinion.name === newOpinion.name &&
          opinion.message === newOpinion.message,
      );
      if (!alreadyExists) {
        target.peopleOpinions.push({ ...newOpinion });
      }
    });
  }
}

export async function GET() {
  requestCount += 1;

  const activeStageIndex = stagedUpdates.reduce((acc, stage, index) => {
    return requestCount >= stage.threshold ? index : acc;
  }, -1);

  if (activeStageIndex > lastAppliedStageIndex) {
    for (
      let stageIndex = lastAppliedStageIndex + 1;
      stageIndex <= activeStageIndex;
      stageIndex += 1
    ) {
      const stage = stagedUpdates[stageIndex];
      if (!stage) continue;

      stage.updates.forEach((update) => {
        const suggestion = currentSuggestions.find(
          (item) => item.title === update.title,
        );
        if (suggestion) {
          applyUpdate(suggestion, update);
        }
      });
    }

    lastAppliedStageIndex = activeStageIndex;
  }

  const payload = currentSuggestions.map(cloneSuggestion);
  return NextResponse.json(payload);
}
