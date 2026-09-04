import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';

import { TokenService } from '../../../../core/services/token';
import { environment } from '../../../../../environments/environment';
import { HomeComponent } from './home';

describe('Home', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;
  let httpTesting: HttpTestingController;
  let tokenService: TokenService;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomeComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();

    httpTesting = TestBed.inject(HttpTestingController);
    tokenService = TestBed.inject(TokenService);
    router = TestBed.inject(Router);
    localStorage.clear();
  });

  afterEach(() => {
    httpTesting.verify();
    localStorage.clear();
  });

  it('should create without loading player data for a non-player user', () => {
    createComponent();
    expect(component).toBeTruthy();
  });

  it('should separate and order administrative competitions', () => {
    tokenService.saveAccessToken(createToken({ user_id: 1, role: 'Organizador' }));
    createComponent();

    httpTesting.expectOne(`${environment.apiUrl}/competitions/`).flush([
      competitionWithStatus(3, 'En curso', 'EN_CURSO', '2026-10-01'),
      competitionWithStatus(2, 'Abierta', 'ABIERTA', '2026-09-10'),
      competitionWithStatus(1, 'Pendiente', 'PENDIENTE', '2026-09-01'),
      competitionWithStatus(4, 'Finalizada', 'FINALIZADA', '2026-08-01'),
    ]);

    expect(component.upcomingCompetitions.map((item) => item.id)).toEqual([1, 2]);
    expect(component.ongoingCompetitions.map((item) => item.id)).toEqual([3]);
  });

  it('keeps global administration shortcuts only for Administrador', () => {
    tokenService.saveAccessToken(createToken({ user_id: 1, role: 'Administrador' }));
    createComponent();
    httpTesting.expectOne(`${environment.apiUrl}/competitions/`).flush([]);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Gestionar inscripciones');
    expect(fixture.nativeElement.textContent).toContain('Ver partidos');

    fixture.destroy();
    tokenService.saveAccessToken(createToken({ user_id: 2, role: 'Organizador' }));
    createComponent();
    httpTesting.expectOne(`${environment.apiUrl}/competitions/`).flush([]);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).not.toContain('Gestionar inscripciones');
    expect(fixture.nativeElement.textContent).not.toContain('Ver partidos');
    expect(fixture.nativeElement.textContent).toContain('Ver competencias');
    expect(fixture.nativeElement.textContent).toContain('Gestionar jugadores');
  });

  it('keeps every administrative shortcut destination unchanged', () => {
    tokenService.saveAccessToken(createToken({ user_id: 1, role: 'Administrador' }));
    spyOn(router, 'navigate');
    createComponent();
    httpTesting.expectOne(`${environment.apiUrl}/competitions/`).flush([]);
    fixture.detectChanges();

    const shortcuts: Array<[string, string]> = [
      ['quick-action-new-competition', '/competitions/new'],
      ['quick-action-competitions', '/competitions'],
      ['quick-action-players', '/players'],
      ['quick-action-registrations', '/registrations'],
      ['quick-action-matches', '/matches'],
    ];

    for (const [testId, route] of shortcuts) {
      (router.navigate as jasmine.Spy).calls.reset();
      (fixture.nativeElement.querySelector(`[data-testid="${testId}"]`) as HTMLButtonElement).click();
      expect(router.navigate).toHaveBeenCalledOnceWith([route]);
    }
  });

  it('opens categories from administrative competition rows', () => {
    tokenService.saveAccessToken(createToken({ user_id: 1, role: 'Organizador' }));
    spyOn(router, 'navigate');
    createComponent();
    httpTesting.expectOne(`${environment.apiUrl}/competitions/`).flush([
      competitionWithStatus(7, 'Copa institucional', 'ABIERTA', '2026-09-10'),
    ]);
    fixture.detectChanges();

    const row = fixture.nativeElement.querySelector(
      '[data-testid="admin-competition-row"]'
    ) as HTMLButtonElement;
    row.click();

    expect(router.navigate).toHaveBeenCalledOnceWith([
      '/competitions', 7, 'categories',
    ]);
  });

  it('should load and relate the player dashboard data', () => {
    tokenService.saveAccessToken(createToken({ user_id: 10, role: 'Jugador' }));
    createComponent();

    const futureDateTime = new Date(Date.now() + 86_400_000).toISOString();
    const futureDate = futureDateTime.slice(0, 10);
    const pastDateTime = new Date(Date.now() - 86_400_000).toISOString();

    httpTesting.expectOne(`${environment.apiUrl}/players/`).flush([
      player(1, 10, 'Ana', 'Pérez'),
      player(2, 11, 'Beatriz', 'Soto'),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/competitions/`).flush([
      competition(1, 'Torneo inscrito', futureDate),
      competition(2, 'Torneo disponible', futureDate),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/registrations/`).flush([
      {
        id: 1,
        competition_category: 101,
        player: 1,
        registration_date: futureDate,
        status: 'CONFIRMADA',
        seed: null,
      },
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/matches/`).flush([
      match(1, 'PROGRAMADO', futureDateTime, null, []),
      match(2, 'FINALIZADO', pastDateTime, 1, [
        set(1, 4, 6),
        set(2, 3, 6),
      ], true),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/competition-categories/`).flush([
      competitionCategory(101, 1),
      competitionCategory(102, 2),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/categories/`).flush([
      { id: 5, name: 'PRIMERA' },
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/courts/`).flush([
      { id: 1, name: 'Cancha Central', status: 'AVAILABLE' },
    ]);

    expect(component.nextMatch?.rival).toBe('Beatriz Soto');
    expect(component.nextMatch?.court).toBe('Cancha Central');
    expect(component.myTournaments.map((item) => item.competition.id)).toEqual([1]);
    expect(component.availableTournaments.map((item) => item.competition.id)).toEqual([2]);
    expect(component.previousResults[0].result).toBe('Victoria');
    expect(component.previousResults[0].score).toBe('6–4 | 6–3');
    expect(component.wins).toBe(1);
    expect(component.losses).toBe(0);
    expect(component.totalPlayed).toBe(1);
    expect(component.winPercentage).toBe(100);
  });

  it('should use only countable results for the table and statistics', () => {
    tokenService.saveAccessToken(createToken({ user_id: 10, role: 'Jugador' }));
    createComponent();

    const pastDateTime = new Date(Date.now() - 86_400_000).toISOString();
    const normalWin = match(1, 'FINALIZADO', pastDateTime, 1, [set(1, 6, 3)]);
    const walkoverLoss = {
      ...match(2, 'FINALIZADO', pastDateTime, 2, []),
      is_walkover: true,
      resolution_type: 'WALKOVER',
    };
    const retirementWin = {
      ...match(3, 'FINALIZADO', pastDateTime, 1, [set(1, 4, 2)]),
      resolution_type: 'RETIREMENT',
    };
    const bye = {
      ...match(4, 'FINALIZADO', pastDateTime, 1, []),
      player2: null,
    };
    const invalidWinner = match(5, 'FINALIZADO', pastDateTime, 99, []);

    flushPlayerDashboard([
      normalWin,
      walkoverLoss,
      retirementWin,
      bye,
      invalidWinner,
    ]);
    fixture.detectChanges();

    expect(component.previousResults.map((item) => item.match.id)).toEqual([1, 2, 3]);
    expect(component.previousResults.map((item) => item.result)).toEqual([
      'Victoria',
      'Derrota',
      'Victoria',
    ]);
    expect(component.wins).toBe(2);
    expect(component.losses).toBe(1);
    expect(component.totalPlayed).toBe(3);
    expect(component.winPercentage).toBe(67);
    expect(fixture.nativeElement.querySelectorAll('tr.result-row').length).toBe(
      component.totalPlayed
    );
  });

  it('shows retirement and Super Tie-Break with the shared score format', () => {
    tokenService.saveAccessToken(createToken({ user_id: 10, role: 'Jugador' }));
    createComponent();
    const playedAt = new Date(Date.now() - 86_400_000).toISOString();
    const retirement = {
      ...match(6, 'FINALIZADO', playedAt, 1, []),
      resolution_type: 'RETIREMENT',
    };
    const superTieBreak = match(7, 'FINALIZADO', playedAt, 1, [
      set(1, 4, 6),
      set(2, 6, 3),
      set(3, 10, 8, true),
    ]);

    flushPlayerDashboard([retirement, superTieBreak]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('RET');
    expect(fixture.nativeElement.textContent).toContain('[10–8]');
    expect(fixture.nativeElement.textContent).not.toContain('Sin sets');
  });

  it('should show neutral zero statistics when there are no countable results', () => {
    tokenService.saveAccessToken(createToken({ user_id: 10, role: 'Jugador' }));
    createComponent();

    flushPlayerDashboard([]);
    fixture.detectChanges();

    expect(component.previousResults).toEqual([]);
    expect(component.wins).toBe(0);
    expect(component.losses).toBe(0);
    expect(component.totalPlayed).toBe(0);
    expect(component.winPercentage).toBe(0);
    expect(component.resultDonutBackground).toBe('var(--bs-secondary-bg)');
    expect(fixture.nativeElement.textContent).toContain('Sin partidos jugados');
  });

  it('should navigate only confirmed registrations using their effective category', () => {
    tokenService.saveAccessToken(createToken({ user_id: 10, role: 'Jugador' }));
    spyOn(router, 'navigate');
    createComponent();
    const date = new Date(Date.now() + 86_400_000).toISOString().slice(0, 10);

    httpTesting.expectOne(`${environment.apiUrl}/players/`).flush([
      player(1, 10, 'Ana', 'Pérez'),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/competitions/`).flush([
      competition(1, 'Confirmado excepcional', date),
      competition(2, 'Pendiente', date),
      competition(3, 'Cancelado', date),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/registrations/`).flush([
      registration(1, 222, 'CONFIRMADA'),
      registration(2, 333, 'PENDIENTE'),
      registration(3, 444, 'CANCELADA'),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/matches/`).flush([]);
    httpTesting.expectOne(`${environment.apiUrl}/competition-categories/`).flush([
      competitionCategoryWithCategory(222, 1, 9),
      competitionCategoryWithCategory(333, 2, 5),
      competitionCategoryWithCategory(444, 3, 5),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/categories/`).flush([
      { id: 5, name: 'CUARTA' },
      { id: 9, name: 'PRIMERA' },
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/courts/`).flush([]);
    fixture.detectChanges();

    expect(component.myTournaments.length).toBe(2);
    expect(component.myTournaments[0].category).toBe('PRIMERA');

    const confirmedRow = fixture.nativeElement.querySelector(
      '[data-testid="confirmed-tournament-row"]'
    ) as HTMLButtonElement;
    const pendingRow = fixture.nativeElement.querySelector(
      '[data-testid="pending-tournament-row"]'
    ) as HTMLElement;

    confirmedRow.click();
    expect(router.navigate).toHaveBeenCalledWith([
      '/competitions', 1, 'categories', 222,
    ]);

    (router.navigate as jasmine.Spy).calls.reset();
    pendingRow.click();
    expect(router.navigate).not.toHaveBeenCalled();
    expect(confirmedRow.tagName).toBe('BUTTON');
    expect(confirmedRow.getAttribute('aria-label')).toContain('PRIMERA');
    expect(fixture.nativeElement.textContent).not.toContain('Ver');
    expect(fixture.nativeElement.querySelectorAll('[data-testid="confirmed-tournament-row"]').length).toBe(1);
    expect(fixture.nativeElement.querySelectorAll('[data-testid="pending-tournament-row"]').length).toBe(1);
  });

  function createComponent(): void {
    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  function createToken(payload: Record<string, unknown>): string {
    const encoded = btoa(JSON.stringify(payload))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
    return `header.${encoded}.signature`;
  }

  function flushPlayerDashboard(matches: object[]): void {
    const date = new Date(Date.now() + 86_400_000).toISOString().slice(0, 10);

    httpTesting.expectOne(`${environment.apiUrl}/players/`).flush([
      player(1, 10, 'Ana', 'Pérez'),
      player(2, 11, 'Beatriz', 'Soto'),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/competitions/`).flush([
      competition(1, 'Torneo', date),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/registrations/`).flush([]);
    httpTesting.expectOne(`${environment.apiUrl}/matches/`).flush(matches);
    httpTesting.expectOne(`${environment.apiUrl}/competition-categories/`).flush([
      competitionCategory(101, 1),
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/categories/`).flush([
      { id: 5, name: 'PRIMERA' },
    ]);
    httpTesting.expectOne(`${environment.apiUrl}/courts/`).flush([
      { id: 1, name: 'Cancha Central', status: 'AVAILABLE' },
    ]);
  }

  function player(id: number, user: number, firstName: string, lastName: string) {
    return {
      id, user, username: firstName, email: '', category: 5, rut: '',
      first_name: firstName, last_name: lastName, birth_date: null, phone: '',
    };
  }

  function competition(id: number, name: string, date: string) {
    return {
      id, name, type: 'ELIMINACION_DIRECTA', start_date: date, end_date: date,
      status: 'ABIERTA', registration_deadline: date,
    };
  }

  function competitionWithStatus(id: number, name: string, status: string, date: string) {
    return {
      id, name, type: 'ELIMINACION_DIRECTA', start_date: date, end_date: date,
      status, registration_deadline: date,
    };
  }

  function competitionCategory(id: number, competitionId: number) {
    return {
      id, competition: competitionId, category: 5, max_players: 16,
      minimum_players: 2, occupied_slots: 0, available_slots: 16,
      registered_players: [],
    };
  }

  function competitionCategoryWithCategory(
    id: number,
    competitionId: number,
    categoryId: number
  ) {
    return {
      ...competitionCategory(id, competitionId),
      category: categoryId,
    };
  }

  function registration(id: number, competitionCategory: number, status: string) {
    return {
      id,
      competition_category: competitionCategory,
      player: 1,
      registration_date: '2026-08-01',
      status,
      seed: null,
    };
  }

  function match(
    id: number,
    status: string,
    scheduledDateTime: string,
    winner: number | null,
    sets: object[],
    currentPlayerIsPlayer2 = false
  ) {
    return {
      id, competition_category: 101, court: 1,
      player1: currentPlayerIsPlayer2 ? 2 : 1,
      player2: currentPlayerIsPlayer2 ? 1 : 2,
      winner_player: winner, scheduled_date_time: scheduledDateTime, status,
      round: 1, is_walkover: false, resolution_type: 'NORMAL', sets,
    };
  }

  function set(
    id: number,
    gamesPlayer1: number,
    gamesPlayer2: number,
    isSuperTieBreak = false
  ) {
    return {
      id, set_number: id, games_player1: gamesPlayer1,
      games_player2: gamesPlayer2, is_super_tie_break: isSuperTieBreak,
    };
  }
});
