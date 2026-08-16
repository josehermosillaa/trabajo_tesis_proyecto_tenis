export interface CompetitionCategory {
  id: number;
  competition: number;
  category: number;
  max_players: number;
  minimum_players: number;
}

export interface Category {
  id: number;
  name: string;
}