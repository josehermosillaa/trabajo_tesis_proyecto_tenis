import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

import { LoginRequest } from '../models/login-request';
import { TokenResponse } from '../models/token-response';
import { TokenService } from './token';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly tokenService = inject(TokenService);

  private readonly apiUrl = `${environment.apiUrl}/token`;

  login(credentials: LoginRequest): Observable<TokenResponse> {
  return this.http.post<TokenResponse>(
    `${this.apiUrl}/`,
    credentials
  );
  
  }
  logout(): void {
    this.tokenService.clearTokens();
  }
}