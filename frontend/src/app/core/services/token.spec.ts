import { TestBed } from '@angular/core/testing';

import { TokenService } from './token';

describe('Token', () => {
  let service: TokenService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TokenService);
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should read the current user role', () => {
    service.saveAccessToken(
      createToken({
        role: 'Organizador',
      })
    );

    expect(
      service.getCurrentUserRole()
    ).toBe('Organizador');
  });

  it('should return null when token has no role', () => {
    service.saveAccessToken(
      createToken({
        user_id: 1,
      })
    );

    expect(
      service.getCurrentUserRole()
    ).toBeNull();
  });

  it('should return null when token is invalid', () => {
    service.saveAccessToken(
      'invalid-token'
    );

    expect(
      service.getCurrentUserRole()
    ).toBeNull();
  });

  it('should identify administrative roles', () => {
    service.saveAccessToken(
      createToken({ role: 'Administrador' })
    );

    expect(
      service.isAdministrativeUser()
    ).toBeTrue();
  });

  it('should not identify player as administrative', () => {
    service.saveAccessToken(
      createToken({ role: 'Jugador' })
    );

    expect(
      service.isAdministrativeUser()
    ).toBeFalse();
  });

  function createToken(
    payload: Record<string, unknown>
  ): string {
    const encodedPayload = btoa(
      JSON.stringify(payload)
    )
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');

    return `header.${encodedPayload}.signature`;
  }
});
