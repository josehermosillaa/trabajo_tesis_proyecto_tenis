import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { TokenService } from '../services/token';

export const managementGuard: CanActivateFn = () => {
  const tokenService = inject(TokenService);
  const router = inject(Router);

  if (!tokenService.isAuthenticated()) {
    return router.createUrlTree(['/login']);
  }

  return tokenService.isAdministrativeUser()
    ? true
    : router.createUrlTree(['/dashboard']);
};
