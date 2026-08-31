import { Injectable } from '@angular/core';

export type UserRole =
  | 'Administrador'
  | 'Organizador'
  | 'Jugador';

//gestion de tokens
@Injectable({
  providedIn: 'root'
})
export class TokenService {

  private readonly ACCESS_TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';

saveTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
}
saveAccessToken(accessToken: string): void {
  localStorage.setItem(
    this.ACCESS_TOKEN_KEY,
    accessToken
  );
}

getAccessToken(): string | null {
  return localStorage.getItem(this.ACCESS_TOKEN_KEY);
}

getRefreshToken(): string | null {
  return localStorage.getItem(this.REFRESH_TOKEN_KEY);
}

clearTokens(): void {
  localStorage.removeItem(this.ACCESS_TOKEN_KEY);
  localStorage.removeItem(this.REFRESH_TOKEN_KEY);
}

isAuthenticated(): boolean {
  return this.getAccessToken() !== null;
}

getCurrentUserId(): number | null {

  const token =
    this.getAccessToken();

  if (!token) {
    return null;
  }

  try {

    const payloadPart =
      token.split('.')[1];

    const normalizedPayload =
      payloadPart
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const payload =
      JSON.parse(
        atob(normalizedPayload)
      );

    if (
      payload.user_id === undefined ||
      payload.user_id === null
    ) {
      return null;
    }

    return Number(
      payload.user_id
    );

  } catch (error) {

    console.error(
      'No fue posible leer el JWT:',
      error
    );

    return null;
  }
}

getCurrentUserRole(): UserRole | null {

  const token =
    this.getAccessToken();

  if (!token) {
    return null;
  }

  try {

    const payloadPart =
      token.split('.')[1];

    if (!payloadPart) {
      return null;
    }

    const normalizedPayload =
      payloadPart
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const payload =
      JSON.parse(
        atob(normalizedPayload)
      );

    const role = payload.role;

    if (
      role === 'Administrador'
      || role === 'Organizador'
      || role === 'Jugador'
    ) {
      return role;
    }

    return null;

  } catch (error) {

    console.error(
      'No fue posible leer el rol del JWT:',
      error
    );

    return null;
  }
}

isAdministrativeUser(): boolean {
  const role = this.getCurrentUserRole();

  return (
    role === 'Administrador'
    || role === 'Organizador'
  );
}

isAdminUser(): boolean {
  return this.getCurrentUserRole() === 'Administrador';
}
}
