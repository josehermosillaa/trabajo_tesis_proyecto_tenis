import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { TokenService } from '../../../../core/services/token';
import { CompetitionService } from '../../../competitions/services/competition';
import { MatchService } from '../../../matches/services/match';
import { PlayerService } from '../../../players/services/player';
import { RegistrationService } from '../../../registrations/services/registration';
import {
  BracketMatch,
  BracketResponse,
  LadderResponse,
} from '../../models/competition-category.model';
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
  let tokenService: jasmine.SpyObj<TokenService>;
  let registrationService: jasmine.SpyObj<RegistrationService>;
  let routeData: Record<string, unknown>;

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
      [
        'getBracket',
        'generateBracket',
        'deleteBracket',
        'getLadder',
        'generateLadder',
        'deleteLadder',
      ]
    );
    playerService = jasmine.createSpyObj<PlayerService>('PlayerService', ['getPlayers']);
    competitionService = jasmine.createSpyObj<CompetitionService>(
      'CompetitionService',
      ['getCompetition']
    );
    tokenService = jasmine.createSpyObj<TokenService>(
      'TokenService',
      ['isAdministrativeUser']
    );
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    registrationService = jasmine.createSpyObj<RegistrationService>(
      'RegistrationService',
      ['getRegistrations']
    );
    routeData = {};

    playerService.getPlayers.and.returnValue(of(players));
    matchService.getCourts.and.returnValue(of([
      { id: 1, name: 'Cancha 1', status: 'AVAILABLE' },
      { id: 2, name: 'Cancha 2', status: 'AVAILABLE' },
    ]));
    tokenService.isAdministrativeUser.and.returnValue(true);
    registrationService.getRegistrations.and.returnValue(of([{
      id: 1,
      competition_category: 12,
      player: 1,
      registration_date: '2026-08-20',
      status: 'CONFIRMADA',
      seed: null,
    }]));
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
    competitionCategoryService.getLadder.and.returnValue(of(ladder()));
    competitionCategoryService.generateLadder.and.returnValue(of({
      detail: 'Escalerilla generada correctamente.',
      competition_category: 12,
      matches: [],
    }));
    competitionCategoryService.deleteLadder.and.returnValue(of({
      detail: 'Escalerilla eliminada correctamente.',
      deleted_matches: 1,
      deleted_scheduled_matches: 0,
      deleted_standings: 2,
    }));
    competitionCategoryService.deleteBracket.and.returnValue(of({
      detail: 'Cuadro eliminado correctamente.',
      deleted_matches: 1,
      deleted_scheduled_matches: 0,
    }));

    await TestBed.configureTestingModule({
      imports: [CompetitionCategoryDetailComponent],
      providers: [
        { provide: MatchService, useValue: matchService },
        { provide: CompetitionCategoryService, useValue: competitionCategoryService },
        { provide: PlayerService, useValue: playerService },
        { provide: CompetitionService, useValue: competitionService },
        { provide: TokenService, useValue: tokenService },
        { provide: RegistrationService, useValue: registrationService },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              get data() { return routeData; },
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

  it('shows delete bracket only to administrative users with a bracket', () => {
    createWithMatches([match(1)]);
    expect(buttonTexts()).toContain('Eliminar cuadro');
    expect(deleteBracketButton().disabled).toBeFalse();

    fixture.destroy();
    tokenService.isAdministrativeUser.and.returnValue(false);
    createWithMatches([match(1)]);
    expect(buttonTexts()).not.toContain('Eliminar cuadro');
  });

  it('uses contextual confirmed participants without loading all players for a player', () => {
    tokenService.isAdministrativeUser.and.returnValue(false);
    createWithMatches([match(1)]);

    expect(playerService.getPlayers).not.toHaveBeenCalled();
    expect(fixture.nativeElement.textContent).toContain('Jugador Uno');
    expect(fixture.nativeElement.textContent).toContain('Jugador Dos');
    expect(buttonTexts()).not.toContain('Generar cuadro');
    expect(buttonTexts()).not.toContain('Eliminar cuadro');
    expect(hasSchedulingButton()).toBeFalse();
    expect(buttonTexts()).not.toContain('Ingresar resultado');

    component.goBack();
    expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
  });

  it('does not show delete bracket when the bracket does not exist', () => {
    createWithBracket(bracket([], false));
    expect(buttonTexts()).not.toContain('Eliminar cuadro');
  });

  it('opens the delete modal and explains preserved registrations and seeds', () => {
    createWithBracket(bracket([match(1)], true, true, 2));

    component.openDeleteBracketModal();
    fixture.detectChanges();

    expect(component.showDeleteBracketModal).toBeTrue();
    expect(fixture.nativeElement.textContent).toContain(
      'Las inscripciones y cabezas de serie se conservarán.'
    );
    expect(fixture.nativeElement.textContent).toContain(
      'También se eliminará la programación de 2 partidos.'
    );
  });

  it('cancels deletion without calling the API', () => {
    createWithMatches([match(1)]);
    component.openDeleteBracketModal();

    component.closeDeleteBracketModal();

    expect(component.showDeleteBracketModal).toBeFalse();
    expect(competitionCategoryService.deleteBracket).not.toHaveBeenCalled();
  });

  it('deletes once and refreshes the bracket after success', () => {
    createWithMatches([match(1)]);
    component.openDeleteBracketModal();
    const callsBeforeDelete =
      competitionCategoryService.getBracket.calls.count();

    component.deleteBracket();
    component.deleteBracket();

    expect(competitionCategoryService.deleteBracket).toHaveBeenCalledTimes(1);
    expect(competitionCategoryService.deleteBracket).toHaveBeenCalledWith(12);
    expect(competitionCategoryService.getBracket.calls.count()).toBe(
      callsBeforeDelete + 1
    );
    expect(component.showDeleteBracketModal).toBeFalse();
  });

  it('keeps the bracket visible when deletion fails', () => {
    competitionCategoryService.deleteBracket.and.returnValue(throwError(() => ({
      error: { detail: 'No se puede eliminar el cuadro.' },
    })));
    createWithMatches([match(1)]);
    component.openDeleteBracketModal();

    component.deleteBracket();

    expect(component.bracket).not.toBeNull();
    expect(component.showDeleteBracketModal).toBeTrue();
    expect(component.deleteBracketErrorMessage).toContain(
      'No se puede eliminar el cuadro.'
    );
  });

  it('disables deletion and exposes the block reason without a permanent alert', () => {
    const reason = 'No se puede eliminar el cuadro porque existen resultados.';
    createWithBracket(bracket([match(1)], true, false, 0, reason));

    component.openDeleteBracketModal();
    fixture.detectChanges();

    const reasonElement = fixture.nativeElement.querySelector(
      '[data-testid="delete-bracket-block-reason"]'
    ) as HTMLElement;

    expect(component.showDeleteBracketModal).toBeFalse();
    expect(competitionCategoryService.deleteBracket).not.toHaveBeenCalled();
    expect(buttonTexts()).toContain('Eliminar cuadro');
    expect(deleteBracketButton().disabled).toBeTrue();
    expect(reasonElement.getAttribute('title')).toBe(reason);
    expect(reasonElement.getAttribute('aria-label')).toBe(reason);
    expect(reasonElement.getAttribute('tabindex')).toBe('0');
    expect(
      Array.from(fixture.nativeElement.querySelectorAll('.alert'))
        .some((element: unknown) =>
          (element as HTMLElement).textContent?.includes(reason)
        )
    ).toBeFalse();
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

  it('keeps the modal values when the backend reports a scheduling conflict', () => {
    const conflictMessage =
      'La cancha seleccionada ya tiene un partido programado en ese horario.';
    matchService.updateMatch.and.returnValue(throwError(() => ({
      error: { court: [conflictMessage] },
    })));
    const scheduledMatch = match(1);
    createWithMatches([scheduledMatch]);
    component.openScheduleModal(scheduledMatch);
    component.scheduleForm.setValue({
      date: '2026-09-05',
      time: '19:30',
      court: 2,
    });

    component.saveSchedule();

    expect(component.schedulingMatch).toBe(scheduledMatch);
    expect(component.scheduleForm.getRawValue()).toEqual({
      date: '2026-09-05',
      time: '19:30',
      court: 2,
    });
    expect(component.scheduleErrorMessage).toContain(conflictMessage);
    expect(competitionCategoryService.getBracket).toHaveBeenCalledTimes(1);
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

  it('loads ladder and never requests bracket for ESCALERILLA', () => {
    createLadderView();

    expect(competitionCategoryService.getLadder).toHaveBeenCalledWith(12);
    expect(competitionCategoryService.getBracket).not.toHaveBeenCalled();
    expect(fixture.nativeElement.textContent).toContain('Tabla de posiciones');
    expect(fixture.nativeElement.textContent).toContain('Jugador Uno');
    expect(fixture.nativeElement.textContent).toContain('4');
  });

  it('keeps requesting bracket and not ladder for direct elimination', () => {
    createWithMatches([match(1)]);

    expect(competitionCategoryService.getBracket).toHaveBeenCalled();
    expect(competitionCategoryService.getLadder).not.toHaveBeenCalled();
  });

  it('keeps the ladder detail as a summary with a management action', () => {
    createLadderView(ladder(true, '2026-09-05T19:30:00-04:00'));

    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Partidos');
    expect(text).toContain('1 generados');
    expect(buttonTexts()).toContain('Gestionar partidos');
    expect(text).not.toContain('05/09/2026');
  });

  it('shows generation only to administrators when ladder is not generated', () => {
    createLadderView(ladder(false));
    expect(buttonTexts()).toContain('Generar escalerilla');

    fixture.destroy();
    tokenService.isAdministrativeUser.and.returnValue(false);
    createLadderView(ladder(false));
    expect(buttonTexts()).not.toContain('Generar escalerilla');
  });

  it('shows enabled deletion to admin or organizer and never to players', () => {
    createLadderView(ladder());
    expect(deleteLadderButton().disabled).toBeFalse();

    fixture.destroy();
    tokenService.isAdministrativeUser.and.returnValue(false);
    createLadderView(ladder());
    expect(buttonTexts()).not.toContain('Eliminar escalerilla');
  });

  it('disables ladder deletion and exposes the backend block reason', () => {
    const response = ladder();
    response.can_delete = false;
    response.delete_block_reason = 'Existen partidos disputados o resultados registrados.';
    createLadderView(response);

    expect(deleteLadderButton().disabled).toBeTrue();
    expect(fixture.nativeElement.textContent).toContain(response.delete_block_reason);
    component.openDeleteLadderModal();
    expect(component.showDeleteLadderModal).toBeFalse();
  });

  it('opens and closes the own ladder deletion modal with scheduled count', () => {
    const response = ladder();
    response.scheduled_matches_count = 3;
    createLadderView(response);

    component.openDeleteLadderModal();
    fixture.detectChanges();
    expect(component.showDeleteLadderModal).toBeTrue();
    expect(fixture.nativeElement.textContent).toContain(
      'También se eliminará la programación de 3 partidos.'
    );

    component.closeDeleteLadderModal();
    expect(component.showDeleteLadderModal).toBeFalse();
  });

  it('deletes ladder once and reloads ladder after success', () => {
    createLadderView(ladder());
    component.openDeleteLadderModal();
    const callsBeforeDelete = competitionCategoryService.getLadder.calls.count();

    component.deleteLadder();
    component.deleteLadder();

    expect(competitionCategoryService.deleteLadder).toHaveBeenCalledTimes(1);
    expect(competitionCategoryService.deleteLadder).toHaveBeenCalledWith(12);
    expect(competitionCategoryService.getLadder.calls.count()).toBe(
      callsBeforeDelete + 1
    );
    expect(component.showDeleteLadderModal).toBeFalse();
  });

  it('shows generation again after deleted ladder response is reloaded', () => {
    const generated = ladder();
    const notGenerated = ladder(false);
    createLadderView(generated);
    competitionCategoryService.getLadder.and.returnValue(of(notGenerated));
    component.openDeleteLadderModal();

    component.deleteLadder();
    fixture.detectChanges();

    expect(component.ladder?.generated).toBeFalse();
    expect(buttonTexts()).toContain('Generar escalerilla');
  });

  it('generates ladder and reloads it after success', () => {
    spyOn(window, 'confirm').and.returnValue(true);
    createLadderView(ladder(false));
    const callsBefore = competitionCategoryService.getLadder.calls.count();

    component.generateLadder();

    expect(competitionCategoryService.generateLadder).toHaveBeenCalledWith(12);
    expect(competitionCategoryService.getLadder.calls.count()).toBe(callsBefore + 1);
  });

  it('shows the backend generation error', () => {
    spyOn(window, 'confirm').and.returnValue(true);
    competitionCategoryService.generateLadder.and.returnValue(throwError(() => ({
      error: { detail: 'Se requieren al menos 2 participantes confirmados.' },
    })));
    createLadderView(ladder(false));

    component.generateLadder();
    fixture.detectChanges();

    expect(component.errorMessage).toContain('Se requieren al menos 2');
    expect(fixture.nativeElement.textContent).toContain('Se requieren al menos 2');
  });

  it('reuses scheduling and result actions in ladder match management', () => {
    createLadderManagement();

    expect(buttonTexts()).toContain('Programar partido');
    expect(buttonTexts()).toContain('Ingresar resultado');
  });

  it('searches ladder matches by player1 and player2 case-insensitively', () => {
    createLadderManagement();

    component.matchSearch = 'jugador uno';
    expect(component.filteredLadderMatches.map((item) => item.id)).toEqual([1]);

    component.matchSearch = 'DOS';
    expect(component.filteredLadderMatches.map((item) => item.id)).toEqual([1]);
  });

  it('combines the unscheduled, scheduled and finished filters with ladder data', () => {
    const response = ladder();
    const base = response.matches[0];
    response.matches = [
      base,
      { ...base, id: 2, scheduled_date_time: '2026-09-05T19:30:00-04:00', court: 1 },
      { ...base, id: 3, status: 'FINALIZADO', winner_player: 1 },
    ];
    createLadderManagement(response);

    component.ladderMatchFilter = 'UNSCHEDULED';
    expect(component.filteredLadderMatches.map((item) => item.id)).toEqual([1]);
    component.ladderMatchFilter = 'SCHEDULED';
    expect(component.filteredLadderMatches.map((item) => item.id)).toEqual([2]);
    component.ladderMatchFilter = 'FINISHED';
    expect(component.filteredLadderMatches.map((item) => item.id)).toEqual([3]);
  });

  it('formats normal sets, Super Tie-Break, walkover and retirement clearly', () => {
    const base = ladder().matches[0];
    expect(componentScore({
      ...base,
      sets: [
        { id: 1, set_number: 1, games_player1: 6, games_player2: 3, is_super_tie_break: false },
        { id: 2, set_number: 2, games_player1: 6, games_player2: 4, is_super_tie_break: false },
      ],
    })).toBe('6–3 | 6–4');
    expect(componentScore({
      ...base,
      sets: [
        { id: 1, set_number: 1, games_player1: 4, games_player2: 6, is_super_tie_break: false },
        { id: 2, set_number: 2, games_player1: 6, games_player2: 3, is_super_tie_break: false },
        { id: 3, set_number: 3, games_player1: 10, games_player2: 12, is_super_tie_break: true },
      ],
    })).toBe('4–6 | 6–3 | [10–12]');
    expect(componentScore({ ...base, resolution_type: 'WALKOVER', is_walkover: true })).toBe('WO');
    expect(componentScore({
      ...base,
      resolution_type: 'RETIREMENT',
      sets: [{
        id: 1, set_number: 1, games_player1: 2, games_player2: 1,
        is_super_tie_break: false, is_incomplete: true,
      }],
    })).toBe('2–1 RET');
  });

  it('shows a player only own scheduled and finished matches, never unscheduled or third-party matches', () => {
    tokenService.isAdministrativeUser.and.returnValue(false);
    const response = ladder();
    const base = response.matches[0];
    response.matches = [
      { ...base, id: 1 },
      { ...base, id: 2, scheduled_date_time: '2026-09-05T19:30:00-04:00', court: 1 },
      { ...base, id: 3, status: 'FINALIZADO', winner_player: 1 },
      { ...base, id: 4, player1: 2, player2: 3, scheduled_date_time: '2026-09-06T18:00:00-04:00', court: 1 },
    ];
    createLadderView(response);

    expect(component.ladderStandings.length).toBe(response.standings.length);
    expect(component.playerUpcomingMatches.map((item) => item.id)).toEqual([2]);
    expect(component.playerFinishedMatches.map((item) => item.id)).toEqual([3]);
    expect(fixture.nativeElement.textContent).toContain('Mis partidos');
    expect(fixture.nativeElement.textContent).toContain('05/09/2026 19:30');
    expect(buttonTexts()).not.toContain('Gestionar partidos');
    expect(hasSchedulingButton()).toBeFalse();
    expect(buttonTexts()).not.toContain('Ingresar resultado');
  });

  it('keeps ladder actions read-only for players', () => {
    tokenService.isAdministrativeUser.and.returnValue(false);
    createLadderView();

    expect(buttonTexts()).not.toContain('Programar partido');
    expect(buttonTexts()).not.toContain('Ingresar resultado');
    expect(buttonTexts()).not.toContain('Generar escalerilla');
  });

  function createLadderView(response: LadderResponse = ladder()): void {
    competitionService.getCompetition.and.returnValue(of({
      id: 8,
      name: 'Torneo Escalerilla',
      type: 'ESCALERILLA',
      start_date: '2026-09-01',
      end_date: '2026-09-15',
      status: 'EN_CURSO',
      registration_deadline: '2026-08-28',
    }));
    competitionCategoryService.getLadder.and.returnValue(of(response));
    fixture = TestBed.createComponent(CompetitionCategoryDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  function createLadderManagement(response: LadderResponse = ladder()): void {
    routeData = { ladderMatchManagement: true };
    createLadderView(response);
  }

  function componentScore(matchValue: LadderResponse['matches'][number]): string {
    if (!component) {
      createLadderView();
    }
    return component.getReadableScore(matchValue);
  }

  function createWithMatches(matches: BracketMatch[]): void {
    createWithBracket(bracket(matches));
  }

  function createWithBracket(response: BracketResponse): void {
    competitionCategoryService.getBracket.and.returnValue(of(response));
    fixture = TestBed.createComponent(CompetitionCategoryDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  function buttonTexts(): string[] {
    return Array.from(fixture.nativeElement.querySelectorAll('button'))
      .map((button: unknown) => (button as HTMLButtonElement).textContent?.trim() ?? '');
  }

  function deleteBracketButton(): HTMLButtonElement {
    return Array.from(
      fixture.nativeElement.querySelectorAll('button')
    ).find(
      (button: unknown) =>
        (button as HTMLButtonElement).textContent?.trim() ===
        'Eliminar cuadro'
    ) as HTMLButtonElement;
  }

  function deleteLadderButton(): HTMLButtonElement {
    return Array.from(
      fixture.nativeElement.querySelectorAll('button')
    ).find(
      (button: unknown) =>
        (button as HTMLButtonElement).textContent?.trim() ===
        'Eliminar escalerilla'
    ) as HTMLButtonElement;
  }

  function hasSchedulingButton(): boolean {
    return buttonTexts().some((text) =>
      text === 'Programar partido' || text === 'Editar programación'
    );
  }

  function bracket(
    matches: BracketMatch[],
    generated = true,
    canDelete = true,
    scheduledMatchesCount = 0,
    deleteBlockReason: string | null = null
  ): BracketResponse {
    return {
      competition_category: 12,
      competition: 8,
      competition_name: 'Torneo',
      category: 1,
      category_name: 'PRIMERA',
      participants: players.map((player) => ({
        id: player.id,
        first_name: player.first_name,
        last_name: player.last_name,
      })),
      generated,
      can_delete: canDelete,
      scheduled_matches_count: scheduledMatchesCount,
      delete_block_reason: deleteBlockReason,
      matches,
    };
  }

  function ladder(
    generated = true,
    scheduledDateTime: string | null = null
  ): LadderResponse {
    const ladderMatch = {
      ...match(1, 'PROGRAMADO', scheduledDateTime, scheduledDateTime ? 1 : null),
      round: null,
      bracket_position: null,
      player1: 1,
      resolution_type: 'NORMAL' as const,
    };

    return {
      competition_category: {
        id: 12,
        competition: 8,
        category: 1,
        max_players: 8,
        minimum_players: 2,
        occupied_slots: 2,
        available_slots: 6,
        registered_players: [],
      },
      participants: players.map((player, index) => ({
        registration: index + 1,
        player: player.id,
        first_name: player.first_name,
        last_name: player.last_name,
      })),
      standings: generated ? [
        {
          id: 1,
          competition_category: 12,
          player: 1,
          position: 1,
          matches_played: 1,
          matches_won: 1,
          matches_lost: 0,
          sets_won: 2,
          sets_lost: 0,
          sets_difference: 2,
          games_won: 12,
          games_lost: 4,
          games_difference: 8,
          points: 4,
          walkovers_won: 0,
          walkovers_lost: 0,
        },
      ] : [],
      matches: generated ? [ladderMatch] : [],
      generated,
      can_delete: generated,
      scheduled_matches_count: scheduledDateTime ? 1 : 0,
      delete_block_reason: generated ? null : 'La escalerilla no ha sido generada.',
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
