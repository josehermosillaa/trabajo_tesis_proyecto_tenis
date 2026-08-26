import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

import { CommonModule } from '@angular/common';

import {
  ActivatedRoute,
  Router,
} from '@angular/router';

import {
  Category,
  CompetitionCategoryService,
} from '../../services/competition-category';

import {
  CompetitionCategory,
} from '../../models/competition-category.model';

import { Player } from '../../../players/models/player.model';

import { PlayerService } from '../../../players/services/player';

import { RegistrationService } from '../../../registrations/services/registration';

import { TokenService } from '../../../../core/services/token';

import { CompetitionService } from '../../../competitions/services/competition';

import { Competition } from '../../../competitions/models/competition.model';


@Component({
  selector: 'app-competition-category-list',

  imports: [
    CommonModule,
  ],

  templateUrl:
    './competition-category-list.html',

  styleUrl:
    './competition-category-list.scss',
})
export class CompetitionCategoryListComponent
  implements OnInit {

  private readonly competitionCategoryService =
    inject(CompetitionCategoryService);

  private readonly playerService =
    inject(PlayerService);

  private readonly registrationService =
    inject(RegistrationService);

  private readonly tokenService =
    inject(TokenService);

  private readonly competitionService =
    inject(CompetitionService);

  private readonly route =
    inject(ActivatedRoute);

  private readonly router =
    inject(Router);


  competitionId:
    number | null = null;

  competition:
    Competition | null = null;

  competitionCategories:
    CompetitionCategory[] = [];

  categories:
    Category[] = [];

  players:
    Player[] = [];

  currentPlayer:
    Player | null = null;

  loading = false;

  registeringCategoryId:
    number | null = null;

  errorMessage = '';

  successMessage = '';


  ngOnInit(): void {

    /*
     * Mensaje recibido al volver,
     * por ejemplo después de inscribir
     * un jugador desde RegistrationForm.
     */
    const navigationMessage =
      history.state?.successMessage;

    if (navigationMessage) {

      this.showSuccessMessage(
        navigationMessage
      );

      history.replaceState(
        {},
        document.title
      );
    }


    const id =
      this.route.snapshot
        .paramMap
        .get('id');

    if (!id) {

      this.errorMessage =
        'No se especificó la competencia.';

      return;
    }

    this.competitionId =
      Number(id);

    /*
     * Cargamos por separado:
     *
     * 1. Datos generales del torneo.
     * 2. Categorías, cupos e inscritos.
     */
    this.loadCompetition();

    this.loadData();
  }


  // =====================================================
  // INFORMACIÓN GENERAL DE LA COMPETENCIA
  // =====================================================

  private loadCompetition(): void {

    if (
      this.competitionId === null
    ) {
      return;
    }

    this.competitionService
      .getCompetition(
        this.competitionId
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

          this.errorMessage =
            'No fue posible cargar la información de la competencia.';
        },
      });
  }


  // =====================================================
  // CATEGORÍAS DE LA COMPETENCIA
  // =====================================================

  loadData(): void {

    if (
      this.competitionId === null
    ) {
      return;
    }

    this.loading = true;

    this.errorMessage = '';

    this.competitionCategoryService
      .getCompetitionCategories()
      .subscribe({

        next: (
          competitionCategories
        ) => {

          this.competitionCategories =
            competitionCategories.filter(
              (item) =>
                item.competition ===
                this.competitionId
            );

          this.loadCategories();
        },

        error: (error) => {

          console.error(
            'Error al cargar categorías de competencia:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las categorías.';

          this.loading = false;
        },
      });
  }


  private loadCategories(): void {

    this.competitionCategoryService
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

    this.playerService
      .getPlayers()
      .subscribe({

        next: (players) => {

          this.players =
            players;

          this.resolveCurrentPlayer();

          this.loading = false;
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


  // =====================================================
  // USUARIO / PLAYER ACTUAL
  // =====================================================

private resolveCurrentPlayer(): void {

  const userId =
    this.tokenService
      .getCurrentUserId();

  console.log(
    'User ID del JWT:',
    userId
  );

  console.log(
    'Players recibidos:',
    this.players
  );

  if (userId === null) {

    this.currentPlayer = null;

    return;
  }

  this.currentPlayer =
    this.players.find(
      (player) =>
        Number(player.user) ===
        Number(userId)
    ) ?? null;

  console.log(
    'Player actual encontrado:',
    this.currentPlayer
  );
}


  // =====================================================
  // HELPERS
  // =====================================================

  getCategoryName(
    categoryId: number
  ): string {

    const category =
      this.categories.find(
        (item) =>
          item.id === categoryId
      );

    return (
      category?.name ??
      `Categoría ${categoryId}`
    );
  }


  /*
   * Si el usuario autenticado tiene
   * un Player asociado, consideramos
   * que estamos frente al rol Jugador.
   */
  isPlayerUser(): boolean {

    return (
      this.currentPlayer !== null
    );
  }


  isPlayerCategory(
    competitionCategory:
      CompetitionCategory
  ): boolean {

    if (!this.currentPlayer) {
      return false;
    }

    return (
      this.currentPlayer.category ===
      competitionCategory.category
    );
  }


  isCurrentPlayerRegistered(
    competitionCategory:
      CompetitionCategory
  ): boolean {

    if (!this.currentPlayer) {
      return false;
    }

    return (
      competitionCategory
        .registered_players
        .some(
          (player) =>
            player.id ===
            this.currentPlayer!.id
        )
    );
  }


  getCurrentRegistrationStatus(
    competitionCategory:
      CompetitionCategory
  ): string {

    if (!this.currentPlayer) {
      return '';
    }

    const registeredPlayer =
      competitionCategory
        .registered_players
        .find(
          (player) =>
            player.id ===
            this.currentPlayer!.id
        );

    if (!registeredPlayer) {
      return '';
    }

    switch (
      registeredPlayer.status
    ) {

      case 'CONFIRMADA':
        return 'Confirmada';

      case 'CANCELADA':
        return 'Cancelada';

      default:
        return 'Pendiente';
    }
  }


  // =====================================================
  // AUTOINSCRIPCIÓN JUGADOR
  // =====================================================

  registerMyself(
    competitionCategory:
      CompetitionCategory
  ): void {

    if (
      !this.currentPlayer
      || this.registeringCategoryId !== null
    ) {
      return;
    }

    this.errorMessage = '';

    this.successMessage = '';

    this.registeringCategoryId =
      competitionCategory.id;

    this.registrationService
      .createRegistration({
        competition_category:
          competitionCategory.id,
      })
      .subscribe({

        next: () => {

          this.registeringCategoryId =
            null;

          this.showSuccessMessage(
            'Inscripción realizada correctamente.'
          );

          /*
           * Recargamos para actualizar:
           *
           * - cupos usados
           * - cupos disponibles
           * - lista de inscritos
           * - estado del jugador
           */
          this.loadData();
        },

        error: (error) => {

          console.error(
            'Error al realizar inscripción:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(
              error
            );

          this.registeringCategoryId =
            null;
        },
      });
  }


  // =====================================================
  // INSCRIPCIÓN ADMIN / ORGANIZADOR
  // =====================================================

  registerPlayer(
    competitionCategory:
      CompetitionCategory
  ): void {

    this.router.navigate(
      ['/registrations/new'],
      {
        queryParams: {

          competition:
            this.competitionId,

          competitionCategory:
            competitionCategory.id,
        },
      }
    );
  }


  // =====================================================
  // EDICIÓN / NAVEGACIÓN
  // =====================================================

  editCompetition(): void {

    if (
      this.competitionId === null
    ) {
      return;
    }

    this.router.navigate([
      '/competitions',
      this.competitionId,
      'edit',
    ]);
  }


  goBack(): void {

    this.router.navigate([
      '/competitions',
    ]);
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
        'No fue posible realizar la inscripción.'
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
        : 'No fue posible realizar la inscripción.'
    );
  }
}