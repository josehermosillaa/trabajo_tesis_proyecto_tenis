import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

import {
  CommonModule,
} from '@angular/common';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';

import {
  ActivatedRoute,
  Router,
} from '@angular/router';

import {
  CompetitionCategoryService,
} from '../../services/competition-category';

import {
  BracketMatch,
  BracketResponse,
  LadderResponse,
  Standing,
} from '../../models/competition-category.model';
import { Match } from '../../../matches/models/match.model';

import {
  Player,
} from '../../../players/models/player.model';

import {
  PlayerService,
} from '../../../players/services/player';
import { TokenService } from '../../../../core/services/token';
import {
  Court,
  MatchService,
} from '../../../matches/services/match';
import {
  CompetitionService,
} from '../../../competitions/services/competition';
import {
  Competition,
} from '../../../competitions/models/competition.model';
import { TemporalInputComponent } from '../../../../shared/date-time/temporal-input.component';
import { UiDateTimePipe } from '../../../../shared/date-time/ui-date-time.pipe';
import { formatMatchScore } from '../../../matches/utils/match-score.utils';
import { RegistrationService } from '../../../registrations/services/registration';


interface BracketRound {
  round: number;
  name: string;
  matches: BracketMatch[];
}

type CategoryMatch = BracketMatch | Match;


@Component({
  selector: 'app-competition-category-detail',

  imports: [
    CommonModule,
    ReactiveFormsModule,
    TemporalInputComponent,
    UiDateTimePipe,
  ],

  templateUrl:
    './competition-category-detail.html',

  styleUrl:
    './competition-category-detail.scss',
})
export class CompetitionCategoryDetailComponent
  implements OnInit {

  private readonly competitionCategoryService =
    inject(
      CompetitionCategoryService
    );

  private readonly playerService =
    inject(
      PlayerService
    );

  private readonly route =
    inject(
      ActivatedRoute
    );

  private readonly router =
    inject(
      Router
    );

  private readonly matchService =
    inject(
      MatchService
    );

  private readonly competitionService =
    inject(
      CompetitionService
    );

  private readonly fb =
    inject(
      FormBuilder
    );

  private readonly tokenService =
    inject(TokenService);

  private readonly registrationService =
    inject(RegistrationService);

  isAdministrativeUser(): boolean {
    return this.tokenService.isAdministrativeUser();
  }


  competitionId:
    number | null = null;

  competitionCategoryId:
    number | null = null;

  ladderMatchManagementMode = false;

  currentPlayerId:
    number | null = null;

  matchSearch = '';

  ladderMatchFilter:
    'ALL' | 'UNSCHEDULED' | 'SCHEDULED' | 'IN_PROGRESS' | 'FINISHED' = 'ALL';


  bracket:
    BracketResponse | null = null;

  ladder:
    LadderResponse | null = null;

  rounds:
    BracketRound[] = [];

  players:
    Player[] = [];

  courts:
    Court[] = [];

  competition:
    Competition | null = null;

  schedulingMatch:
    CategoryMatch | null = null;

  savingSchedule = false;

  scheduleErrorMessage = '';

  courtsErrorMessage = '';

  readonly scheduleForm =
    this.fb.group({
      date: this.fb.nonNullable.control(
        '',
        Validators.required
      ),
      time: this.fb.nonNullable.control(
        '',
        Validators.required
      ),
      court: this.fb.control<number | null>(
        null,
        Validators.required
      ),
    });


  loading = false;

  generating = false;

  deletingBracket = false;

  showDeleteBracketModal = false;

  deleteBracketErrorMessage = '';

  deletingLadder = false;

  showDeleteLadderModal = false;

  deleteLadderErrorMessage = '';

  errorMessage = '';

  successMessage = '';


  ngOnInit(): void {

    this.ladderMatchManagementMode =
      this.route.snapshot.data?.['ladderMatchManagement'] === true;

    const competitionIdParam =
      this.route.snapshot
        .paramMap
        .get('competitionId');

    const competitionCategoryIdParam =
      this.route.snapshot
        .paramMap
        .get('competitionCategoryId');


    if (
      !competitionIdParam
      ||
      !competitionCategoryIdParam
    ) {

      this.errorMessage =
        'No se especificó correctamente la competencia o categoría.';

      return;
    }


    this.competitionId =
      Number(
        competitionIdParam
      );

    this.competitionCategoryId =
      Number(
        competitionCategoryIdParam
      );


    this.loadCompetition();
  }


  // =====================================================
  // CARGA
  // =====================================================

  private loadCompetition(): void {
    if (this.competitionId === null) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.competitionService.getCompetition(this.competitionId).subscribe({
      next: (competition) => {
        this.competition = competition;

        this.loadCourts();

        if (competition.type === 'ESCALERILLA') {
          if (this.isAdministrativeUser()) {
            this.loadLadder();
          } else {
            this.loadCurrentPlayerIdentity();
          }
        } else if (this.isAdministrativeUser()) {
          this.loadPlayers();
        } else {
          this.refreshCurrentView();
        }
      },
      error: (error) => {
        console.error('Error al cargar competencia:', error);
        this.competition = null;

        if (this.isAdministrativeUser()) {
          this.loadCourts();
          this.loadPlayers();
        } else {
          this.loadBracket();
        }
      },
    });
  }

  private loadCurrentPlayerIdentity(): void {
    if (this.competitionCategoryId === null) {
      return;
    }

    this.registrationService.getRegistrations().subscribe({
      next: (registrations) => {
        this.currentPlayerId = registrations.find(
          (registration) =>
            Number(registration.competition_category) ===
              Number(this.competitionCategoryId)
            && registration.status === 'CONFIRMADA'
        )?.player ?? null;
        this.loadLadder();
      },
      error: () => {
        this.currentPlayerId = null;
        this.loadLadder();
      },
    });
  }

  private loadPlayers(): void {

    this.loading = true;

    this.errorMessage = '';

    this.playerService
      .getPlayers()
      .subscribe({

        next: (players) => {

          this.players =
            players;

          this.loadBracket();
        },

        error: (error) => {

          console.error(
            'Error al cargar jugadores:',
            error
          );

          this.errorMessage =
            'No fue posible cargar los jugadores.';

          this.loading = false;
        },
      });
  }

  private loadCourts(): void {

    this.courtsErrorMessage = '';

    this.matchService
      .getCourts()
      .subscribe({

        next: (courts) => {

          this.courts = courts;
        },

        error: (error) => {

          console.error(
            'Error al cargar canchas:',
            error
          );

          this.courts = [];

          this.courtsErrorMessage =
            'No fue posible cargar las canchas.';
        },
      });
  }


  loadBracket(): void {

    if (
      this.competitionCategoryId ===
      null
    ) {
      return;
    }

    this.loading = true;

    this.errorMessage = '';

    this.competitionCategoryService
      .getBracket(
        this.competitionCategoryId
      )
      .subscribe({

        next: (response) => {

          this.bracket =
            response;

          this.buildRounds();

          this.loading = false;

          this.loadCompetitionPeriod(
            response.competition
          );
        },

        error: (error) => {

          console.error(
            'Error al cargar cuadro:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.loading =
            false;
        },
      });
  }

  private loadCompetitionPeriod(
    competitionId: number
  ): void {

    if (
      this.competition?.id ===
      competitionId
    ) {

      return;
    }

    this.competitionService
      .getCompetition(
        competitionId
      )
      .subscribe({

        next: (competition) => {

          this.competition =
            competition;

        },

        error: (error) => {

          console.error(
            'Error al cargar competencia:',
            error
          );

          this.competition = null;
        },
      });
  }

  loadLadder(): void {
    if (this.competitionCategoryId === null) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.competitionCategoryService
      .getLadder(this.competitionCategoryId)
      .subscribe({
        next: (response) => {
          this.ladder = {
            ...response,
            standings: [...response.standings].sort(
              (left, right) =>
                (left.position ?? Number.MAX_SAFE_INTEGER) -
                (right.position ?? Number.MAX_SAFE_INTEGER)
            ),
          };
          this.loading = false;
        },
        error: (error) => {
          console.error('Error al cargar escalerilla:', error);
          this.errorMessage = this.getBackendErrorMessage(error);
          this.loading = false;
        },
      });
  }


  // =====================================================
  // GENERAR CUADRO
  // =====================================================

  generateBracket(): void {

    if (
      this.competitionCategoryId ===
      null
    ) {
      return;
    }


    const confirmed =
      window.confirm(
        '¿Deseas generar el cuadro de esta categoría? '
        + 'Una vez generado no podrá volver a generarse '
        + 'mientras existan sus partidos.'
      );


    if (!confirmed) {
      return;
    }


    this.generating =
      true;

    this.errorMessage =
      '';

    this.successMessage =
      '';


    this.competitionCategoryService
      .generateBracket(
        this.competitionCategoryId
      )
      .subscribe({

        next: () => {

          this.generating =
            false;

          this.showSuccessMessage(
            'Cuadro generado correctamente.'
          );

          this.loadBracket();
        },

        error: (error) => {

          console.error(
            'Error al generar cuadro:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.generating =
            false;
        },
      });
  }


  // =====================================================
  // CONSTRUIR RONDAS
  // =====================================================

  private buildRounds(): void {

    if (
      !this.bracket
      ||
      this.bracket.matches.length ===
        0
    ) {

      this.rounds = [];

      return;
    }


    const totalRounds =
      Math.max(
        ...this.bracket.matches.map(
          (match) =>
            match.round
        )
      );


    const rounds:
      BracketRound[] = [];


    for (
      let round = 1;
      round <= totalRounds;
      round++
    ) {

      const matches =
        this.bracket.matches
          .filter(
            (match) =>
              match.round ===
              round
          )
          .sort(
            (a, b) =>
              a.bracket_position -
              b.bracket_position
          );


      rounds.push(
        {
          round,
          name:
            this.getRoundName(
              round,
              totalRounds
            ),
          matches,
        }
      );
    }


    this.rounds =
      rounds;
  }


  // =====================================================
  // NOMBRE DE RONDA
  // =====================================================

  getRoundName(
    round: number,
    totalRounds: number
  ): string {

    const remaining =
      totalRounds - round;


    if (
      remaining === 0
    ) {
      return 'Final';
    }


    if (
      remaining === 1
    ) {
      return 'Semifinal';
    }


    if (
      remaining === 2
    ) {
      return 'Cuartos de final';
    }


    if (
      remaining === 3
    ) {
      return 'Octavos de final';
    }


    if (
      remaining === 4
    ) {
      return 'Dieciseisavos de final';
    }


    return (
      `Ronda ${round}`
    );
  }


  // =====================================================
  // FINAL / CAMPEÓN
  // =====================================================

  getFinalMatch():
    BracketMatch | null {

    if (
      this.rounds.length ===
      0
    ) {
      return null;
    }


    const finalRound =
      this.rounds[
        this.rounds.length - 1
      ];


    return (
      finalRound.matches[0]
      ?? null
    );
  }


  getChampionId():
    number | null {

    const finalMatch =
      this.getFinalMatch();


    if (
      !finalMatch
      ||
      finalMatch.status !==
        'FINALIZADO'
      ||
      finalMatch.winner_player ===
        null
    ) {

      return null;
    }


    return (
      finalMatch.winner_player
    );
  }


  getChampionName():
    string {

    const championId =
      this.getChampionId();


    if (
      championId === null
    ) {

      return 'Por definir';
    }


    const player =
      this.bracket?.participants.find(
        (item) => Number(item.id) === Number(championId)
      )
      ?? this.players.find(
        (item) =>
          Number(
            item.id
          ) ===
          Number(
            championId
          )
      );


    if (!player) {

      return (
        `Jugador ${championId}`
      );
    }


    return (
      `${player.first_name} `
      + `${player.last_name}`
    );
  }


  hasChampion():
    boolean {

    return (
      this.getChampionId() !==
      null
    );
  }


  // =====================================================
  // JUGADORES
  // =====================================================

  getLadderPlayerName(playerId: number): string {
    const participant = this.ladder?.participants.find(
      (item) => Number(item.player) === Number(playerId)
    );

    return participant
      ? `${participant.first_name} ${participant.last_name}`
      : `Jugador ${playerId}`;
  }

  getPlayerName(
    playerId: number | null,
    match: CategoryMatch
  ): string {

    if (
      playerId === null
    ) {

      if (
        match.round === 1
      ) {

        return 'BYE';
      }

      return 'Por definir';
    }


    const player =
      this.ladder?.participants.find(
        (item) => Number(item.player) === Number(playerId)
      )
      ?? this.bracket?.participants.find(
        (item) => Number(item.id) === Number(playerId)
      )
      ?? this.players.find(
        (item) =>
          Number(item.id) ===
          Number(playerId)
      );


    if (!player) {

      return (
        `Jugador ${playerId}`
      );
    }


    return (
      `${player.first_name} `
      + `${player.last_name}`
    );
  }


  // =====================================================
  // RESULTADOS
  // =====================================================

  getPlayer1Score(
    match: CategoryMatch
  ): string {

    if (
      !match.sets || match.sets.length === 0
    ) {
      return '';
    }


    return match.sets
      .map(
        (set) =>
          set.games_player1
      )
      .join(' ');
  }


  getPlayer2Score(
    match: CategoryMatch
  ): string {

    if (
      !match.sets || match.sets.length === 0
    ) {
      return '';
    }


    return match.sets
      .map(
        (set) =>
          set.games_player2
      )
      .join(' ');
  }


  isWinner(
    match: CategoryMatch,
    playerId: number | null
  ): boolean {

    if (
      playerId === null
      ||
      match.winner_player === null
    ) {

      return false;
    }


    return (
      Number(
        playerId
      ) ===
      Number(
        match.winner_player
      )
    );
  }


  // =====================================================
  // ESTADO
  // =====================================================

  getStatusLabel(
    status:
      CategoryMatch['status']
  ): string {

    switch (
      status
    ) {

      case 'PROGRAMADO':
        return 'Programado';

      case 'EN_JUEGO':
        return 'En juego';

      case 'FINALIZADO':
        return 'Finalizado';

      case 'CANCELADO':
        return 'Cancelado';

      default:
        return status;
    }
  }


  // =====================================================
  // PARTIDO DISPONIBLE
  // =====================================================

  canPlayMatch(
    match: CategoryMatch
  ): boolean {

    /*
     * El botón de resultado debe mantenerse disponible
     * aunque el partido ya esté FINALIZADO o haya sido
     * definido por WALKOVER/RETIRO, ya que el
     * Administrador/Organizador puede necesitar corregirlo.
     *
     * Solo se oculta cuando todavía falta un jugador
     * (BYE / ronda futura) o el partido está cancelado.
     */
    return (
      match.player1 !== null
      &&
      match.player2 !== null
      &&
      match.status !==
        'CANCELADO'
    );
  }


  // =====================================================
  // ELIMINAR CUADRO
  // =====================================================

  openDeleteBracketModal(): void {

    if (
      !this.isAdministrativeUser()
      || !this.bracket?.generated
      || !this.bracket.can_delete
    ) {
      return;
    }

    this.deleteBracketErrorMessage = '';
    this.showDeleteBracketModal = true;
  }


  closeDeleteBracketModal(): void {

    if (this.deletingBracket) {
      return;
    }

    this.showDeleteBracketModal = false;
    this.deleteBracketErrorMessage = '';
  }


  deleteBracket(): void {

    if (
      this.deletingBracket
      || !this.showDeleteBracketModal
      || this.competitionCategoryId === null
    ) {
      return;
    }

    this.deletingBracket = true;
    this.deleteBracketErrorMessage = '';

    this.competitionCategoryService
      .deleteBracket(
        this.competitionCategoryId
      )
      .subscribe({

        next: () => {

          this.deletingBracket = false;
          this.showDeleteBracketModal = false;
          this.deleteBracketErrorMessage = '';

          this.showSuccessMessage(
            'Cuadro eliminado correctamente.'
          );

          this.loadBracket();
        },

        error: (error) => {

          console.error(
            'Error al eliminar cuadro:',
            error
          );

          this.deleteBracketErrorMessage =
            this.getBackendErrorMessage(error);

          this.deletingBracket = false;
        },
      });
  }

  generateLadder(): void {
    if (
      this.competitionCategoryId === null
      || !this.isAdministrativeUser()
      || this.ladder?.generated
    ) {
      return;
    }

    const confirmed = window.confirm(
      'Se generará un partido todos contra todos entre los jugadores confirmados. ¿Deseas continuar?'
    );

    if (!confirmed) {
      return;
    }

    this.generating = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.competitionCategoryService
      .generateLadder(this.competitionCategoryId)
      .subscribe({
        next: (response) => {
          this.generating = false;
          this.showSuccessMessage(response.detail);
          this.loadLadder();
        },
        error: (error) => {
          this.errorMessage = this.getBackendErrorMessage(error);
          this.generating = false;
        },
      });
  }

  openDeleteLadderModal(): void {
    if (
      !this.isAdministrativeUser()
      || this.ladderMatchManagementMode
      || !this.ladder?.generated
      || !this.ladder.can_delete
    ) {
      return;
    }

    this.deleteLadderErrorMessage = '';
    this.showDeleteLadderModal = true;
  }

  closeDeleteLadderModal(): void {
    if (this.deletingLadder) {
      return;
    }

    this.showDeleteLadderModal = false;
    this.deleteLadderErrorMessage = '';
  }

  deleteLadder(): void {
    if (
      this.deletingLadder
      || !this.showDeleteLadderModal
      || this.competitionCategoryId === null
    ) {
      return;
    }

    this.deletingLadder = true;
    this.deleteLadderErrorMessage = '';

    this.competitionCategoryService
      .deleteLadder(this.competitionCategoryId)
      .subscribe({
        next: (response) => {
          this.deletingLadder = false;
          this.showDeleteLadderModal = false;
          this.deleteLadderErrorMessage = '';
          this.showSuccessMessage(response.detail);
          this.loadLadder();
        },
        error: (error) => {
          this.deleteLadderErrorMessage =
            this.getBackendErrorMessage(error);
          this.deletingLadder = false;
        },
      });
  }

  get ladderStandings(): Standing[] {
    return this.ladder?.standings ?? [];
  }

  get ladderFinishedCount(): number {
    return this.ladder?.matches.filter(
      (match) => match.status === 'FINALIZADO'
    ).length ?? 0;
  }

  get ladderScheduledCount(): number {
    return this.ladder?.matches.filter(
      (match) =>
        match.status !== 'FINALIZADO'
        && match.scheduled_date_time !== null
        && match.court !== null
    ).length ?? 0;
  }

  get ladderUnscheduledCount(): number {
    return this.ladder?.matches.filter(
      (match) =>
        match.status === 'PROGRAMADO'
        && match.scheduled_date_time === null
        && match.court === null
    ).length ?? 0;
  }

  get filteredLadderMatches(): Match[] {
    const search = this.matchSearch.trim().toLocaleLowerCase();
    return (this.ladder?.matches ?? []).filter((match) => {
      const names = `${match.player1 === null ? '' : this.getLadderPlayerName(match.player1)} ${
        match.player2 === null ? '' : this.getLadderPlayerName(match.player2)
      }`.toLocaleLowerCase();
      const matchesSearch = !search || names.includes(search);
      const matchesFilter = this.ladderMatchFilter === 'ALL'
        || (this.ladderMatchFilter === 'UNSCHEDULED'
          && match.status === 'PROGRAMADO'
          && match.scheduled_date_time === null
          && match.court === null)
        || (this.ladderMatchFilter === 'SCHEDULED'
          && match.status !== 'FINALIZADO'
          && match.scheduled_date_time !== null
          && match.court !== null)
        || (this.ladderMatchFilter === 'IN_PROGRESS'
          && match.status === 'EN_JUEGO')
        || (this.ladderMatchFilter === 'FINISHED'
          && match.status === 'FINALIZADO');
      return matchesSearch && matchesFilter;
    });
  }

  get playerUpcomingMatches(): Match[] {
    return this.getOwnMatches()
      .filter((match) =>
        match.status !== 'FINALIZADO'
        && match.scheduled_date_time !== null
        && match.court !== null
      )
      .sort((left, right) =>
        left.scheduled_date_time!.localeCompare(right.scheduled_date_time!)
      );
  }

  get playerFinishedMatches(): Match[] {
    return this.getOwnMatches()
      .filter((match) => match.status === 'FINALIZADO')
      .sort((left, right) =>
        (right.scheduled_date_time ?? '').localeCompare(left.scheduled_date_time ?? '')
      );
  }

  private getOwnMatches(): Match[] {
    if (this.currentPlayerId === null) {
      return [];
    }
    return (this.ladder?.matches ?? []).filter(
      (match) =>
        Number(match.player1) === Number(this.currentPlayerId)
        || Number(match.player2) === Number(this.currentPlayerId)
    );
  }

  getReadableScore(match: CategoryMatch): string {
    return formatMatchScore(match);
  }

  getOpponentName(match: Match): string {
    const opponentId = Number(match.player1) === Number(this.currentPlayerId)
      ? match.player2
      : match.player1;
    return opponentId === null ? 'Por definir' : this.getLadderPlayerName(opponentId);
  }

  getPlayerOutcome(match: Match): string {
    if (match.status !== 'FINALIZADO' || match.winner_player === null) {
      return '';
    }
    return Number(match.winner_player) === Number(this.currentPlayerId)
      ? 'Ganaste'
      : 'Perdiste';
  }

  goToLadderMatches(): void {
    if (this.competitionId === null || this.competitionCategoryId === null) {
      return;
    }
    this.router.navigate([
      '/competitions', this.competitionId,
      'categories', this.competitionCategoryId,
      'matches',
    ]);
  }


  // =====================================================
  // PROGRAMACIÓN
  // =====================================================

  canScheduleMatch(
    match: CategoryMatch
  ): boolean {

    return (
      this.isAdministrativeUser()
      &&
      match.player1 !== null
      &&
      match.player2 !== null
      &&
      match.status === 'PROGRAMADO'
    );
  }


  hasSchedule(
    match: CategoryMatch
  ): boolean {

    return (
      match.scheduled_date_time !== null
      ||
      match.court !== null
    );
  }


  getCourtName(
    courtId: number | null
  ): string {

    if (courtId === null) {
      return 'Cancha por definir';
    }

    return (
      this.courts.find(
        (court) =>
          court.id === courtId
      )?.name
      ??
      `Cancha ${courtId}`
    );
  }


  openScheduleModal(
    match: CategoryMatch
  ): void {

    if (!this.canScheduleMatch(match)) {
      return;
    }

    const localDateTime =
      this.toDateTimeLocalParts(
        match.scheduled_date_time
      );

    this.schedulingMatch = match;

    this.scheduleErrorMessage =
      this.courtsErrorMessage;

    this.scheduleForm.reset(
      {
        date: localDateTime.date,
        time: localDateTime.time,
        court: match.court,
      }
    );
  }


  closeScheduleModal(): void {

    if (this.savingSchedule) {
      return;
    }

    this.schedulingMatch = null;

    this.scheduleErrorMessage = '';

    this.scheduleForm.reset(
      {
        date: '',
        time: '',
        court: null,
      }
    );
  }


  isScheduleOutsideCompetitionPeriod():
    boolean {

    const selectedDate =
      this.scheduleForm.controls
        .date.value;

    if (
      !selectedDate
      ||
      !this.competition
    ) {
      return false;
    }

    return (
      selectedDate <
        this.competition.start_date
      ||
      selectedDate >
        this.competition.end_date
    );
  }


  isScheduleInPast(
    today: Date = new Date()
  ): boolean {

    const selectedDate =
      this.scheduleForm.controls
        .date.value;

    if (!selectedDate) {
      return false;
    }

    const year = today.getFullYear();

    const month = String(
      today.getMonth() + 1
    ).padStart(2, '0');

    const day = String(
      today.getDate()
    ).padStart(2, '0');

    return selectedDate <
      `${year}-${month}-${day}`;
  }


  saveSchedule(): void {

    if (
      !this.schedulingMatch
      ||
      this.savingSchedule
    ) {
      return;
    }

    if (this.scheduleForm.invalid) {

      this.scheduleForm
        .markAllAsTouched();

      return;
    }

    if (this.courtsErrorMessage) {

      this.scheduleErrorMessage =
        this.courtsErrorMessage;

      return;
    }

    const formValue =
      this.scheduleForm
        .getRawValue();

    this.savingSchedule = true;

    this.scheduleErrorMessage = '';

    this.matchService
      .updateMatch(
        this.schedulingMatch.id,
        {
          scheduled_date_time:
            `${formValue.date}T${formValue.time}`,
          court: formValue.court,
        }
      )
      .subscribe({

        next: () => {

          this.savingSchedule = false;

          this.closeScheduleModal();

          this.showSuccessMessage(
            'Programación guardada correctamente.'
          );

          this.refreshCurrentView();
        },

        error: (error) => {

          console.error(
            'Error al guardar programación:',
            error
          );

          this.scheduleErrorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.savingSchedule = false;
        },
      });
  }


  private toDateTimeLocalParts(
    value: string | null
  ): {
    date: string;
    time: string;
  } {

    if (!value) {
      return {
        date: '',
        time: '',
      };
    }

    const date = new Date(value);

    const year = date.getFullYear();
    const month = String(
      date.getMonth() + 1
    ).padStart(2, '0');
    const day = String(
      date.getDate()
    ).padStart(2, '0');
    const hours = String(
      date.getHours()
    ).padStart(2, '0');
    const minutes = String(
      date.getMinutes()
    ).padStart(2, '0');

    return {
      date: `${year}-${month}-${day}`,
      time: `${hours}:${minutes}`,
    };
  }


  // =====================================================
  // NAVEGACIÓN RESULTADO
  // =====================================================

  goToResult(
    match: CategoryMatch
  ): void {

    this.router.navigate(
      [
        '/matches',
        match.id,
        'result',
      ],
      {
        queryParams: {
          returnTo: 'bracket',
          competitionId:
            this.competitionId,
          competitionCategoryId:
            this.competitionCategoryId,
        },
      }
    );
  }


  goToEdit(
    match: CategoryMatch
  ): void {

    this.router.navigate([
      '/matches',
      match.id,
      'edit',
    ]);
  }

  refreshCurrentView(): void {
    if (this.competition?.type === 'ESCALERILLA') {
      this.loadLadder();
    } else {
      this.loadBracket();
    }
  }


  goBack(): void {

    if (
      this.ladderMatchManagementMode
      && this.competitionId !== null
      && this.competitionCategoryId !== null
    ) {
      this.router.navigate([
        '/competitions',
        this.competitionId,
        'categories',
        this.competitionCategoryId,
      ]);

      return;
    }

    if (!this.isAdministrativeUser()) {
      this.router.navigate([
        '/dashboard',
      ]);

      return;
    }

    if (
      this.competitionId ===
      null
    ) {

      this.router.navigate([
        '/competitions',
      ]);

      return;
    }


    this.router.navigate([
      '/competitions',
      this.competitionId,
      'categories',
    ]);
  }


  // =====================================================
  // ERRORES
  // =====================================================

  private getBackendErrorMessage(
    error: any
  ): string {

    const backendError =
      error?.error;


    if (!backendError) {

      return (
        'Ocurrió un error inesperado.'
      );
    }


    if (
      typeof backendError ===
      'string'
    ) {

      return backendError;
    }


    const messages:
      string[] = [];


    for (
      const key of
      Object.keys(
        backendError
      )
    ) {

      const value =
        backendError[key];


      if (
        Array.isArray(
          value
        )
      ) {

        messages.push(
          ...value
        );

      } else if (
        typeof value ===
        'string'
      ) {

        messages.push(
          value
        );
      }
    }


    return (
      messages.length > 0
        ? messages.join(' ')
        : 'Ocurrió un error inesperado.'
    );
  }


  // =====================================================
  // MENSAJE ÉXITO
  // =====================================================

  private showSuccessMessage(
    message: string
  ): void {

    this.successMessage =
      message;


    setTimeout(
      () => {

        this.successMessage =
          '';

      },
      4000
    );
  }
}
