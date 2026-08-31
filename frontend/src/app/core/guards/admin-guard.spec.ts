import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { TokenService } from '../services/token';
import { adminGuard } from './admin-guard';

describe('adminGuard', () => {
  let tokenService: jasmine.SpyObj<TokenService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(() => {
    tokenService = jasmine.createSpyObj<TokenService>(
      'TokenService',
      ['isAuthenticated', 'getCurrentUserRole']
    );
    router = jasmine.createSpyObj<Router>('Router', ['createUrlTree']);
    router.createUrlTree.and.callFake((commands) => commands as never);
    TestBed.configureTestingModule({
      providers: [
        { provide: TokenService, useValue: tokenService },
        { provide: Router, useValue: router },
      ],
    });
  });

  it('allows only Administrador', () => {
    tokenService.isAuthenticated.and.returnValue(true);
    tokenService.getCurrentUserRole.and.returnValue('Administrador');
    expect(runGuard()).toBeTrue();
  });

  it('redirects Organizador and Jugador to dashboard', () => {
    tokenService.isAuthenticated.and.returnValue(true);
    for (const role of ['Organizador', 'Jugador'] as const) {
      tokenService.getCurrentUserRole.and.returnValue(role);
      expect(runGuard()).toEqual(['/dashboard'] as never);
    }
  });

  function runGuard() {
    return TestBed.runInInjectionContext(() => adminGuard(null as never, null as never));
  }
});
