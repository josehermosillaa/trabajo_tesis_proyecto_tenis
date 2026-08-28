export type MatchStatus =
  | 'PROGRAMADO'
  | 'EN_JUEGO'
  | 'FINALIZADO'
  | 'CANCELADO';


export type MatchResolutionType =
  | 'NORMAL'
  | 'WALKOVER'
  | 'RETIREMENT';


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

  resolution_type:
    MatchResolutionType;
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

  resolution_type?:
    MatchResolutionType;

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

  resolution_type?:
    MatchResolutionType;

  winner_player?: number | null;
}


export interface ResolveMatchRequest {

  winner_player: number;
}