import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';

import { TokenService, UserRole } from '../../../../core/services/token';
import { CompetitionService } from '../../../competitions/services/competition';
import { PlayerService } from '../../../players/services/player';
import { RegistrationService } from '../../../registrations/services/registration';
import { CompetitionCategoryService } from '../../services/competition-category';
import { CompetitionCategoryListComponent } from './competition-category-list';

describe('CompetitionCategoryListComponent sport navigation', () => {
  let fixture: ComponentFixture<CompetitionCategoryListComponent>;
  let categoryService: jasmine.SpyObj<CompetitionCategoryService>;
  let competitionService: jasmine.SpyObj<CompetitionService>;
  let playerService: jasmine.SpyObj<PlayerService>;
  let registrationService: jasmine.SpyObj<RegistrationService>;
  let tokenService: jasmine.SpyObj<TokenService>;
  let router: jasmine.SpyObj<Router>;

  const competitionCategory = {
    id: 12, competition: 8, category: 1, max_players: 8, minimum_players: 2,
    occupied_slots: 8, available_slots: 0, registered_players: [],
  };
  const currentPlayer = {
    id: 5, user: 50, username: 'player', email: 'player@test.cl', category: 99,
    rut: '11111111-1', first_name: 'Jugador', last_name: 'Excepcional',
    birth_date: null, phone: '',
  };

  beforeEach(async () => {
    categoryService = jasmine.createSpyObj('CompetitionCategoryService', [
      'getCompetitionCategories', 'getCategories',
    ]);
    competitionService = jasmine.createSpyObj('CompetitionService', ['getCompetition']);
    playerService = jasmine.createSpyObj('PlayerService', ['getPlayers']);
    registrationService = jasmine.createSpyObj('RegistrationService', [
      'getRegistrations', 'createRegistration',
    ]);
    tokenService = jasmine.createSpyObj('TokenService', [
      'getCurrentUserId', 'getCurrentUserRole', 'isAdministrativeUser',
    ]);
    router = jasmine.createSpyObj('Router', ['navigate']);

    categoryService.getCompetitionCategories.and.returnValue(of([competitionCategory]));
    categoryService.getCategories.and.returnValue(of([{ id: 1, name: 'CUARTA' }]));
    playerService.getPlayers.and.returnValue(of([currentPlayer]));
    registrationService.getRegistrations.and.returnValue(of([]));
    tokenService.getCurrentUserId.and.returnValue(50);

    await TestBed.configureTestingModule({
      imports: [CompetitionCategoryListComponent],
      providers: [
        { provide: CompetitionCategoryService, useValue: categoryService },
        { provide: CompetitionService, useValue: competitionService },
        { provide: PlayerService, useValue: playerService },
        { provide: RegistrationService, useValue: registrationService },
        { provide: TokenService, useValue: tokenService },
        { provide: Router, useValue: router },
        { provide: ActivatedRoute, useValue: {
          snapshot: { paramMap: { get: () => '8' } },
        } },
      ],
    }).compileComponents();
  });

  it('shows Gestionar escalerilla for ADMIN and navigates with both ids', () => {
    createView('ESCALERILLA', 'Administrador');
    expect(buttonTexts()).toContain('Gestionar escalerilla');
    clickButton('Gestionar escalerilla');
    expect(router.navigate).toHaveBeenCalledWith([
      '/competitions', 8, 'categories', 12,
    ]);
  });

  it('shows Gestionar escalerilla for ORGANIZADOR', () => {
    createView('ESCALERILLA', 'Organizador');
    expect(buttonTexts()).toContain('Gestionar escalerilla');
  });

  it('shows Ver escalerilla to a confirmed exceptional player', () => {
    createView('ESCALERILLA', 'Jugador', 'CONFIRMADA');
    expect(buttonTexts()).toContain('Ver escalerilla');
  });

  it('does not grant sport access to a pending player', () => {
    createView('ESCALERILLA', 'Jugador', 'PENDIENTE');
    expect(buttonTexts()).not.toContain('Ver escalerilla');
  });

  it('does not grant sport access to a cancelled player', () => {
    createView('ESCALERILLA', 'Jugador', 'CANCELADA');
    expect(buttonTexts()).not.toContain('Ver escalerilla');
  });

  it('does not use a confirmed registration from another category', () => {
    createView('ESCALERILLA', 'Jugador', 'CONFIRMADA', 99);
    expect(buttonTexts()).not.toContain('Ver escalerilla');
  });

  it('shows Gestionar cuadro for direct elimination administrators', () => {
    createView('ELIMINACION_DIRECTA', 'Administrador');
    expect(buttonTexts()).toContain('Gestionar cuadro');
  });

  it('shows Ver cuadro to a confirmed direct-elimination player', () => {
    createView('ELIMINACION_DIRECTA', 'Jugador', 'CONFIRMADA');
    expect(buttonTexts()).toContain('Ver cuadro');
  });

  function createView(
    type: 'ESCALERILLA' | 'ELIMINACION_DIRECTA',
    role: UserRole,
    registrationStatus?: 'PENDIENTE' | 'CONFIRMADA' | 'CANCELADA',
    registrationCategory = 12
  ): void {
    tokenService.getCurrentUserRole.and.returnValue(role);
    tokenService.isAdministrativeUser.and.returnValue(
      role === 'Administrador' || role === 'Organizador'
    );
    competitionService.getCompetition.and.returnValue(of({
      id: 8, name: 'Torneo', type, start_date: '2026-09-01',
      end_date: '2026-09-15', status: 'EN_CURSO', registration_deadline: '2026-08-28',
    }));
    registrationService.getRegistrations.and.returnValue(of(
      registrationStatus ? [{
        id: 20, competition_category: registrationCategory, player: 5,
        registration_date: '2026-08-01T12:00:00Z',
        status: registrationStatus, seed: null,
      }] : []
    ));

    fixture = TestBed.createComponent(CompetitionCategoryListComponent);
    fixture.detectChanges();
  }

  function buttonTexts(): string[] {
    return Array.from(fixture.nativeElement.querySelectorAll('button'))
      .map((button: unknown) => (button as HTMLButtonElement).textContent?.trim() ?? '');
  }

  function clickButton(text: string): void {
    const button = Array.from(fixture.nativeElement.querySelectorAll('button'))
      .find((item: unknown) =>
        (item as HTMLButtonElement).textContent?.trim() === text
      ) as HTMLButtonElement;
    button.click();
  }
});
