import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

import {
  CommonModule,
} from '@angular/common';

import {
  Router,
} from '@angular/router';

import {
  MatchService,
  Court,
} from '../../services/match';

import {
  Match,
} from '../../models/match.model';

import {
  Competition,
} from '../../../registrations/models/registration.model';

import {
  CompetitionCategory,
} from '../../../competition-categories/models/competition-category.model';

import {
  Player,
} from '../../../players/models/player.model';


@Component({
  selector: 'app-match-list',

  imports: [
    CommonModule,
  ],

  templateUrl:
    './match-list.html',

  styleUrl:
    './match-list.scss',
})
export class MatchListComponent
  implements OnInit {

  private readonly matchService =
    inject(MatchService);

  private readonly router =
    inject(Router);


  matches:
    Match[] = [];

  competitions:
    Competition[] = [];

  competitionCategories:
    CompetitionCategory[] = [];

  players:
    Player[] = [];

  courts:
    Court[] = [];


  loading = false;

  deletingId:
    number | null = null;

  errorMessage = '';

  successMessage = '';

  showDeleteModal = false;

  matchToDelete:
    Match | null = null;


  ngOnInit(): void {

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

    this.loadData();
  }


  // =====================================================
  // CARGA DE DATOS
  // =====================================================

  loadData(): void {

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

          this.loadPlayers();
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

          this.loadMatches();
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


  private loadMatches(): void {

    this.matchService
      .getMatches()
      .subscribe({

        next: (matches) => {

          this.matches =
            matches;

          this.loading = false;
        },

        error: (error) => {

          console.error(
            'Error al cargar partidos:',
            error
          );

          this.errorMessage =
            'No fue posible cargar los partidos.';

          this.loading = false;
        },
      });
  }


  // =====================================================
  // HELPERS
  // =====================================================

  getPlayerName(
    playerId: number | null
  ): string {

    if (playerId === null) {
      return 'BYE';
    }

    const player =
      this.players.find(
        (item) =>
          item.id === playerId
      );

    if (!player) {
      return `Jugador ${playerId}`;
    }

    return (
      `${player.first_name} ${player.last_name}`
    );
  }


  getCompetitionCategory(
    competitionCategoryId: number
  ): CompetitionCategory | undefined {

    return this.competitionCategories.find(
      (item) =>
        item.id ===
        competitionCategoryId
    );
  }


  getCompetitionName(
    competitionCategoryId: number
  ): string {

    const competitionCategory =
      this.getCompetitionCategory(
        competitionCategoryId
      );

    if (!competitionCategory) {
      return 'Competencia no encontrada';
    }

    const competition =
      this.competitions.find(
        (item) =>
          item.id ===
          competitionCategory.competition
      );

    return (
      competition?.name ??
      'Competencia no encontrada'
    );
  }


  getCategoryName(
    competitionCategoryId: number
  ): string {

    const competitionCategory =
      this.getCompetitionCategory(
        competitionCategoryId
      );

    if (!competitionCategory) {
      return 'Categoría no encontrada';
    }

    return (
      `Categoría ${competitionCategory.category}`
    );
  }


  getCourtName(
    courtId: number | null
  ): string {

    if (courtId === null) {
      return 'Sin cancha';
    }

    const court =
      this.courts.find(
        (item) =>
          item.id === courtId
      );

    return (
      court?.name ??
      `Cancha ${courtId}`
    );
  }


  getStatusLabel(
    status: Match['status']
  ): string {

    switch (status) {

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
  // NAVEGACIÓN
  // =====================================================

  goToCreate(): void {

    this.router.navigate([
      '/matches/new',
    ]);
  }


  goToEdit(
    id: number
  ): void {

    this.router.navigate([
      '/matches',
      id,
      'edit',
    ]);
  }


  goToResult(
    id: number
  ): void {

    this.router.navigate([
      '/matches',
      id,
      'result',
    ]);
  }


  // =====================================================
  // ELIMINACIÓN
  // =====================================================

  openDeleteModal(
    match: Match
  ): void {

    this.matchToDelete =
      match;

    this.showDeleteModal =
      true;

    this.errorMessage = '';
  }


  closeDeleteModal(): void {

    if (
      this.deletingId !== null
    ) {
      return;
    }

    this.showDeleteModal =
      false;

    this.matchToDelete =
      null;
  }


  confirmDelete(): void {

    if (!this.matchToDelete) {
      return;
    }

    const match =
      this.matchToDelete;

    this.deletingId =
      match.id;

    this.errorMessage = '';

    this.matchService
      .deleteMatch(
        match.id
      )
      .subscribe({

        next: () => {

          this.matches =
            this.matches.filter(
              (item) =>
                item.id !==
                match.id
            );

          this.deletingId =
            null;

          this.showDeleteModal =
            false;

          this.matchToDelete =
            null;

          this.showSuccessMessage(
            'Partido eliminado correctamente.'
          );
        },

        error: (error) => {

          console.error(
            'Error al eliminar partido:',
            error
          );

          this.errorMessage =
            'No fue posible eliminar el partido.';

          this.deletingId =
            null;
        },
      });
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
}