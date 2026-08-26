import { Injectable } from '@angular/core';
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

    const payload =
      JSON.parse(
        atob(
          token.split('.')[1]
            .replace(/-/g, '+')
            .replace(/_/g, '/')
        )
      );

    return payload.user_id ?? null;

  } catch (error) {

    console.error(
      'No fue posible leer el JWT:',
      error
    );

    return null;
  }
}
}