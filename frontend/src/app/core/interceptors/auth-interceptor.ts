import { inject } from '@angular/core';
import {
  HttpInterceptorFn,
} from '@angular/common/http';

import { TokenService } from '../services/token';

export const authInterceptor: HttpInterceptorFn = (req, next) => {

  const tokenService = inject(TokenService);

  const accessToken = tokenService.getAccessToken();

  if (!accessToken) {
    return next(req);
  }

  const authenticatedRequest = req.clone({
    setHeaders: {
      Authorization: `Bearer ${accessToken}`
    }
  });

  return next(authenticatedRequest);

};