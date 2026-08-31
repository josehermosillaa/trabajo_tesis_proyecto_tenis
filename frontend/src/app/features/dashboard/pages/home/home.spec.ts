import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TokenService } from '../../../../core/services/token';
import { environment } from '../../../../../environments/environment';
import { HomeComponent } from './home';

describe('Home', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;
  let httpTesting: HttpTestingController;
  let tokenService: TokenService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomeComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    httpTesting = TestBed.inject(HttpTestingController);
    tokenService = TestBed.inject(TokenService);
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
    expect(component.previousResults[0].sets).toEqual(['6-4', '6-3']);
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

  function set(id: number, gamesPlayer1: number, gamesPlayer2: number) {
    return {
      id, set_number: id, games_player1: gamesPlayer1,
      games_player2: gamesPlayer2, is_super_tie_break: false,
    };
  }
});
