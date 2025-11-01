export type Message = {
  user: string;
  message: string;
  profilePicUrl?: string;
};

export type OpinionClassification = "good" | "neutral" | "bad";

export type SuggestionOpinion = {
  name: string;
  profilePicUrl: string;
  message: string; // If followup questions were asked, this is the summary / all the messages
  classification: OpinionClassification;
  isExcellent: boolean;
};

export type Suggestions = Suggestion[];

export type Suggestion = {
  title: string;
  size: number; // normalized 0 - 1
  pros: string[];
  contra: string[];
  peopleOpinions: SuggestionOpinion[];
};

export type SuggestionsResponse = Suggestion[];

// Report page types
export type MessagePoint = {
  id: string;
  x: number;
  y: number;
  message: string;
  user: string;
  profilePicUrl: string;
  cluster?: string;
  classification?: OpinionClassification;
};

export type ConsensusSolution = {
  id: string;
  title: string;
  description: string;
  pros: string[];
  cons: string[];
  approvalPercentage: number;
};

export type ReportData = {
  question: string;
  summary: string;
  opinions: string[];
  messagePoints: MessagePoint[];
  solutions: ConsensusSolution[];
};
