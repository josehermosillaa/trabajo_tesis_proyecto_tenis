import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { AuthService } from './core/services/auth';
import { TokenService, UserRole } from './core/services/token';
import { App } from './app';

describe('App navigation by role', () => {
  let fixture: ComponentFixture<App>;
  let tokenService: jasmine.SpyObj<TokenService>;

  beforeEach(async () => {
    tokenService = jasmine.createSpyObj<TokenService>(
      'TokenService', ['isAuthenticated', 'isAdministrativeUser', 'isAdminUser']
    );
    tokenService.isAuthenticated.and.returnValue(true);
    const authService = jasmine.createSpyObj<AuthService>('AuthService', ['logout']);
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        { provide: TokenService, useValue: tokenService },
        provideRouter([]),
        { provide: AuthService, useValue: authService },
      ],
    }).compileComponents();
  });

  it('shows global administration links to Administrador', () => {
    createForRole('Administrador');
    expect(navText()).toContain('Inscripciones');
    expect(navText()).toContain('Partidos');
    expect(navText()).toContain('Organizadores');
  });

  it('shows only operational links to Organizador', () => {
    createForRole('Organizador');
    expect(navText()).toContain('Dashboard');
    expect(navText()).toContain('Competencias');
    expect(navText()).toContain('Jugadores');
    expect(navText()).not.toContain('Inscripciones');
    expect(navText()).not.toContain('Partidos');
    expect(navText()).not.toContain('Organizadores');
  });

  function createForRole(role: UserRole): void {
    tokenService.isAdministrativeUser.and.returnValue(
      role === 'Administrador' || role === 'Organizador'
    );
    tokenService.isAdminUser.and.returnValue(role === 'Administrador');
    fixture = TestBed.createComponent(App);
    fixture.detectChanges();
  }

  function navText(): string {
    return fixture.nativeElement.querySelector('nav')?.textContent ?? '';
  }
});
