export type Message = {
  user: string;
  message: string;
  profilePicUrl?: string;
};

export type OpinionClassification = "sophisticated" | "simple" | "neutral";

export type SuggestionOpinion = {
  name: string;
  profilePicUrl: string;
  message: string;
  classification: OpinionClassification;
};

export type Suggestion = {
  title: string;
  size: number; // normalized 0 - 1
  pros: string[];
  contra: string[];
  peopleOpinions: SuggestionOpinion[];
};

export type SuggestionsResponse = Suggestion[];
