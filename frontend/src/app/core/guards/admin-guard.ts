import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

import { TokenService } from '../services/token';

export const adminGuard: CanActivateFn = () => {
  const tokenService = inject(TokenService);
  const router = inject(Router);

  if (!tokenService.isAuthenticated()) {
    return router.createUrlTree(['/login']);
  }

  if (tokenService.getCurrentUserRole() !== 'Administrador') {
    return router.createUrlTree(['/dashboard']);
  }

  return true;
};
