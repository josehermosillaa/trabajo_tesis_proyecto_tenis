import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';

import { TokenService } from '../../../../core/services/token';
import { MatchService } from '../../services/match';
import { MatchListComponent } from './match-list';

describe('MatchListComponent stable order and search', () => {
  let fixture: ComponentFixture<MatchListComponent>;
  let component: MatchListComponent;

  beforeEach(async () => {
    const service = jasmine.createSpyObj<MatchService>('MatchService', [
      'getCompetitions', 'getCompetitionCategories', 'getCategories', 'getPlayers',
      'getCourts', 'getMatches', 'deleteMatch',
    ]);
    service.getCompetitions.and.returnValue(of([{
      id: 1, name: 'Copa Supervisión', type: 'ELIMINACION_DIRECTA', start_date: '2026-09-01',
      end_date: '2026-09-10', status: 'EN_CURSO', registration_deadline: '2026-08-30',
    }]));
    service.getCompetitionCategories.and.returnValue(of([{
      id: 10, competition: 1, category: 5, max_players: 8, minimum_players: 2,
      occupied_slots: 2, available_slots: 6, registered_players: [],
    }]));
    service.getCategories.and.returnValue(of([{ id: 5, name: 'HONOR' }]));
    service.getPlayers.and.returnValue(of([
      { id: 1, user: 11, username: 'ana', email: 'ana@example.com', category: 5,
        rut: '11-1', first_name: 'Ana', last_name: 'Pérez', birth_date: null, phone: '' },
      { id: 2, user: 12, username: 'luis', email: 'luis@example.com', category: 5,
        rut: '22-2', first_name: 'Luis', last_name: 'Soto', birth_date: null, phone: '' },
    ]));
    service.getCourts.and.returnValue(of([{ id: 3, name: 'Cancha Central', status: 'AVAILABLE' }]));
    service.getMatches.and.returnValue(of([
      match(2, 1, 2, 'FINALIZADO', 3),
      match(5, 1, null, 'PROGRAMADO', null, 2, 5),
      match(6, 1, null, 'PROGRAMADO', null, 1, 6),
    ]));
    service.deleteMatch.and.returnValue(of(undefined));
    const token = jasmine.createSpyObj<TokenService>('TokenService', ['isAdministrativeUser']);
    token.isAdministrativeUser.and.returnValue(true);
    const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    await TestBed.configureTestingModule({
      imports: [MatchListComponent],
      providers: [
        { provide: MatchService, useValue: service },
        { provide: TokenService, useValue: token },
        { provide: Router, useValue: router },
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { paramMap: { get: () => null } } },
        },
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(MatchListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('uses id descending because Match has no creation timestamp', () => {
    expect(component.filteredMatches.map((item) => item.id)).toEqual([6, 5, 2]);
  });

  it('searches by player, status and court', () => {
    component.searchTerm = 'luis';
    expect(component.filteredMatches.map((item) => item.id)).toEqual([2]);
    component.searchTerm = 'finalizado';
    expect(component.filteredMatches.map((item) => item.id)).toEqual([2]);
    component.searchTerm = 'cancha central';
    expect(component.filteredMatches.map((item) => item.id)).toEqual([2]);
  });

  it('distinguishes a real first-round BYE from a future participant', () => {
    component.searchTerm = 'bye';
    expect(component.filteredMatches.map((item) => item.id)).toEqual([6]);
    component.searchTerm = 'por definir';
    expect(component.filteredMatches.map((item) => item.id)).toEqual([5]);
  });

  it('requires both real participants before opening a result', () => {
    expect(component.canOpenResult(component.matches.find((item) => item.id === 2)!)).toBeTrue();
    expect(component.canOpenResult(component.matches.find((item) => item.id === 5)!)).toBeFalse();
    expect(component.canOpenResult(component.matches.find((item) => item.id === 6)!)).toBeFalse();
  });

  it('handles empty and no-result searches', () => {
    component.searchTerm = '';
    expect(component.filteredMatches.length).toBe(3);
    component.searchTerm = 'nadie';
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('No se encontraron partidos.');
  });

  it('keeps the loaded total, search and table inside the list surface', () => {
    const card = fixture.nativeElement.querySelector('.match-list-card') as HTMLElement;

    expect(card.textContent).toContain('3 partidos registrados');
    expect(card.querySelector('#match-search')).not.toBeNull();
    expect(card.querySelector('table')).not.toBeNull();
    expect(card.querySelector('tbody .badge.text-bg-secondary')?.textContent).toContain('HONOR');
  });

  it('presents schedule placeholders as secondary information', () => {
    const secondaryTexts = Array.from<HTMLElement>(
      fixture.nativeElement.querySelectorAll('tbody .text-body-secondary')
    ).map((element) => element.textContent?.trim());

    expect(secondaryTexts).toContain('Sin cancha');
    expect(secondaryTexts).toContain('Sin programación');
  });

  function match(
    id: number,
    player1: number,
    player2: number | null,
    status: 'PROGRAMADO' | 'FINALIZADO',
    court: number | null,
    round: number | null = null,
    bracketPosition: number | null = null
  ) {
    return {
      id, competition_category: 10, court, player1, player2,
      winner_player: status === 'FINALIZADO' ? player1 : null,
      scheduled_date_time: null, status, round, bracket_position: bracketPosition,
      next_match: null, next_match_slot: null, is_walkover: false,
      resolution_type: 'NORMAL' as const, sets: [],
    };
  }
});
