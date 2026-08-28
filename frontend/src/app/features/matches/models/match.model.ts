export type MatchStatus =
  | 'PROGRAMADO'
  | 'EN_JUEGO'
  | 'FINALIZADO'
  | 'CANCELADO';

export interface Match {
  id: number;

  competition_category: number;

  court: number | null;

  player1: number;

  player2: number | null;

  winner_player: number | null;

  scheduled_date_time:
    string | null;

  status: MatchStatus;

  round: number | null;

  is_walkover: boolean;
}


export interface CreateMatchRequest {

  competition_category: number;

  court?: number | null;

  player1: number;

  player2?: number | null;

  scheduled_date_time?: string | null;

  status?: MatchStatus;

  round?: number | null;

  is_walkover?: boolean;

  winner_player?: number | null;
}


export interface UpdateMatchRequest {

  competition_category?: number;

  court?: number | null;

  player1?: number;

  player2?: number | null;

  scheduled_date_time?: string | null;

  status?: MatchStatus;

  round?: number | null;

  is_walkover?: boolean;

  winner_player?: number | null;
}