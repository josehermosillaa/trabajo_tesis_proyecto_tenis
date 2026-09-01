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
  MatchService,
  Court,
} from '../../services/match';

import {
  Competition,
} from '../../../registrations/models/registration.model';

import {
  CompetitionCategory,
} from '../../../competition-categories/models/competition-category.model';

import {
  Category,
} from '../../../competition-categories/services/competition-category';

import {
  Player,
} from '../../../players/models/player.model';

import {
  CreateMatchRequest,
  Match,
  MatchStatus,
  UpdateMatchRequest,
} from '../../models/match.model';
import { TokenService } from '../../../../core/services/token';
import { TemporalInputComponent } from '../../../../shared/date-time/temporal-input.component';


@Component({
  selector: 'app-match-form',

  imports: [
    CommonModule,
    ReactiveFormsModule,
    TemporalInputComponent,
  ],

  templateUrl:
    './match-form.html',

  styleUrl:
    './match-form.scss',
})
export class MatchFormComponent
  implements OnInit {

  private readonly fb =
    inject(FormBuilder);

  private readonly matchService =
    inject(MatchService);

  private readonly router =
    inject(Router);

  private readonly route =
    inject(ActivatedRoute);

  private readonly tokenService =
    inject(TokenService);

  isAdministrativeUser(): boolean {
    return this.tokenService.isAdministrativeUser();
  }


  loading = false;

  errorMessage = '';

  isEditMode = false;

  matchId:
    number | null = null;

  generatedBracketMatch:
    Match | null = null;

  generatedBracketCompetitionId:
    number | null = null;


  competitions:
    Competition[] = [];

  competitionCategories:
    CompetitionCategory[] = [];

  filteredCompetitionCategories:
    CompetitionCategory[] = [];

  categories:
    Category[] = [];

  players:
    Player[] = [];

  filteredPlayers:
    Player[] = [];

  courts:
    Court[] = [];


  readonly matchForm =
    this.fb.nonNullable.group({

      competition: [
        0,
        Validators.required,
      ],

      competition_category: [
        0,
        Validators.required,
      ],

      court: [
        null as number | null,
      ],

      player1: [
        0,
        Validators.required,
      ],

      player2: [
        null as number | null,
      ],

      scheduled_date_time: [
        '',
      ],

      status:
        this.fb.nonNullable.control<
          MatchStatus
        >(
          'PROGRAMADO',
          Validators.required
        ),

      round: [
        null as number | null,
      ],

      is_walkover: [
        false,
      ],

      winner_player: [
        null as number | null,
      ],

    });


  ngOnInit(): void {

    const id =
      this.route.snapshot
        .paramMap
        .get('id');

    if (id) {

      this.isEditMode = true;

      this.matchId =
        Number(id);
    }

    this.loadBaseData();


    this.matchForm
      .controls.competition
      .valueChanges
      .subscribe(
        (competitionId) => {

          this.onCompetitionChange(
            competitionId
          );
        }
      );


    this.matchForm
      .controls.competition_category
      .valueChanges
      .subscribe(
        (competitionCategoryId) => {

          this.onCompetitionCategoryChange(
            competitionCategoryId
          );
        }
      );


    this.matchForm
      .controls.player1
      .valueChanges
      .subscribe(
        () => {

          this.validateSelectedPlayers();
        }
      );


    this.matchForm
      .controls.player2
      .valueChanges
      .subscribe(
        () => {

          this.validateSelectedPlayers();
        }
      );


    this.matchForm
      .controls.is_walkover
      .valueChanges
      .subscribe(
        (isWalkover) => {

          this.onWalkoverChange(
            isWalkover
          );
        }
      );
  }


  // =====================================================
  // CARGA BASE
  // =====================================================

  private loadBaseData(): void {

    this.loading = true;

    this.errorMessage = '';

    this.matchService
      .getCompetitions()
      .subscribe({

        next: (competitions) => {

          this.competitions =
            competitions;

          this.loadCompetitionCategories();
        },

        error: (error) => {

          console.error(
            'Error al cargar competencias:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las competencias.';

          this.loading = false;
        },
      });
  }


  private loadCompetitionCategories(): void {

    this.matchService
      .getCompetitionCategories()
      .subscribe({

        next: (competitionCategories) => {

          this.competitionCategories =
            competitionCategories;

          this.loadCategories();
        },

        error: (error) => {

          console.error(
            'Error al cargar categorías de competencia:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las categorías de competencia.';

          this.loading = false;
        },
      });
  }


  private loadCategories(): void {

    this.matchService
      .getCategories()
      .subscribe({

        next: (categories) => {

          this.categories =
            categories;

          this.loadPlayers();
        },

        error: (error) => {

          console.error(
            'Error al cargar categorías:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las categorías.';

          this.loading = false;
        },
      });
  }


  private loadPlayers(): void {

    this.matchService
      .getPlayers()
      .subscribe({

        next: (players) => {

          this.players =
            players;

          this.loadCourts();
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

    this.matchService
      .getCourts()
      .subscribe({

        next: (courts) => {

          this.courts =
            courts;

          if (
            this.isEditMode
            && this.matchId !== null
          ) {

            this.loadMatch(
              this.matchId
            );

          } else {

            this.applyQueryParams();

            this.loading = false;
          }
        },

        error: (error) => {

          console.error(
            'Error al cargar canchas:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las canchas.';

          this.loading = false;
        },
      });
  }


  // =====================================================
  // CARGAR PARTIDO EN EDICIÓN
  // =====================================================

  private loadMatch(
    id: number
  ): void {

    this.matchService
      .getMatch(id)
      .subscribe({

        next: (match) => {

          const competitionCategory =
            this.competitionCategories.find(
              (item) =>
                item.id ===
                match.competition_category
            );

          if (!competitionCategory) {

            this.errorMessage =
              'No fue posible identificar la categoría del partido.';

            this.loading = false;

            return;
          }

          const competition =
            this.competitions.find(
              (item) =>
                item.id ===
                competitionCategory.competition
            );

          if (
            competition?.type ===
              'ELIMINACION_DIRECTA'
            && match.bracket_position !== null
          ) {
            this.generatedBracketMatch = match;
            this.generatedBracketCompetitionId =
              competitionCategory.competition;
            this.loading = false;
            return;
          }

          this.filteredCompetitionCategories =
            this.competitionCategories.filter(
              (item) =>
                item.competition ===
                competitionCategory.competition
            );

          this.loadConfirmedPlayers(
            competitionCategory
          );

          this.matchForm.patchValue(
            {
              competition:
                competitionCategory.competition,

              competition_category:
                match.competition_category,

              court:
                match.court,

              player1:
                match.player1 ?? 0,

              player2:
                match.player2,

              scheduled_date_time:
                this.toDateTimeLocal(
                  match.scheduled_date_time
                ),

              status:
                match.status,

              round:
                match.round,

              is_walkover:
                match.is_walkover,

              winner_player:
                match.winner_player,
            },
            {
              emitEvent: false,
            }
          );

          this.loading = false;
        },

        error: (error) => {

          console.error(
            'Error al cargar partido:',
            error
          );

          this.errorMessage =
            'No fue posible cargar el partido.';

          this.loading = false;
        },
      });
  }


  // =====================================================
  // QUERY PARAMS
  // =====================================================

  private applyQueryParams(): void {

    const competition =
      this.route.snapshot
        .queryParamMap
        .get('competition');

    const competitionCategory =
      this.route.snapshot
        .queryParamMap
        .get('competitionCategory');

    if (!competition) {
      return;
    }

    const competitionId =
      Number(competition);

    this.filteredCompetitionCategories =
      this.competitionCategories.filter(
        (item) =>
          item.competition ===
          competitionId
      );

    this.matchForm.patchValue(
      {
        competition:
          competitionId,
      },
      {
        emitEvent: false,
      }
    );

    if (!competitionCategory) {
      return;
    }

    const competitionCategoryId =
      Number(
        competitionCategory
      );

    const category =
      this.competitionCategories.find(
        (item) =>
          item.id ===
          competitionCategoryId
      );

    if (!category) {
      return;
    }

    this.loadConfirmedPlayers(
      category
    );

    this.matchForm.patchValue(
      {
        competition_category:
          competitionCategoryId,

        player1:
          0,

        player2:
          null,

        round:
          this.getCompetitionType(
            category.competition
          ) === 'ELIMINACION_DIRECTA'
            ? 1
            : null,
      },
      {
        emitEvent: false,
      }
    );
  }


  // =====================================================
  // CAMBIO DE COMPETENCIA
  // =====================================================

  onCompetitionChange(
    competitionId: number
  ): void {

    this.filteredCompetitionCategories =
      this.competitionCategories.filter(
        (item) =>
          item.competition ===
          competitionId
      );

    this.filteredPlayers = [];

    this.matchForm.patchValue(
      {
        competition_category:
          0,

        player1:
          0,

        player2:
          null,

        winner_player:
          null,

        round:
          this.getCompetitionType(
            competitionId
          ) === 'ELIMINACION_DIRECTA'
            ? 1
            : null,
      },
      {
        emitEvent: false,
      }
    );
  }


  // =====================================================
  // CAMBIO DE CATEGORÍA
  // =====================================================

  onCompetitionCategoryChange(
    competitionCategoryId: number
  ): void {

    const competitionCategory =
      this.competitionCategories.find(
        (item) =>
          item.id ===
          competitionCategoryId
      );

    if (!competitionCategory) {

      this.filteredPlayers = [];

      this.matchForm.patchValue(
        {
          player1:
            0,

          player2:
            null,

          winner_player:
            null,
        },
        {
          emitEvent: false,
        }
      );

      return;
    }

    this.loadConfirmedPlayers(
      competitionCategory
    );

    const competitionType =
      this.getCompetitionType(
        competitionCategory.competition
      );

    this.matchForm.patchValue(
      {
        player1:
          0,

        player2:
          null,

        winner_player:
          null,

        round:
          competitionType ===
          'ELIMINACION_DIRECTA'
            ? 1
            : null,
      },
      {
        emitEvent: false,
      }
    );
  }


  // =====================================================
  // JUGADORES CONFIRMADOS
  // =====================================================

  private loadConfirmedPlayers(
    competitionCategory:
      CompetitionCategory
  ): void {

    const confirmedPlayerIds =
      competitionCategory
        .registered_players
        .filter(
          (registeredPlayer) =>
            registeredPlayer.status ===
            'CONFIRMADA'
        )
        .map(
          (registeredPlayer) =>
            registeredPlayer.id
        );

    this.filteredPlayers =
      this.players.filter(
        (player) =>
          confirmedPlayerIds.includes(
            player.id
          )
      );
  }


  // =====================================================
  // WALKOVER
  // =====================================================

  private onWalkoverChange(
    isWalkover: boolean
  ): void {

    if (!isWalkover) {

      this.matchForm.patchValue(
        {
          winner_player:
            null,
        },
        {
          emitEvent: false,
        }
      );

      return;
    }

    /*
     * En WO debe haber Player 2.
     * El ganador se selecciona manualmente.
     */
    if (
      this.matchForm
        .controls.player2
        .value === null
    ) {

      this.errorMessage =
        'Un walkover requiere dos jugadores.';

      this.matchForm.patchValue(
        {
          is_walkover:
            false,
        },
        {
          emitEvent: false,
        }
      );
    }
  }


  // =====================================================
  // VALIDACIÓN DE JUGADORES
  // =====================================================

  private validateSelectedPlayers(): void {

    const player1 =
      this.matchForm
        .controls.player1
        .value;

    const player2 =
      this.matchForm
        .controls.player2
        .value;

    if (
      player1 > 0
      && player2 !== null
      && player1 === player2
    ) {

      this.errorMessage =
        'Un jugador no puede enfrentarse contra sí mismo.';

      this.matchForm.patchValue(
        {
          player2:
            null,
        },
        {
          emitEvent: false,
        }
      );
    }
  }


  // =====================================================
  // HELPERS
  // =====================================================

  getCompetitionType(
    competitionId: number
  ): Competition['type'] | null {

    const competition =
      this.competitions.find(
        (item) =>
          item.id ===
          competitionId
      );

    return (
      competition?.type ??
      null
    );
  }


  isEliminationDirect(): boolean {

    const competitionId =
      this.matchForm
        .controls.competition
        .value;

    return (
      this.getCompetitionType(
        competitionId
      ) ===
      'ELIMINACION_DIRECTA'
    );
  }


  getCategoryName(
    categoryId: number
  ): string {

    const category =
      this.categories.find(
        (item) =>
          item.id ===
          categoryId
      );

    return (
      category?.name ??
      `Categoría ${categoryId}`
    );
  }


  getPlayerName(
    player: Player
  ): string {

    return (
      `${player.first_name} ${player.last_name}`
    );
  }


  getWinnerCandidates():
    Player[] {

    const player1Id =
      this.matchForm
        .controls.player1
        .value;

    const player2Id =
      this.matchForm
        .controls.player2
        .value;

    return this.filteredPlayers.filter(
      (player) =>
        player.id === player1Id
        ||
        player.id === player2Id
    );
  }


  private toDateTimeLocal(
    value: string | null
  ): string {

    if (!value) {
      return '';
    }

    const date =
      new Date(value);

    const year =
      date.getFullYear();

    const month =
      String(
        date.getMonth() + 1
      ).padStart(
        2,
        '0'
      );

    const day =
      String(
        date.getDate()
      ).padStart(
        2,
        '0'
      );

    const hours =
      String(
        date.getHours()
      ).padStart(
        2,
        '0'
      );

    const minutes =
      String(
        date.getMinutes()
      ).padStart(
        2,
        '0'
      );

    return (
      `${year}-${month}-${day}T`
      + `${hours}:${minutes}`
    );
  }


  // =====================================================
  // SUBMIT
  // =====================================================

  onSubmit(): void {

    if (this.generatedBracketMatch) {
      return;
    }

    if (!this.isAdministrativeUser()) {
      return;
    }

    this.errorMessage = '';

    if (
      this.matchForm.invalid
    ) {

      this.matchForm
        .markAllAsTouched();

      return;
    }

    const formValue =
      this.matchForm
        .getRawValue();


    if (
      formValue.competition <= 0
    ) {

      this.errorMessage =
        'Debes seleccionar una competencia.';

      return;
    }


    if (
      formValue.competition_category <= 0
    ) {

      this.errorMessage =
        'Debes seleccionar una categoría.';

      return;
    }


    if (
      formValue.player1 <= 0
    ) {

      this.errorMessage =
        'Debes seleccionar el jugador 1.';

      return;
    }


    if (
      formValue.player2 !== null
      &&
      formValue.player1 ===
      formValue.player2
    ) {

      this.errorMessage =
        'Un jugador no puede enfrentarse contra sí mismo.';

      return;
    }


    if (
      this.isEliminationDirect()
      &&
      (
        formValue.round === null
        ||
        formValue.round < 1
      )
    ) {

      this.errorMessage =
        'La ronda es obligatoria para eliminación directa.';

      return;
    }


    if (
      formValue.is_walkover
      &&
      formValue.player2 === null
    ) {

      this.errorMessage =
        'Un walkover requiere dos jugadores.';

      return;
    }


    if (
      formValue.is_walkover
      &&
      formValue.winner_player === null
    ) {

      this.errorMessage =
        'Debes seleccionar el ganador del walkover.';

      return;
    }


    if (
      this.isEditMode
      &&
      this.matchId !== null
    ) {

      this.updateMatch();

      return;
    }

    this.createMatch();
  }


  goToBracket(): void {

    if (
      !this.generatedBracketMatch
      || this.generatedBracketCompetitionId === null
    ) {
      return;
    }

    this.router.navigate([
      '/competitions',
      this.generatedBracketCompetitionId,
      'categories',
      this.generatedBracketMatch.competition_category,
    ]);
  }


  // =====================================================
  // CREAR
  // =====================================================

  private createMatch(): void {

    this.loading = true;

    this.errorMessage = '';

    const formValue =
      this.matchForm
        .getRawValue();

    const match:
      CreateMatchRequest = {

      competition_category:
        formValue.competition_category,

      court:
        formValue.court,

      player1:
        formValue.player1,

      player2:
        formValue.player2,

      scheduled_date_time:
        formValue.scheduled_date_time
          ? formValue.scheduled_date_time
          : null,

      status:
        formValue.is_walkover
          ? 'FINALIZADO'
          : formValue.status,

      round:
        this.isEliminationDirect()
          ? formValue.round
          : null,

      is_walkover:
        formValue.is_walkover,

      winner_player:
        formValue.is_walkover
          ? formValue.winner_player
          : null,
    };


    this.matchService
      .createMatch(
        match
      )
      .subscribe({

        next: () => {

          this.router.navigate(
            ['/matches'],
            {
              state: {
                successMessage:
                  'Partido creado correctamente.',
              },
            }
          );
        },

        error: (error) => {

          console.error(
            'Error al crear partido:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.loading = false;
        },
      });
  }


  // =====================================================
  // ACTUALIZAR
  // =====================================================

  private updateMatch(): void {

    this.loading = true;

    this.errorMessage = '';

    const formValue =
      this.matchForm
        .getRawValue();

    const match:
      UpdateMatchRequest = {

      competition_category:
        formValue.competition_category,

      court:
        formValue.court,

      player1:
        formValue.player1,

      player2:
        formValue.player2,

      scheduled_date_time:
        formValue.scheduled_date_time
          ? formValue.scheduled_date_time
          : null,

      status:
        formValue.is_walkover
          ? 'FINALIZADO'
          : formValue.status,

      round:
        this.isEliminationDirect()
          ? formValue.round
          : null,

      is_walkover:
        formValue.is_walkover,

      winner_player:
        formValue.is_walkover
          ? formValue.winner_player
          : null,
    };


    this.matchService
      .updateMatch(
        this.matchId!,
        match
      )
      .subscribe({

        next: () => {

          this.router.navigate(
            ['/matches'],
            {
              state: {
                successMessage:
                  'Partido actualizado correctamente.',
              },
            }
          );
        },

        error: (error) => {

          console.error(
            'Error al actualizar partido:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.loading = false;
        },
      });
  }


  // =====================================================
  // ERRORES BACKEND
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
      Object.keys(backendError)
    ) {

      const value =
        backendError[key];

      if (
        Array.isArray(value)
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
  // CANCELAR
  // =====================================================

  cancel(): void {

    this.router.navigate([
      '/matches',
    ]);
  }
}
