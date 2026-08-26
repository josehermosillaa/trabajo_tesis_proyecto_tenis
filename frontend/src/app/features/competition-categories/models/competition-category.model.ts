export interface RegisteredPlayer {
  id: number;
  first_name: string;
  last_name: string;
  status:
    | 'PENDIENTE'
    | 'CONFIRMADA'
    | 'CANCELADA';
}

export interface CompetitionCategory {
  id: number;
  competition: number;
  category: number;
  max_players: number;
  minimum_players: number;

  occupied_slots: number;
  available_slots: number;
  registered_players: RegisteredPlayer[];
}

export interface CreateCompetitionCategoryRequest {
  competition: number;
  category: number;
  max_players: number;
  minimum_players: number;
}

export interface UpdateCompetitionCategoryRequest {
  competition?: number;
  category?: number;
  max_players?: number;
  minimum_players?: number;
}