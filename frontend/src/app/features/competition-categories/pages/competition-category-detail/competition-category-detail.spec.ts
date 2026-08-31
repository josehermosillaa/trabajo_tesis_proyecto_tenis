import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { TokenService } from '../../../../core/services/token';
import { CompetitionService } from '../../../competitions/services/competition';
import { MatchService } from '../../../matches/services/match';
import { PlayerService } from '../../../players/services/player';
import { BracketMatch, BracketResponse } from '../../models/competition-category.model';
import { CompetitionCategoryService } from '../../services/competition-category';
import { CompetitionCategoryDetailComponent } from './competition-category-detail';

describe('CompetitionCategoryDetailComponent scheduling', () => {
  let component: CompetitionCategoryDetailComponent;
  let fixture: ComponentFixture<CompetitionCategoryDetailComponent>;
  let matchService: jasmine.SpyObj<MatchService>;
  let competitionCategoryService: jasmine.SpyObj<CompetitionCategoryService>;
  let playerService: jasmine.SpyObj<PlayerService>;
  let competitionService: jasmine.SpyObj<CompetitionService>;
  let router: jasmine.SpyObj<Router>;

  const players = [
    {
      id: 1, user: 10, username: 'uno', email: '', category: 1, rut: '',
      first_name: 'Jugador', last_name: 'Uno', birth_date: null, phone: '',
    },
    {
      id: 2, user: 11, username: 'dos', email: '', category: 1, rut: '',
      first_name: 'Jugador', last_name: 'Dos', birth_date: null, phone: '',
    },
  ];

  beforeEach(async () => {
    matchService = jasmine.createSpyObj<MatchService>(
      'MatchService',
      ['getCourts', 'updateMatch']
    );
    competitionCategoryService = jasmine.createSpyObj<CompetitionCategoryService>(
      'CompetitionCategoryService',
      ['getBracket', 'generateBracket']
    );
    playerService = jasmine.createSpyObj<PlayerService>('PlayerService', ['getPlayers']);
    competitionService = jasmine.createSpyObj<CompetitionService>(
      'CompetitionService',
      ['getCompetition']
    );
    const tokenService = jasmine.createSpyObj<TokenService>(
      'TokenService',
      ['isAdministrativeUser']
    );
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);

    playerService.getPlayers.and.returnValue(of(players));
    matchService.getCourts.and.returnValue(of([
      { id: 1, name: 'Cancha 1', status: 'AVAILABLE' },
      { id: 2, name: 'Cancha 2', status: 'AVAILABLE' },
    ]));
    tokenService.isAdministrativeUser.and.returnValue(true);
    competitionService.getCompetition.and.returnValue(of({
      id: 8,
      name: 'Torneo',
      type: 'ELIMINACION_DIRECTA',
      start_date: '2026-09-01',
      end_date: '2026-09-15',
      status: 'EN_CURSO',
      registration_deadline: '2026-08-28',
    }));
    competitionCategoryService.getBracket.and.returnValue(of(bracket([
      match(1),
    ])));

    await TestBed.configureTestingModule({
      imports: [CompetitionCategoryDetailComponent],
      providers: [
        { provide: MatchService, useValue: matchService },
        { provide: CompetitionCategoryService, useValue: competitionCategoryService },
        { provide: PlayerService, useValue: playerService },
        { provide: CompetitionService, useValue: competitionService },
        { provide: TokenService, useValue: tokenService },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) => key === 'competitionId' ? '8' : '12',
              },
            },
          },
        },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();
  });

  it('shows Programar partido for a playable unscheduled match', () => {
    createWithMatches([match(1)]);
    expect(buttonTexts()).toContain('Programar partido');
  });

  it('shows Editar programación for a programmed match with scheduling', () => {
    createWithMatches([
      match(1, 'PROGRAMADO', '2026-09-05T19:30:00-04:00', 1),
    ]);
    expect(buttonTexts()).toContain('Editar programación');
  });

  it('adds persistent bracket return context when opening a result', () => {
    const bracketMatch = match(26);
    createWithMatches([bracketMatch]);

    component.goToResult(bracketMatch);

    expect(router.navigate).toHaveBeenCalledWith(
      ['/matches', 26, 'result'],
      {
        queryParams: {
          returnTo: 'bracket',
          competitionId: 8,
          competitionCategoryId: 12,
        },
      }
    );
  });

  it('does not show scheduling for FINALIZADO', () => {
    createWithMatches([match(1, 'FINALIZADO')]);
    expect(hasSchedulingButton()).toBeFalse();
  });

  it('does not show scheduling for EN_JUEGO', () => {
    createWithMatches([match(1, 'EN_JUEGO')]);
    expect(hasSchedulingButton()).toBeFalse();
  });

  it('does not show scheduling for CANCELADO', () => {
    createWithMatches([match(1, 'CANCELADO')]);
    expect(hasSchedulingButton()).toBeFalse();
  });

  it('does not show scheduling for a BYE', () => {
    createWithMatches([match(1, 'FINALIZADO', null, null, 1, null)]);
    expect(hasSchedulingButton()).toBeFalse();
  });

  it('does not show scheduling while participants are pending', () => {
    createWithMatches([match(1, 'PROGRAMADO', null, null, 2, null, null)]);
    expect(hasSchedulingButton()).toBeFalse();
  });

  it('prefills the reusable modal when editing scheduling', () => {
    createWithMatches([match(1)]);
    const scheduledMatch = match(1, 'PROGRAMADO', '2026-09-05T19:30:00', 2);

    component.openScheduleModal(scheduledMatch);

    expect(component.schedulingMatch).toBe(scheduledMatch);
    expect(component.scheduleForm.getRawValue()).toEqual({
      date: '2026-09-05',
      time: '19:30',
      court: 2,
    });
  });

  it('keeps the bracket visible when loading courts fails', () => {
    matchService.getCourts.and.returnValue(throwError(() => new Error('courts')));

    createWithMatches([match(1)]);

    expect(competitionCategoryService.getBracket).toHaveBeenCalled();
    expect(component.bracket).not.toBeNull();
    expect(component.errorMessage).toBe('');
    expect(component.courtsErrorMessage).toBe('No fue posible cargar las canchas.');
  });

  it('reports the courts error in the modal and prevents saving', () => {
    matchService.getCourts.and.returnValue(throwError(() => new Error('courts')));
    createWithMatches([match(1)]);
    component.openScheduleModal(match(1));
    component.scheduleForm.setValue({
      date: '2026-09-05',
      time: '19:30',
      court: 1,
    });

    component.saveSchedule();

    expect(component.scheduleErrorMessage).toBe('No fue posible cargar las canchas.');
    expect(matchService.updateMatch).not.toHaveBeenCalled();
  });

  it('keeps the bracket and scheduling form available when loading the period fails', () => {
    competitionService.getCompetition.and.returnValue(
      throwError(() => new Error('competition'))
    );
    const scheduledMatch = match(1);
    matchService.updateMatch.and.returnValue(of({
      ...scheduledMatch,
      player1: scheduledMatch.player1!,
      resolution_type: 'NORMAL',
    }));

    createWithMatches([scheduledMatch]);
    component.openScheduleModal(scheduledMatch);
    component.scheduleForm.setValue({
      date: '2027-01-01',
      time: '19:30',
      court: 1,
    });
    fixture.detectChanges();

    expect(component.bracket).not.toBeNull();
    expect(component.errorMessage).toBe('');
    expect(component.scheduleForm.valid).toBeTrue();
    expect(component.isScheduleOutsideCompetitionPeriod()).toBeFalse();
    expect(fixture.nativeElement.querySelector('.alert-warning')).toBeNull();

    component.saveSchedule();

    expect(matchService.updateMatch).toHaveBeenCalled();
  });

  it('keeps the players loading error handling', () => {
    playerService.getPlayers.and.returnValue(throwError(() => new Error('players')));

    fixture = TestBed.createComponent(CompetitionCategoryDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    expect(component.errorMessage).toBe('No fue posible cargar los jugadores.');
  });

  it('keeps the bracket loading error handling', () => {
    competitionCategoryService.getBracket.and.returnValue(
      throwError(() => ({ error: { detail: 'No fue posible cargar el cuadro.' } }))
    );

    fixture = TestBed.createComponent(CompetitionCategoryDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    expect(component.bracket).toBeNull();
    expect(component.errorMessage).toBeTruthy();
  });

  it('calls updateMatch and refreshes the bracket after success', () => {
    createWithMatches([match(1)]);
    const scheduledMatch = match(1);
    matchService.updateMatch.and.returnValue(of({
      ...scheduledMatch,
      player1: scheduledMatch.player1!,
      resolution_type: 'NORMAL',
    }));
    component.openScheduleModal(scheduledMatch);
    component.scheduleForm.setValue({
      date: '2026-09-05',
      time: '19:30',
      court: 2,
    });

    component.saveSchedule();

    expect(matchService.updateMatch).toHaveBeenCalledWith(1, {
      scheduled_date_time: '2026-09-05T19:30',
      court: 2,
    });
    expect(component.schedulingMatch).toBeNull();
    expect(competitionCategoryService.getBracket).toHaveBeenCalledTimes(2);
  });

  it('does not warn for a date inside the competition period', () => {
    createWithMatches([match(1)]);
    component.scheduleForm.controls.date.setValue('2026-09-10');
    expect(component.isScheduleOutsideCompetitionPeriod()).toBeFalse();
  });

  it('warns before the competition period', () => {
    createWithMatches([match(1)]);
    component.scheduleForm.controls.date.setValue('2026-08-31');
    expect(component.isScheduleOutsideCompetitionPeriod()).toBeTrue();
  });

  it('warns after the competition period', () => {
    createWithMatches([match(1)]);
    component.scheduleForm.controls.date.setValue('2026-09-16');
    expect(component.isScheduleOutsideCompetitionPeriod()).toBeTrue();
  });

  it('keeps saving enabled despite the period warning', () => {
    createWithMatches([match(1)]);
    const scheduledMatch = match(1);
    matchService.updateMatch.and.returnValue(of({
      ...scheduledMatch,
      player1: scheduledMatch.player1!,
      resolution_type: 'NORMAL',
    }));
    component.openScheduleModal(scheduledMatch);
    component.scheduleForm.setValue({
      date: '2026-09-16',
      time: '19:30',
      court: 1,
    });

    expect(component.isScheduleOutsideCompetitionPeriod()).toBeTrue();
    expect(component.scheduleForm.valid).toBeTrue();
    component.saveSchedule();
    expect(matchService.updateMatch).toHaveBeenCalled();
  });

  it('removes the warning after selecting a valid date again', () => {
    createWithMatches([match(1)]);
    component.scheduleForm.controls.date.setValue('2026-08-31');
    expect(component.isScheduleOutsideCompetitionPeriod()).toBeTrue();
    component.scheduleForm.controls.date.setValue('2026-09-01');
    expect(component.isScheduleOutsideCompetitionPeriod()).toBeFalse();
  });

  it('warns when the selected date is before today', () => {
    createWithMatches([match(1)]);
    component.scheduleForm.controls.date.setValue('2026-09-09');
    expect(component.isScheduleInPast(new Date(2026, 8, 10))).toBeTrue();
  });

  it('does not warn when the selected date is today', () => {
    createWithMatches([match(1)]);
    component.scheduleForm.controls.date.setValue('2026-09-10');
    expect(component.isScheduleInPast(new Date(2026, 8, 10))).toBeFalse();
  });

  it('does not warn when the selected date is in the future', () => {
    createWithMatches([match(1)]);
    component.scheduleForm.controls.date.setValue('2026-09-11');
    expect(component.isScheduleInPast(new Date(2026, 8, 10))).toBeFalse();
  });

  it('keeps a past-date warning non-blocking', () => {
    createWithMatches([match(1)]);
    const scheduledMatch = match(1);
    matchService.updateMatch.and.returnValue(of({
      ...scheduledMatch,
      player1: scheduledMatch.player1!,
      resolution_type: 'NORMAL',
    }));
    component.openScheduleModal(scheduledMatch);
    component.scheduleForm.setValue({
      date: '2026-09-09',
      time: '19:30',
      court: 1,
    });

    expect(component.isScheduleInPast(new Date(2026, 8, 10))).toBeTrue();
    expect(component.scheduleForm.valid).toBeTrue();
    component.saveSchedule();
    expect(matchService.updateMatch).toHaveBeenCalled();
  });

  it('keeps the past-date and competition-period warnings independent', () => {
    createWithMatches([match(1)]);
    component.scheduleForm.controls.date.setValue('2026-08-31');
    expect(component.isScheduleInPast(new Date(2026, 8, 10))).toBeTrue();
    expect(component.isScheduleOutsideCompetitionPeriod()).toBeTrue();
  });

  function createWithMatches(matches: BracketMatch[]): void {
    competitionCategoryService.getBracket.and.returnValue(of(bracket(matches)));
    fixture = TestBed.createComponent(CompetitionCategoryDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  function buttonTexts(): string[] {
    return Array.from(fixture.nativeElement.querySelectorAll('button'))
      .map((button: unknown) => (button as HTMLButtonElement).textContent?.trim() ?? '');
  }

  function hasSchedulingButton(): boolean {
    return buttonTexts().some((text) =>
      text === 'Programar partido' || text === 'Editar programación'
    );
  }

  function bracket(matches: BracketMatch[]): BracketResponse {
    return {
      competition_category: 12,
      competition: 8,
      competition_name: 'Torneo',
      category: 1,
      category_name: 'PRIMERA',
      generated: true,
      matches,
    };
  }

  function match(
    id: number,
    status: BracketMatch['status'] = 'PROGRAMADO',
    scheduledDateTime: string | null = null,
    court: number | null = null,
    round = 1,
    player1: number | null = 1,
    player2: number | null = 2
  ): BracketMatch {
    return {
      id,
      competition_category: 12,
      court,
      player1,
      player2,
      winner_player: status === 'FINALIZADO' ? player1 : null,
      scheduled_date_time: scheduledDateTime,
      status,
      round,
      bracket_position: id,
      next_match: null,
      next_match_slot: null,
      is_walkover: false,
      sets: [],
    };
  }
});
