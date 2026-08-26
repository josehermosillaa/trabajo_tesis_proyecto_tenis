export interface Registration {
  id: number;
  competition_category: number;
  player: number;
  registration_date: string;
  status: 'PENDIENTE' | 'CONFIRMADA' | 'CANCELADA';
  seed: number | null;
}

export interface CreateRegistrationRequest {
  competition_category: number;
  player?: number;

  status?:
    | 'PENDIENTE'
    | 'CONFIRMADA'
    | 'CANCELADA';

  seed?: number | null;
}

export interface UpdateRegistrationRequest {
  competition_category?: number;
  player?: number;
  status?: 'PENDIENTE' | 'CONFIRMADA' | 'CANCELADA';
  seed?: number | null;
}

export interface CompetitionCategory {
  id: number;
  competition: number;
  category: number;
  max_players: number;
  minimum_players: number;
}

export interface Competition {
  id: number;
  name: string;
  type: 'ESCALERILLA' | 'ELIMINACION_DIRECTA';
  start_date: string;
  end_date: string;
  status:
    | 'PENDIENTE'
    | 'ABIERTA'
    | 'EN_CURSO'
    | 'FINALIZADA'
    | 'CANCELADA';
  registration_deadline: string;
}