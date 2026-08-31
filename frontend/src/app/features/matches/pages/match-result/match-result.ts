import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

import {
  CommonModule,
} from '@angular/common';

import {
  FormsModule,
} from '@angular/forms';

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
} from '../../services/match';

import {
  Match,
} from '../../models/match.model';

import {
  MatchSet,
  CreateMatchSetRequest,
  UpdateMatchSetRequest,
} from '../../models/match-set.model';

import {
  Player,
} from '../../../players/models/player.model';
import { TokenService } from '../../../../core/services/token';


@Component({
  selector: 'app-match-result',

  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
  ],

  templateUrl:
    './match-result.html',

  styleUrl:
    './match-result.scss',
})
export class MatchResultComponent
  implements OnInit {

  private readonly fb =
    inject(FormBuilder);

  private readonly matchService =
    inject(MatchService);

  private readonly route =
    inject(ActivatedRoute);

  private readonly router =
    inject(Router);

  private readonly tokenService =
    inject(TokenService);

  isAdministrativeUser(): boolean {
    return this.tokenService.isAdministrativeUser();
  }


  matchId:
    number | null = null;

  private returnCompetitionId:
    number | null = null;

  private returnCompetitionCategoryId:
    number | null = null;

  match:
    Match | null = null;

  matchSets:
    MatchSet[] = [];

  players:
    Player[] = [];


  loading = false;

  saving = false;

  deletingSetId:
    number | null = null;

  editingSetId:
    number | null = null;

  /*
   * Set seleccionado para confirmar
   * su eliminación mediante modal.
   */
  setPendingDelete:
    MatchSet | null = null;
      /*
   * Tipo de resolución pendiente.
   */
  resolutionPending:
    'WALKOVER'
    | 'RETIREMENT'
    | null = null;

  /*
   * Jugador seleccionado como ganador
   * en WO o Retiro.
   */
  resolutionWinnerId:
    number | null = null;

  resolvingMatch = false;

  /*
   * Marcador parcial del set actual cuando
   * el partido finaliza por retiro.
   */
  retirementGamesPlayer1 = 0;

  retirementGamesPlayer2 = 0;

  errorMessage = '';

  successMessage = '';


  readonly resultForm =
    this.fb.nonNullable.group({

      set_number: [
        1,
        [
          Validators.required,
          Validators.min(1),
          Validators.max(3),
        ],
      ],

      games_player1: [
        0,
        [
          Validators.required,
          Validators.min(0),
        ],
      ],

      games_player2: [
        0,
        [
          Validators.required,
          Validators.min(0),
        ],
      ],

      is_super_tie_break: [
        false,
      ],

    });


  ngOnInit(): void {

    const id =
      this.route.snapshot
        .paramMap
        .get('id');

    if (!id) {

      this.errorMessage =
        'No se especificó el partido.';

      return;
    }

    this.matchId =
      Number(id);

    this.loadReturnContext();

    this.loadData();
  }


  private loadReturnContext(): void {

    const queryParams =
      this.route.snapshot.queryParamMap;

    if (
      queryParams.get('returnTo') !==
      'bracket'
    ) {
      return;
    }

    const competitionId = Number(
      queryParams.get('competitionId')
    );

    const competitionCategoryId = Number(
      queryParams.get(
        'competitionCategoryId'
      )
    );

    if (
      !Number.isInteger(competitionId)
      ||
      competitionId <= 0
      ||
      !Number.isInteger(
        competitionCategoryId
      )
      ||
      competitionCategoryId <= 0
    ) {
      return;
    }

    this.returnCompetitionId =
      competitionId;

    this.returnCompetitionCategoryId =
      competitionCategoryId;
  }


  // =====================================================
  // CARGA
  // =====================================================

  loadData(): void {

    if (
      this.matchId === null
    ) {
      return;
    }

    this.loading = true;

    this.errorMessage = '';

    this.matchService
      .getPlayers()
      .subscribe({

        next: (players) => {

          this.players =
            players;

          this.loadMatch();
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


  private loadMatch(): void {

    if (
      this.matchId === null
    ) {
      return;
    }

    this.matchService
      .getMatch(
        this.matchId
      )
      .subscribe({

        next: (match) => {

          this.match =
            match;

          this.loadMatchSets();
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


  private loadMatchSets(): void {

    if (
      this.matchId === null
    ) {
      return;
    }

    this.matchService
      .getMatchSets()
      .subscribe({

        next: (sets) => {

          this.matchSets =
            sets
              .filter(
                (set) =>
                  set.match ===
                  this.matchId
              )
              .sort(
                (a, b) =>
                  a.set_number -
                  b.set_number
              );

          this.prepareNextSet();

          this.loading = false;
        },

        error: (error) => {

          console.error(
            'Error al cargar sets:',
            error
          );

          this.errorMessage =
            'No fue posible cargar los sets del partido.';

          this.loading = false;
        },
      });
  }


  // =====================================================
  // PREPARAR SIGUIENTE SET
  // =====================================================

  private prepareNextSet(): void {

    if (
      this.editingSetId !== null
    ) {
      return;
    }

    const nextSetNumber =
      this.matchSets.length + 1;

    if (
      nextSetNumber > 3
    ) {
      return;
    }

    const isSuperTieBreak =
      nextSetNumber === 3;

    this.resultForm.patchValue(
      {
        set_number:
          nextSetNumber,

        games_player1:
          0,

        games_player2:
          0,

        is_super_tie_break:
          isSuperTieBreak,
      },
      {
        emitEvent: false,
      }
    );
  }


  // =====================================================
  // HELPERS
  // =====================================================

  getPlayerName(
    playerId: number | null
  ): string {

    if (
      playerId === null
    ) {
      return 'BYE';
    }

    const player =
      this.players.find(
        (item) =>
          item.id === playerId
      );

    if (!player) {

      return (
        `Jugador ${playerId}`
      );
    }

    return (
      `${player.first_name} ${player.last_name}`
    );
  }


  getWinnerName(): string {

    if (
      !this.match
      ||
      this.match.winner_player === null
    ) {
      return '';
    }

    return this.getPlayerName(
      this.match.winner_player
    );
  }


  getStatusLabel(): string {

    if (!this.match) {
      return '';
    }

    switch (
      this.match.status
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
        return this.match.status;
    }
  }


  getSetWinner(
    matchSet: MatchSet
  ): string {

    if (!this.match) {
      return '';
    }

    if (
      matchSet.is_incomplete
    ) {
      return 'Retiro';
    }

    if (
      matchSet.games_player1 >
      matchSet.games_player2
    ) {

      return this.getPlayerName(
        this.match.player1
      );
    }

    return this.getPlayerName(
      this.match.player2
    );
  }


canRegisterSet(): boolean {

  if (!this.match) {
    return false;
  }

  if (
    this.match.is_walkover
    ||
    this.match.resolution_type === 'WALKOVER'
    ||
    this.match.resolution_type === 'RETIREMENT'
    ||
    this.match.player2 === null
    ||
    this.match.status === 'CANCELADO'
  ) {
    return false;
  }

  if (
    this.match.status === 'FINALIZADO'
  ) {
    return false;
  }

  return (
    this.matchSets.length < 3
  );
}


  // =====================================================
  // CREAR / ACTUALIZAR SET
  // =====================================================

  onSubmit(): void {

    this.errorMessage = '';

    if (
      this.resultForm.invalid
    ) {

      this.resultForm
        .markAllAsTouched();

      return;
    }

    if (!this.match) {
      return;
    }

    const formValue =
      this.resultForm
        .getRawValue();

    if (
      formValue.games_player1 ===
      formValue.games_player2
    ) {

      this.errorMessage =
        'El set no puede terminar empatado.';

      return;
    }

    if (
      this.editingSetId !== null
    ) {

      this.updateSet();

      return;
    }

    this.createSet();
  }


  private createSet(): void {

    if (!this.match) {
      return;
    }

    this.saving = true;

    this.errorMessage = '';

    const formValue =
      this.resultForm
        .getRawValue();

    const data:
      CreateMatchSetRequest = {

      match:
        this.match.id,

      set_number:
        formValue.set_number,

      games_player1:
        formValue.games_player1,

      games_player2:
        formValue.games_player2,

      is_super_tie_break:
        formValue.is_super_tie_break,
    };


    this.matchService
      .createMatchSet(
        data
      )
      .subscribe({

        next: () => {

          this.saving =
            false;

          this.showSuccessMessage(
            'Set registrado correctamente.'
          );

          /*
           * Recargamos tanto Match
           * como MatchSet porque el backend
           * puede haber actualizado:
           *
           * status
           * winner_player
           */
          this.loadMatch();
        },

        error: (error) => {

          console.error(
            'Error al registrar set:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.saving =
            false;
        },
      });
  }


  private updateSet(): void {

    if (
      this.editingSetId === null
    ) {
      return;
    }

    this.saving = true;

    this.errorMessage = '';

    const formValue =
      this.resultForm
        .getRawValue();

    const data:
      UpdateMatchSetRequest = {

      set_number:
        formValue.set_number,

      games_player1:
        formValue.games_player1,

      games_player2:
        formValue.games_player2,

      is_super_tie_break:
        formValue.is_super_tie_break,
    };


    this.matchService
      .updateMatchSet(
        this.editingSetId,
        data
      )
      .subscribe({

        next: () => {

          this.editingSetId =
            null;

          this.saving =
            false;

          this.showSuccessMessage(
            'Set actualizado correctamente.'
          );

          this.loadMatch();
        },

        error: (error) => {

          console.error(
            'Error al actualizar set:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.saving =
            false;
        },
      });
  }


  // =====================================================
  // EDITAR SET
  // =====================================================

  editSet(
    matchSet: MatchSet
  ): void {

    this.errorMessage = '';

    this.editingSetId =
      matchSet.id;

    this.resultForm.patchValue(
      {
        set_number:
          matchSet.set_number,

        games_player1:
          matchSet.games_player1,

        games_player2:
          matchSet.games_player2,

        is_super_tie_break:
          matchSet.is_super_tie_break,
      },
      {
        emitEvent: false,
      }
    );
  }


  cancelEdit(): void {

    this.editingSetId =
      null;

    this.errorMessage = '';

    this.prepareNextSet();
  }


  // =====================================================
  // MODAL ELIMINAR SET
  // =====================================================

  openDeleteSetModal(
    matchSet: MatchSet
  ): void {

    if (
      this.deletingSetId !== null
    ) {
      return;
    }

    this.errorMessage = '';

    this.setPendingDelete =
      matchSet;
  }


  closeDeleteSetModal(): void {

    if (
      this.deletingSetId !== null
    ) {
      return;
    }

    this.setPendingDelete =
      null;
  }


  confirmDeleteSet(): void {

    if (
      this.setPendingDelete === null
      ||
      this.deletingSetId !== null
    ) {
      return;
    }

    const matchSet =
      this.setPendingDelete;

    this.deletingSetId =
      matchSet.id;

    this.errorMessage = '';

    this.matchService
      .deleteMatchSet(
        matchSet.id
      )
      .subscribe({

        next: () => {

          this.deletingSetId =
            null;

          this.editingSetId =
            null;

          this.setPendingDelete =
            null;

          this.showSuccessMessage(
            'Set eliminado correctamente.'
          );

          /*
           * El backend recalcula
           * automáticamente:
           *
           * status
           * winner_player
           *
           * y, cuando corresponde,
           * el clasificado de la
           * siguiente ronda.
           */
          this.loadMatch();
        },

        error: (error) => {

          console.error(
            'Error al eliminar set:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.deletingSetId =
            null;

          this.setPendingDelete =
            null;
        },
      });
  }

    // =====================================================
  // WALKOVER / RETIRO
  // =====================================================

canRegisterWalkover(): boolean {
  if (!this.match) {
    return false;
  }

  if (
    this.match.player2 === null
    ||
    this.match.status === 'CANCELADO'
  ) {
    return false;
  }

  /*
   * Si ya es WALKOVER,
   * permitimos editar el ganador.
   */
  if (
    this.match.resolution_type === 'WALKOVER'
    ||
    this.match.is_walkover
  ) {
    return true;
  }

  /*
   * Un retiro no se transforma
   * directamente en WO.
   * Primero debe restablecerse.
   */
  if (
    this.match.resolution_type === 'RETIREMENT'
  ) {
    return false;
  }

  /*
   * Un WO solamente puede registrarse
   * si todavía no existen sets.
   */
  return this.matchSets.length === 0;
}


canRegisterRetirement(): boolean {
  if (!this.match) {
    return false;
  }

  if (
    this.match.player2 === null
    ||
    this.match.status === 'CANCELADO'
  ) {
    return false;
  }

  /*
   * Si ya es RETIREMENT,
   * permitimos editar el ganador.
   */
  if (
    this.match.resolution_type === 'RETIREMENT'
  ) {
    return true;
  }

  /*
   * Un WO no se transforma
   * directamente en retiro.
   */
  if (
    this.match.resolution_type === 'WALKOVER'
    ||
    this.match.is_walkover
  ) {
    return false;
  }

  /*
   * El retiro puede producirse en cualquier
   * momento después de iniciado el partido,
   * incluso durante el primer set.
   */
  return true;
}


openResolutionModal(
  type: 'WALKOVER' | 'RETIREMENT'
): void {

  if (!this.match) {
    return;
  }

  this.resolutionPending = type;

  /*
   * Si estamos editando una resolución,
   * dejamos seleccionado al ganador actual.
   */
  this.resolutionWinnerId =
    this.match.winner_player ?? null;

  if (
    type === 'RETIREMENT'
    &&
    this.match.resolution_type !== 'RETIREMENT'
  ) {
    this.retirementGamesPlayer1 = 0;
    this.retirementGamesPlayer2 = 0;
  }
}


  closeResolutionModal(): void {

    if (this.resolvingMatch) {
      return;
    }

    this.resolutionPending =
      null;

    this.resolutionWinnerId =
      null;

    this.retirementGamesPlayer1 =
      0;

    this.retirementGamesPlayer2 =
      0;
  }


  selectResolutionWinner(
    playerId: number
  ): void {

    if (this.resolvingMatch) {
      return;
    }

    this.resolutionWinnerId =
      playerId;
  }


  confirmResolution(): void {

    if (
      !this.match
      ||
      this.resolutionPending ===
        null
      ||
      this.resolutionWinnerId ===
        null
      ||
      this.resolvingMatch
    ) {
      return;
    }

    this.resolvingMatch = true;

    this.errorMessage = '';

    const resolution =
      this.resolutionPending;

    /*
     * WALKOVER y edición de un RETIRO ya existente
     * no necesitan crear un marcador parcial.
     */
    if (
      resolution === 'WALKOVER'
      ||
      this.match.resolution_type ===
        'RETIREMENT'
    ) {

      this.sendResolutionRequest(
        resolution
      );

      return;
    }

    /*
     * RETIRO NUEVO:
     *
     * Si existe un marcador parcial distinto de
     * 0-0, lo guardamos como MatchSet incompleto
     * antes de finalizar el partido por retiro.
     *
     * Si está 0-0, no es necesario crear un set
     * incompleto: el retiro puede registrarse
     * igualmente.
     */
    const hasPartialScore =
      (
        this.retirementGamesPlayer1 > 0
        ||
        this.retirementGamesPlayer2 > 0
      );

    if (!hasPartialScore) {

      this.sendResolutionRequest(
        'RETIREMENT'
      );

      return;
    }

    const nextSetNumber =
      this.matchSets.length + 1;

    if (
      nextSetNumber > 3
    ) {

      this.errorMessage =
        'No es posible registrar otro set en este partido.';

      this.resolvingMatch =
        false;

      return;
    }

    const partialSet:
      CreateMatchSetRequest = {

      match:
        this.match.id,

      set_number:
        nextSetNumber,

      games_player1:
        this.retirementGamesPlayer1,

      games_player2:
        this.retirementGamesPlayer2,

      is_super_tie_break:
        nextSetNumber === 3,

      is_incomplete:
        true,
    };

    this.matchService
      .createMatchSet(
        partialSet
      )
      .subscribe({

        next: () => {

          this.sendResolutionRequest(
            'RETIREMENT'
          );
        },

        error: (error) => {

          console.error(
            'Error al registrar marcador parcial:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.resolvingMatch =
            false;
        },
      });
  }


  private sendResolutionRequest(
    resolution:
      'WALKOVER'
      | 'RETIREMENT'
  ): void {

    if (
      !this.match
      ||
      this.resolutionWinnerId === null
    ) {

      this.resolvingMatch =
        false;

      return;
    }

    const data = {
      winner_player:
        this.resolutionWinnerId,
    };

    const request =
      resolution === 'WALKOVER'
        ? this.matchService.walkover(
            this.match.id,
            data
          )
        : this.matchService.retirement(
            this.match.id,
            data
          );

    request.subscribe({

      next: () => {

        this.resolvingMatch =
          false;

        this.resolutionPending =
          null;

        this.resolutionWinnerId =
          null;

        this.retirementGamesPlayer1 =
          0;

        this.retirementGamesPlayer2 =
          0;

        this.editingSetId =
          null;

        this.showSuccessMessage(
          resolution === 'WALKOVER'
            ? (
              'Walkover guardado correctamente.'
            )
            : (
              'Retiro guardado correctamente.'
            )
        );

        this.loadMatch();
      },

      error: (error) => {

        console.error(
          'Error al resolver partido:',
          error
        );

        this.errorMessage =
          this.getBackendErrorMessage(
            error
          );

        this.resolvingMatch =
          false;
      },
    });
  }


  resetResolution(): void {

    if (
      !this.match
      ||
      this.resolvingMatch
    ) {
      return;
    }

    this.resolvingMatch = true;

    this.errorMessage = '';

    this.matchService
      .resetResolution(
        this.match.id
      )
      .subscribe({

        next: () => {

          this.resolvingMatch =
            false;

          this.resolutionPending =
            null;

          this.resolutionWinnerId =
            null;

          this.editingSetId =
            null;

          this.showSuccessMessage(
            'La resolución especial fue restablecida correctamente.'
          );

          this.loadMatch();
        },

        error: (error) => {

          console.error(
            'Error al restablecer resolución:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.resolvingMatch =
            false;
        },
      });
  }


  getResolutionLabel(): string {

    if (!this.match) {
      return '';
    }

    switch (
      this.match.resolution_type
    ) {

      case 'WALKOVER':
        return 'Walkover';

      case 'RETIREMENT':
        return 'Retiro';

      default:
        return 'Normal';
    }
  }

  // =====================================================
  // MENSAJES
  // =====================================================

  private showSuccessMessage(
    message: string
  ): void {

    this.successMessage =
      message;

    setTimeout(() => {

      this.successMessage = '';

    }, 4000);
  }


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
  // NAVEGACIÓN
  // =====================================================

  goBack(): void {

    if (
      this.returnCompetitionId !== null
      &&
      this.returnCompetitionCategoryId !== null
    ) {

      this.router.navigate([
        '/competitions',
        this.returnCompetitionId,
        'categories',
        this.returnCompetitionCategoryId,
      ]);

      return;
    }

    this.router.navigate([
      '/matches',
    ]);
  }
}
