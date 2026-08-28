export interface MatchSet {

  id: number;

  match: number;

  set_number: number;

  games_player1: number;

  games_player2: number;

  is_super_tie_break: boolean;

  is_incomplete: boolean;
}


export interface CreateMatchSetRequest {

  match: number;

  set_number: number;

  games_player1: number;

  games_player2: number;

  is_super_tie_break?: boolean;

  is_incomplete?: boolean;
}


export interface UpdateMatchSetRequest {

  match?: number;

  set_number?: number;

  games_player1?: number;

  games_player2?: number;

  is_super_tie_break?: boolean;

  is_incomplete?: boolean;
}