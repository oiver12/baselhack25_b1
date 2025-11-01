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
