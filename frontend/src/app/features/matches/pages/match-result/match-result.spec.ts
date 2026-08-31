import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';

import { TokenService } from '../../../../core/services/token';
import { MatchService } from '../../services/match';
import { MatchResultComponent } from './match-result';

describe('MatchResultComponent return navigation', () => {
  let component: MatchResultComponent;
  let fixture: ComponentFixture<MatchResultComponent>;
  let router: jasmine.SpyObj<Router>;
  let queryParams: Record<string, string>;

  beforeEach(async () => {
    queryParams = {};
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);

    const matchService = jasmine.createSpyObj<MatchService>(
      'MatchService',
      ['getPlayers', 'getMatch', 'getMatchSets']
    );
    matchService.getPlayers.and.returnValue(of([]));
    matchService.getMatch.and.returnValue(of({
      id: 26,
      competition_category: 5,
      court: null,
      player1: 1,
      player2: 2,
      winner_player: null,
      scheduled_date_time: null,
      status: 'PROGRAMADO',
      round: 1,
      is_walkover: false,
      resolution_type: 'NORMAL',
    }));
    matchService.getMatchSets.and.returnValue(of([]));

    const tokenService = jasmine.createSpyObj<TokenService>(
      'TokenService',
      ['isAdministrativeUser']
    );
    tokenService.isAdministrativeUser.and.returnValue(true);

    await TestBed.configureTestingModule({
      imports: [MatchResultComponent],
      providers: [
        { provide: MatchService, useValue: matchService },
        { provide: TokenService, useValue: tokenService },
        { provide: Router, useValue: router },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) => key === 'id' ? '26' : null,
              },
              queryParamMap: {
                get: (key: string) => queryParams[key] ?? null,
              },
            },
          },
        },
      ],
    }).compileComponents();
  });

  it('returns to the same bracket when opened to enter a result', () => {
    createWithBracketContext();
    component.goBack();
    expectBracketNavigation();
  });

  it('returns to the same bracket when opened to edit a result', () => {
    createWithBracketContext();
    component.goBack();
    expectBracketNavigation();
  });

  it('returns to matches when opened from the matches list', () => {
    createComponent();
    component.goBack();
    expect(router.navigate).toHaveBeenCalledWith(['/matches']);
  });

  it('returns to matches on direct access without query params', () => {
    createComponent();
    component.goBack();
    expect(router.navigate).toHaveBeenCalledWith(['/matches']);
  });

  it('preserves bracket return context after recreating the component', () => {
    setBracketContext();
    createComponent();
    fixture.destroy();
    router.navigate.calls.reset();

    createComponent();
    component.goBack();
    expectBracketNavigation();
  });

  it('ignores an incomplete bracket return context', () => {
    queryParams = {
      returnTo: 'bracket',
      competitionId: '8',
    };
    createComponent();
    component.goBack();
    expect(router.navigate).toHaveBeenCalledWith(['/matches']);
  });

  function setBracketContext(): void {
    queryParams = {
      returnTo: 'bracket',
      competitionId: '8',
      competitionCategoryId: '5',
    };
  }

  function createWithBracketContext(): void {
    setBracketContext();
    createComponent();
  }

  function createComponent(): void {
    fixture = TestBed.createComponent(MatchResultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  function expectBracketNavigation(): void {
    expect(router.navigate).toHaveBeenCalledWith([
      '/competitions',
      8,
      'categories',
      5,
    ]);
  }
});
