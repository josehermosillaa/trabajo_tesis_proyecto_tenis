import { TestBed } from '@angular/core/testing';
import { CanActivateFn, Router, UrlTree } from '@angular/router';

import { TokenService, UserRole } from '../services/token';
import { managementGuard } from './management-guard';

describe('managementGuard', () => {
  let tokenService: jasmine.SpyObj<TokenService>;
  let router: jasmine.SpyObj<Router>;

  const executeGuard: CanActivateFn = (...parameters) =>
    TestBed.runInInjectionContext(() => managementGuard(...parameters));

  beforeEach(() => {
    tokenService = jasmine.createSpyObj<TokenService>(
      'TokenService',
      ['isAuthenticated', 'isAdministrativeUser']
    );
    router = jasmine.createSpyObj<Router>('Router', ['createUrlTree']);
    router.createUrlTree.and.callFake((commands) => ({ commands }) as unknown as UrlTree);

    TestBed.configureTestingModule({
      providers: [
        { provide: TokenService, useValue: tokenService },
        { provide: Router, useValue: router },
      ],
    });
  });

  for (const role of ['Administrador', 'Organizador'] as UserRole[]) {
    it(`allows ${role}`, () => {
      setRole(role);
      expect(executeGuard({} as never, {} as never)).toBeTrue();
    });
  }

  it('rejects Jugador', () => {
    setRole('Jugador');
    expect(executeGuard({} as never, {} as never)).toBe(
      router.createUrlTree.calls.mostRecent().returnValue
    );
    expect(router.createUrlTree).toHaveBeenCalledWith(['/dashboard']);
  });

  it('redirects unauthenticated users to login', () => {
    tokenService.isAuthenticated.and.returnValue(false);
    expect(executeGuard({} as never, {} as never)).toBe(
      router.createUrlTree.calls.mostRecent().returnValue
    );
    expect(router.createUrlTree).toHaveBeenCalledWith(['/login']);
  });

  function setRole(role: UserRole): void {
    tokenService.isAuthenticated.and.returnValue(true);
    tokenService.isAdministrativeUser.and.returnValue(
      role === 'Administrador' || role === 'Organizador'
    );
  }
});
