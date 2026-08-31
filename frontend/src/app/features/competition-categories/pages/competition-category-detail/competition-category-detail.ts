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
} from '../../models/competition-category.model';

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


interface BracketRound {
  round: number;
  name: string;
  matches: BracketMatch[];
}


@Component({
  selector: 'app-competition-category-detail',

  imports: [
    CommonModule,
    ReactiveFormsModule,
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

  isAdministrativeUser(): boolean {
    return this.tokenService.isAdministrativeUser();
  }


  competitionId:
    number | null = null;

  competitionCategoryId:
    number | null = null;


  bracket:
    BracketResponse | null = null;

  rounds:
    BracketRound[] = [];

  players:
    Player[] = [];

  courts:
    Court[] = [];

  competition:
    Competition | null = null;

  schedulingMatch:
    BracketMatch | null = null;

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

  errorMessage = '';

  successMessage = '';


  ngOnInit(): void {

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


    if (this.isAdministrativeUser()) {
      this.loadCourts();
    }

    this.loadPlayers();
  }


  // =====================================================
  // CARGA
  // =====================================================

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
      this.players.find(
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

  getPlayerName(
    playerId: number | null,
    match: BracketMatch
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
      this.players.find(
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
    match: BracketMatch
  ): string {

    if (
      match.sets.length === 0
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
    match: BracketMatch
  ): string {

    if (
      match.sets.length === 0
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
    match: BracketMatch,
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
      BracketMatch['status']
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
    match: BracketMatch
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
  // PROGRAMACIÓN
  // =====================================================

  canScheduleMatch(
    match: BracketMatch
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
    match: BracketMatch
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
    match: BracketMatch
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

          this.loadBracket();
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
    match: BracketMatch
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
    match: BracketMatch
  ): void {

    this.router.navigate([
      '/matches',
      match.id,
      'edit',
    ]);
  }


  goBack(): void {

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
