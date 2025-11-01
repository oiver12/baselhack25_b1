import { NextResponse } from "next/server";
import type { SuggestionsResponse } from "@/lib/types";

// Hardcoded stages that build up progressively
const stages: SuggestionsResponse[] = [
  // Stage 0: Just 1 suggestion, size 1.0, 1 opinion, NO pros/cons
  [
    {
      title: "AI-powered local assistant",
      size: 1.0,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Amelia",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 1: Add another opinion, still no pros/cons
  [
    {
      title: "AI-powered local assistant",
      size: 1.0,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Amelia",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 2: Add first pros
  [
    {
      title: "AI-powered local assistant",
      size: 1.0,
      pros: ["Personalized support for civic services"],
      contra: [],
      peopleOpinions: [
        {
          name: "Amelia",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 3: Add more pros
  [
    {
      title: "AI-powered local assistant",
      size: 1.0,
      pros: [
        "Personalized support for civic services",
        "Leverages existing open data",
      ],
      contra: [],
      peopleOpinions: [
        {
          name: "Amelia",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 4: Add another opinion
  [
    {
      title: "AI-powered local assistant",
      size: 1.0,
      pros: [
        "Personalized support for civic services",
        "Leverages existing open data",
      ],
      contra: [],
      peopleOpinions: [
        {
          name: "Amelia",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 5: Add first cons
  [
    {
      title: "AI-powered local assistant",
      size: 1.0,
      pros: [
        "Personalized support for civic services",
        "Leverages existing open data",
      ],
      contra: ["Requires robust privacy safeguards"],
      peopleOpinions: [
        {
          name: "Amelia",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 6: Add more pros and another opinion
  [
    {
      title: "AI-powered local assistant",
      size: 1.0,
      pros: [
        "Personalized support for civic services",
        "Leverages existing open data",
        "Could integrate with existing chat platforms",
      ],
      contra: ["Requires robust privacy safeguards"],
      peopleOpinions: [
        {
          name: "Amelia",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 7: Add more cons
  [
    {
      title: "AI-powered local assistant",
      size: 1.0,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 8: 2nd suggestion appears! Redistribute sizes (70/30)
  [
    {
      title: "AI-powered local assistant",
      size: 0.7,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.3,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 9: 2nd suggestion gets another opinion
  [
    {
      title: "AI-powered local assistant",
      size: 0.7,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.3,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 10: 2nd suggestion gets pros
  [
    {
      title: "AI-powered local assistant",
      size: 0.7,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.3,
      pros: ["Connects NGOs with available volunteers"],
      contra: [],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 11: 2nd suggestion gets more pros and cons
  [
    {
      title: "AI-powered local assistant",
      size: 0.7,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.3,
      pros: [
        "Connects NGOs with available volunteers",
        "Gamification keeps engagement high",
      ],
      contra: ["Needs moderation to avoid spam"],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 12: 3rd suggestion appears! Sizes redistribute (55/25/20)
  [
    {
      title: "AI-powered local assistant",
      size: 0.55,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.25,
      pros: [
        "Connects NGOs with available volunteers",
        "Gamification keeps engagement high",
      ],
      contra: ["Needs moderation to avoid spam"],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Pop-up mobility insights",
      size: 0.2,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Sara",
          profilePicUrl:
            "https://api.dicebear.com/7.x/adventurer/svg?seed=Sara",
          message:
            "Fits well with the smart-city narrative the city already tells.",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 13: 3rd suggestion gets another opinion
  [
    {
      title: "AI-powered local assistant",
      size: 0.55,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.25,
      pros: [
        "Connects NGOs with available volunteers",
        "Gamification keeps engagement high",
      ],
      contra: ["Needs moderation to avoid spam"],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Pop-up mobility insights",
      size: 0.2,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Sara",
          profilePicUrl:
            "https://api.dicebear.com/7.x/adventurer/svg?seed=Sara",
          message:
            "Fits well with the smart-city narrative the city already tells.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Ben",
          profilePicUrl: "https://api.dicebear.com/7.x/fun-emoji/svg?seed=Ben",
          message: "Fun demo!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 14: 3rd suggestion gets pros
  [
    {
      title: "AI-powered local assistant",
      size: 0.55,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.25,
      pros: [
        "Connects NGOs with available volunteers",
        "Gamification keeps engagement high",
      ],
      contra: ["Needs moderation to avoid spam"],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Pop-up mobility insights",
      size: 0.2,
      pros: ["Low hardware cost with e-ink displays"],
      contra: [],
      peopleOpinions: [
        {
          name: "Sara",
          profilePicUrl:
            "https://api.dicebear.com/7.x/adventurer/svg?seed=Sara",
          message:
            "Fits well with the smart-city narrative the city already tells.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Ben",
          profilePicUrl: "https://api.dicebear.com/7.x/fun-emoji/svg?seed=Ben",
          message: "Fun demo!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 15: 3rd suggestion gets cons
  [
    {
      title: "AI-powered local assistant",
      size: 0.55,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.25,
      pros: [
        "Connects NGOs with available volunteers",
        "Gamification keeps engagement high",
      ],
      contra: ["Needs moderation to avoid spam"],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Pop-up mobility insights",
      size: 0.2,
      pros: ["Low hardware cost with e-ink displays"],
      contra: ["Weather-proofing might be expensive"],
      peopleOpinions: [
        {
          name: "Sara",
          profilePicUrl:
            "https://api.dicebear.com/7.x/adventurer/svg?seed=Sara",
          message:
            "Fits well with the smart-city narrative the city already tells.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Ben",
          profilePicUrl: "https://api.dicebear.com/7.x/fun-emoji/svg?seed=Ben",
          message: "Fun demo!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 16: 4th small suggestion appears
  [
    {
      title: "AI-powered local assistant",
      size: 0.52,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.24,
      pros: [
        "Connects NGOs with available volunteers",
        "Gamification keeps engagement high",
      ],
      contra: ["Needs moderation to avoid spam"],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Pop-up mobility insights",
      size: 0.19,
      pros: ["Low hardware cost with e-ink displays"],
      contra: ["Weather-proofing might be expensive"],
      peopleOpinions: [
        {
          name: "Sara",
          profilePicUrl:
            "https://api.dicebear.com/7.x/adventurer/svg?seed=Sara",
          message:
            "Fits well with the smart-city narrative the city already tells.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Ben",
          profilePicUrl: "https://api.dicebear.com/7.x/fun-emoji/svg?seed=Ben",
          message: "Fun demo!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Participatory budgeting map",
      size: 0.05,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Elena",
          profilePicUrl:
            "https://api.dicebear.com/7.x/big-smile/svg?seed=Elena",
          message: "Nice",
          classification: "neutral",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 17: 5th tiny suggestion
  [
    {
      title: "AI-powered local assistant",
      size: 0.5,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.23,
      pros: [
        "Connects NGOs with available volunteers",
        "Gamification keeps engagement high",
      ],
      contra: ["Needs moderation to avoid spam"],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Pop-up mobility insights",
      size: 0.18,
      pros: ["Low hardware cost with e-ink displays"],
      contra: ["Weather-proofing might be expensive"],
      peopleOpinions: [
        {
          name: "Sara",
          profilePicUrl:
            "https://api.dicebear.com/7.x/adventurer/svg?seed=Sara",
          message:
            "Fits well with the smart-city narrative the city already tells.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Ben",
          profilePicUrl: "https://api.dicebear.com/7.x/fun-emoji/svg?seed=Ben",
          message: "Fun demo!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Participatory budgeting map",
      size: 0.05,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Elena",
          profilePicUrl:
            "https://api.dicebear.com/7.x/big-smile/svg?seed=Elena",
          message: "Nice",
          classification: "neutral",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Green space tracker",
      size: 0.04,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Omar",
          profilePicUrl: "https://api.dicebear.com/7.x/shapes/svg?seed=Omar",
          message: "Cool",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 18: 6th tiny suggestion
  [
    {
      title: "AI-powered local assistant",
      size: 0.48,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.22,
      pros: [
        "Connects NGOs with available volunteers",
        "Gamification keeps engagement high",
      ],
      contra: ["Needs moderation to avoid spam"],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Pop-up mobility insights",
      size: 0.17,
      pros: ["Low hardware cost with e-ink displays"],
      contra: ["Weather-proofing might be expensive"],
      peopleOpinions: [
        {
          name: "Sara",
          profilePicUrl:
            "https://api.dicebear.com/7.x/adventurer/svg?seed=Sara",
          message:
            "Fits well with the smart-city narrative the city already tells.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Ben",
          profilePicUrl: "https://api.dicebear.com/7.x/fun-emoji/svg?seed=Ben",
          message: "Fun demo!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Participatory budgeting map",
      size: 0.05,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Elena",
          profilePicUrl:
            "https://api.dicebear.com/7.x/big-smile/svg?seed=Elena",
          message: "Nice",
          classification: "neutral",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Green space tracker",
      size: 0.04,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Omar",
          profilePicUrl: "https://api.dicebear.com/7.x/shapes/svg?seed=Omar",
          message: "Cool",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Noise complaint heatmap",
      size: 0.04,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Zoe",
          profilePicUrl:
            "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Zoe",
          message: "Meh",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],

  // Stage 19: 7th tiny suggestion - final count
  [
    {
      title: "AI-powered local assistant",
      size: 0.47,
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
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Amelia",
          message:
            "Could triage citizen requests automatically and route them to the right department, leveraging existing open data infrastructure.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Jonas",
          profilePicUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Jonas",
          message: "Familiar",
          classification: "bad",
          isExcellent: false,
        },
        {
          name: "Priya",
          profilePicUrl: "https://api.dicebear.com/7.x/personas/svg?seed=Priya",
          message:
            "Needs fallback flows when AI confidence is low — maybe hand off to human agents.",
          classification: "neutral",
          isExcellent: false,
        },
        {
          name: "Mira",
          profilePicUrl:
            "https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=Mira",
          message:
            "Could we fine-tune it on past 311 tickets for better accuracy?",
          classification: "good",
          isExcellent: false,
        },
      ],
    },
    {
      title: "City-wide volunteer app",
      size: 0.21,
      pros: [
        "Connects NGOs with available volunteers",
        "Gamification keeps engagement high",
      ],
      contra: ["Needs moderation to avoid spam"],
      peopleOpinions: [
        {
          name: "Rafael",
          profilePicUrl: "https://api.dicebear.com/7.x/lorelei/svg?seed=Rafael",
          message:
            "Could integrate calendars to prevent overbooking of volunteers.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Yara",
          profilePicUrl: "https://api.dicebear.com/7.x/micah/svg?seed=Yara",
          message: "Love it!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Pop-up mobility insights",
      size: 0.17,
      pros: ["Low hardware cost with e-ink displays"],
      contra: ["Weather-proofing might be expensive"],
      peopleOpinions: [
        {
          name: "Sara",
          profilePicUrl:
            "https://api.dicebear.com/7.x/adventurer/svg?seed=Sara",
          message:
            "Fits well with the smart-city narrative the city already tells.",
          classification: "good",
          isExcellent: false,
        },
        {
          name: "Ben",
          profilePicUrl: "https://api.dicebear.com/7.x/fun-emoji/svg?seed=Ben",
          message: "Fun demo!",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Participatory budgeting map",
      size: 0.06,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Elena",
          profilePicUrl:
            "https://api.dicebear.com/7.x/big-smile/svg?seed=Elena",
          message: "Nice",
          classification: "neutral",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Green space tracker",
      size: 0.04,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Omar",
          profilePicUrl: "https://api.dicebear.com/7.x/shapes/svg?seed=Omar",
          message: "Cool",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Noise complaint heatmap",
      size: 0.03,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Zoe",
          profilePicUrl:
            "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Zoe",
          message: "Meh",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
    {
      title: "Public WiFi expansion",
      size: 0.02,
      pros: [],
      contra: [],
      peopleOpinions: [
        {
          name: "Max",
          profilePicUrl: "https://api.dicebear.com/7.x/identicon/svg?seed=Max",
          message: "Ok",
          classification: "bad",
          isExcellent: false,
        },
      ],
    },
  ],
];

export async function GET(request: Request) {
  // Get stage from query parameter, default to 0
  const { searchParams } = new URL(request.url);
  const stageParam = searchParams.get("stage");
  const stageIndex = stageParam
    ? Math.min(parseInt(stageParam, 10), stages.length - 1)
    : 0;

  const payload = stages[stageIndex];

  return NextResponse.json(payload);
}
