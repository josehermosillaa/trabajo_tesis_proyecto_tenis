import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';

import { TokenService } from '../../../../core/services/token';
import { RegistrationService } from '../../services/registration';
import { RegistrationFormComponent } from './registration-form';

describe('RegistrationFormComponent administrative player search', () => {
  let component: RegistrationFormComponent;
  let fixture: ComponentFixture<RegistrationFormComponent>;
  let registrationService: jasmine.SpyObj<RegistrationService>;
  let routeId: string | null;

  const categories = [
    { id: 1, name: 'CUARTA' },
    { id: 2, name: 'TERCERA' },
  ];

  const players = [
    {
      id: 1, user: 11, username: 'ana', email: '', category: 2, rut: '1-9',
      first_name: 'Ana', last_name: 'Pérez', birth_date: null, phone: '',
    },
    {
      id: 2, user: 12, username: 'jose', email: '', category: 1, rut: '2-7',
      first_name: 'José', last_name: 'Álvarez', birth_date: null, phone: '',
    },
  ];

  const competitionCategories = [
    {
      id: 21, competition: 11, category: 1, minimum_players: 4,
      max_players: 16, occupied_slots: 0, available_slots: 16,
      registered_players: [],
    },
    {
      id: 22, competition: 11, category: 2, minimum_players: 4,
      max_players: 16, occupied_slots: 0, available_slots: 16,
      registered_players: [],
    },
  ];

  beforeEach(async () => {
    routeId = null;
    registrationService = jasmine.createSpyObj<RegistrationService>(
      'RegistrationService',
      [
        'getCompetitions', 'getCompetitionCategories', 'getCategories',
        'getPlayers', 'getRegistrations', 'getRegistration',
        'createRegistration', 'updateRegistration',
      ]
    );
    registrationService.getCompetitions.and.returnValue(of([{
      id: 11,
      name: 'Torneo',
      type: 'ELIMINACION_DIRECTA',
      start_date: '2026-09-01',
      end_date: '2026-09-15',
      status: 'PENDIENTE',
      registration_deadline: '2026-08-25',
    }]));
    registrationService.getCompetitionCategories.and.returnValue(
      of(competitionCategories)
    );
    registrationService.getCategories.and.returnValue(of(categories));
    registrationService.getPlayers.and.returnValue(of(players));
    registrationService.getRegistrations.and.returnValue(of([]));
    registrationService.getRegistration.and.returnValue(of({
      id: 9,
      competition_category: 22,
      player: 2,
      registration_date: '2026-08-20T10:00:00Z',
      status: 'PENDIENTE',
      seed: null,
    }));

    const tokenService = jasmine.createSpyObj<TokenService>(
      'TokenService',
      ['isAdministrativeUser']
    );
    tokenService.isAdministrativeUser.and.returnValue(true);

    await TestBed.configureTestingModule({
      imports: [RegistrationFormComponent],
      providers: [
        { provide: RegistrationService, useValue: registrationService },
        { provide: TokenService, useValue: tokenService },
        { provide: Router, useValue: jasmine.createSpyObj('Router', ['navigate']) },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) => key === 'id' ? routeId : null,
              },
              queryParamMap: {
                get: (key: string) => ({
                  competition: '11',
                  competitionCategory: '22',
                }[key] ?? null),
              },
            },
          },
        },
      ],
    }).compileComponents();
  });

  it('shows players from every category and prioritizes matching players', () => {
    createComponent();

    expect(component.filteredPlayers.map((player) => player.id)).toEqual([1, 2]);
  });

  it('starts a new registration as confirmed', () => {
    createComponent();

    expect(component.registrationForm.controls.status.value).toBe('CONFIRMADA');
  });

  it('keeps pending status when editing a pending registration', () => {
    createComponent('9');

    expect(component.registrationForm.controls.status.value).toBe('PENDIENTE');
  });

  it('keeps confirmed status when editing a confirmed registration', () => {
    registrationService.getRegistration.and.returnValue(of({
      id: 9,
      competition_category: 22,
      player: 2,
      registration_date: '2026-08-20T10:00:00Z',
      status: 'CONFIRMADA',
      seed: null,
    }));

    createComponent('9');

    expect(component.registrationForm.controls.status.value).toBe('CONFIRMADA');
  });

  it('keeps cancelled status when editing a cancelled registration', () => {
    registrationService.getRegistration.and.returnValue(of({
      id: 9,
      competition_category: 22,
      player: 2,
      registration_date: '2026-08-20T10:00:00Z',
      status: 'CANCELADA',
      seed: null,
    }));

    createComponent('9');

    expect(component.registrationForm.controls.status.value).toBe('CANCELADA');
  });

  it('submits confirmed status by default for a new registration', () => {
    registrationService.createRegistration.and.returnValue(of({
      id: 30,
      competition_category: 22,
      player: 1,
      registration_date: '2026-08-20T10:00:00Z',
      status: 'CONFIRMADA',
      seed: null,
    }));
    createComponent();
    component.selectPlayer(players[0]);

    component.onSubmit();

    expect(registrationService.createRegistration).toHaveBeenCalledWith({
      competition_category: 22,
      player: 1,
      status: 'CONFIRMADA',
      seed: null,
    });
  });

  it('searches by name or surname ignoring accents and case', () => {
    createComponent();
    component.playerSearchControl.setValue('JOSE ALVAREZ');

    component.updatePlayerSearchResults();

    expect(component.playerSearchResults.map((player) => player.id)).toEqual([2]);
  });

  it('selects a player and displays the current category', () => {
    createComponent();

    component.selectPlayer(players[1]);
    fixture.detectChanges();

    expect(component.registrationForm.controls.player.value).toBe(2);
    expect(fixture.nativeElement.textContent).toContain('Categoría actual:');
    expect(fixture.nativeElement.textContent).toContain('CUARTA');
  });

  it('does not warn for a matching category', () => {
    createComponent();
    component.selectPlayer(players[0]);
    expect(component.isExceptionalCategorySelection()).toBeFalse();
  });

  it('shows a non-blocking warning for a different category', () => {
    createComponent();
    component.selectPlayer(players[1]);
    fixture.detectChanges();

    expect(component.isExceptionalCategorySelection()).toBeTrue();
    expect(component.registrationForm.valid).toBeTrue();
    expect(fixture.nativeElement.textContent).toContain(
      'será inscrito excepcionalmente'
    );
  });

  it('allows submit and preserves the registration payload for an exception', () => {
    createComponent();
    registrationService.createRegistration.and.returnValue(of({
      id: 30,
      competition_category: 22,
      player: 2,
      registration_date: '2026-08-20T10:00:00Z',
      status: 'CONFIRMADA',
      seed: 3,
    }));
    component.selectPlayer(players[1]);
    component.registrationForm.patchValue({
      status: 'CONFIRMADA',
      seed: 3,
    });

    component.onSubmit();

    expect(registrationService.createRegistration).toHaveBeenCalledWith({
      competition_category: 22,
      player: 2,
      status: 'CONFIRMADA',
      seed: 3,
    });
  });

  it('shows but blocks a player with an active registration in the competition', () => {
    registrationService.getRegistrations.and.returnValue(of([{
      id: 31,
      competition_category: 21,
      player: 2,
      registration_date: '2026-08-20T10:00:00Z',
      status: 'CONFIRMADA',
      seed: null,
    }]));
    createComponent();

    expect(component.filteredPlayers.some((player) => player.id === 2)).toBeTrue();
    expect(component.isPlayerRegisteredInCurrentCompetition(2)).toBeTrue();
    component.selectPlayer(players[1]);
    expect(component.registrationForm.controls.player.value).toBe(0);
  });

  it('does not block a player whose registration is cancelled', () => {
    registrationService.getRegistrations.and.returnValue(of([{
      id: 31,
      competition_category: 21,
      player: 2,
      registration_date: '2026-08-20T10:00:00Z',
      status: 'CANCELADA',
      seed: null,
    }]));
    createComponent();

    expect(component.isPlayerRegisteredInCurrentCompetition(2)).toBeFalse();
    component.selectPlayer(players[1]);
    expect(component.registrationForm.controls.player.value).toBe(2);
  });

  it('prefills an exceptional registration in edit mode', () => {
    createComponent('9');

    expect(component.registrationForm.controls.player.value).toBe(2);
    expect(component.playerSearchControl.value).toBe('José Álvarez');
    expect(component.isExceptionalCategorySelection()).toBeTrue();
  });

  function createComponent(id: string | null = null): void {
    routeId = id;
    fixture = TestBed.createComponent(RegistrationFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }
});
