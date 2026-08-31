import { Match } from '../../matches/models/match.model';

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

// =====================================================
// BRACKET
// =====================================================

export interface BracketSet {
  id: number;
  set_number: number;
  games_player1: number;
  games_player2: number;
  is_super_tie_break: boolean;
}

export interface BracketMatch {
  id: number;
  competition_category: number;

  court: number | null;

  player1: number | null;
  player2: number | null;

  winner_player: number | null;

  scheduled_date_time: string | null;

  status:
    | 'PROGRAMADO'
    | 'EN_JUEGO'
    | 'FINALIZADO'
    | 'CANCELADO';

  round: number;
  bracket_position: number;

  next_match: number | null;
  next_match_slot: number | null;

  is_walkover: boolean;

  sets: BracketSet[];
}

export interface BracketParticipant {
  id: number;
  first_name: string;
  last_name: string;
}

export interface BracketResponse {
  competition_category: number;

  competition: number;
  competition_name: string;

  category: number;
  category_name: string;

  participants: BracketParticipant[];

  generated: boolean;

  can_delete: boolean;
  scheduled_matches_count: number;
  delete_block_reason: string | null;

  matches: BracketMatch[];
}

export interface GenerateBracketResponse {
  detail: string;
  competition_category: number;
  matches: BracketMatch[];
}

export interface DeleteBracketResponse {
  detail: string;
  deleted_matches: number;
  deleted_scheduled_matches: number;
}

// =====================================================
// ESCALERILLA
// =====================================================

export interface Standing {
  id: number;
  competition_category: number;
  player: number;
  position: number | null;
  matches_played: number;
  matches_won: number;
  matches_lost: number;
  sets_won: number;
  sets_lost: number;
  sets_difference: number;
  games_won: number;
  games_lost: number;
  games_difference: number;
  points: number;
  walkovers_won: number;
  walkovers_lost: number;
}

export interface LadderParticipant {
  registration: number;
  player: number;
  first_name: string;
  last_name: string;
}

export interface LadderResponse {
  competition_category: CompetitionCategory;
  participants: LadderParticipant[];
  standings: Standing[];
  matches: Match[];
  generated: boolean;
  can_delete: boolean;
  scheduled_matches_count: number;
  delete_block_reason: string | null;
}

export interface GenerateLadderResponse {
  detail: string;
  competition_category: number;
  matches: Match[];
}

export interface DeleteLadderResponse {
  detail: string;
  deleted_matches: number;
  deleted_scheduled_matches: number;
  deleted_standings: number;
}
