export interface Player {
  id: number;
  user: number;
  username: string;
  email: string;
  category: number;
  rut: string;
  first_name: string;
  last_name: string;
  birth_date: string | null;
  phone: string;
}

export interface CreatePlayerRequest {
  username: string;
  email: string;
  password: string;
  category: number;
  rut: string;
  first_name: string;
  last_name: string;
  birth_date: string | null;
  phone: string;
}

export interface UpdatePlayerRequest {
  username?: string;
  email?: string;
  category?: number;
  rut?: string;
  first_name?: string;
  last_name?: string;
  birth_date?: string | null;
  phone?: string;
}