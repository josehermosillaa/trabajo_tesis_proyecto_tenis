export interface Organizer {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  is_active: boolean;
  role: 'Organizador';
}

export interface CreateOrganizerRequest {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  password_confirmation: string;
}

export interface UpdateOrganizerRequest {
  username?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
}
