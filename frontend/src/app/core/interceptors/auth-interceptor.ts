import { inject } from '@angular/core';

import {
  HttpClient,
  HttpErrorResponse,
  HttpInterceptorFn,
} from '@angular/common/http';

import { Router } from '@angular/router';

import {
  catchError,
  switchMap,
  throwError,
} from 'rxjs';

import { TokenService } from '../services/token';

import { environment } from '../../../environments/environment';


interface RefreshTokenResponse {
  access: string;
}


export const authInterceptor: HttpInterceptorFn = (
  req,
  next
) => {
  const tokenService = inject(TokenService);
  const http = inject(HttpClient);
  const router = inject(Router);

  /*
   * No interceptamos login ni refresh.
   *
   * Esto evita intentar renovar el token
   * mientras estamos precisamente llamando
   * al endpoint de renovación.
   */
  const isTokenRequest =
    req.url.includes('/token/') ||
    req.url.includes('/token/refresh/');

  if (isTokenRequest) {
    return next(req);
  }

  const accessToken =
    tokenService.getAccessToken();

  let requestToSend = req;

  /*
   * Si existe access token,
   * lo agregamos a la petición.
   */
  if (accessToken) {
    requestToSend = req.clone({
      setHeaders: {
        Authorization:
          `Bearer ${accessToken}`,
      },
    });
  }

  return next(requestToSend).pipe(

    catchError(
      (error: HttpErrorResponse) => {

        /*
         * Si no es 401, no tiene relación
         * con expiración de sesión.
         */
        if (error.status !== 401) {
          return throwError(() => error);
        }

        const refreshToken =
          tokenService.getRefreshToken();

        /*
         * No existe refresh token.
         * La sesión ya no puede recuperarse.
         */
        if (!refreshToken) {
          expireSession();

          return throwError(() => error);
        }

        /*
         * Intentamos obtener un nuevo access token.
         */
        return http
          .post<RefreshTokenResponse>(
            `${environment.apiUrl}/token/refresh/`,
            {
              refresh: refreshToken,
            }
          )
          .pipe(

            switchMap((response) => {

              /*
               * Guardamos únicamente el nuevo
               * access token.
               *
               * El refresh original sigue siendo
               * válido porque ROTATE_REFRESH_TOKENS
               * está en False.
               */
              tokenService.saveAccessToken(
                response.access
              );

              /*
               * Repetimos la petición original
               * con el access token nuevo.
               */
              const retryRequest =
                req.clone({
                  setHeaders: {
                    Authorization:
                      `Bearer ${response.access}`,
                  },
                });

              return next(retryRequest);
            }),

            catchError((refreshError) => {

              /*
               * Si también falla el refresh,
               * la sesión terminó definitivamente.
               */
              expireSession();

              return throwError(
                () => refreshError
              );
            })
          );
      }
    )
  );


  function expireSession(): void {
    tokenService.clearTokens();

    router.navigate(
      ['/login'],
      {
        state: {
          sessionExpired: true,
        },
      }
    );
  }
};