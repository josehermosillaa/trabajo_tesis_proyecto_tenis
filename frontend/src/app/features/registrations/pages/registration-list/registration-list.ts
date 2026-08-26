import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import {
  RegistrationService,
  Category,
} from '../../services/registration';

import {
  Registration,
  Competition,
  CompetitionCategory,
} from '../../models/registration.model';

import { Player } from '../../../players/models/player.model';

@Component({
  selector: 'app-registration-list',
  imports: [CommonModule],
  templateUrl: './registration-list.html',
  styleUrl: './registration-list.scss',
})
export class RegistrationListComponent
  implements OnInit {

  private readonly registrationService =
    inject(RegistrationService);

  private readonly router =
    inject(Router);

  registrations: Registration[] = [];
  competitions: Competition[] = [];
  competitionCategories:
    CompetitionCategory[] = [];
  players: Player[] = [];
  categories: Category[] = [];

  loading = false;
  deletingId: number | null = null;

  errorMessage = '';
  successMessage = '';

  showDeleteModal = false;
  registrationToDelete:
    Registration | null = null;

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

  loadData(): void {

    this.loading = true;
    this.errorMessage = '';

    this.registrationService
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

    this.registrationService
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

    this.registrationService
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

    this.registrationService
      .getPlayers()
      .subscribe({

        next: (players) => {

          this.players = players;

          this.loadRegistrations();
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

  private loadRegistrations(): void {

    this.registrationService
      .getRegistrations()
      .subscribe({

        next: (registrations) => {

          this.registrations =
            registrations;

          this.loading = false;
        },

        error: (error) => {

          console.error(
            'Error al cargar inscripciones:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las inscripciones.';

          this.loading = false;
        },
      });
  }

  getPlayerName(
    playerId: number
  ): string {

    const player =
      this.players.find(
        (item) =>
          item.id === playerId
      );

    if (!player) {
      return `Jugador ${playerId}`;
    }

    return `${player.first_name} ${player.last_name}`;
  }

  getCompetitionCategory(
    competitionCategoryId: number
  ): CompetitionCategory | undefined {

    return this.competitionCategories.find(
      (item) =>
        item.id === competitionCategoryId
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

    const category =
      this.categories.find(
        (item) =>
          item.id ===
          competitionCategory.category
      );

    return (
      category?.name ??
      'Categoría no encontrada'
    );
  }

  goToCreate(): void {

    this.router.navigate([
      '/registrations/new',
    ]);
  }

  goToEdit(id: number): void {

    this.router.navigate([
      '/registrations',
      id,
      'edit',
    ]);
  }

  openDeleteModal(
    registration: Registration
  ): void {

    this.registrationToDelete =
      registration;

    this.showDeleteModal = true;

    this.errorMessage = '';
  }

  closeDeleteModal(): void {

    if (this.deletingId !== null) {
      return;
    }

    this.showDeleteModal = false;
    this.registrationToDelete = null;
  }

  confirmDelete(): void {

    if (!this.registrationToDelete) {
      return;
    }

    const registration =
      this.registrationToDelete;

    this.deletingId =
      registration.id;

    this.errorMessage = '';

    this.registrationService
      .deleteRegistration(
        registration.id
      )
      .subscribe({

        next: () => {

          this.registrations =
            this.registrations.filter(
              (item) =>
                item.id !==
                registration.id
            );

          this.deletingId = null;

          this.showDeleteModal = false;

          this.registrationToDelete =
            null;

          this.showSuccessMessage(
            'Inscripción eliminada correctamente.'
          );
        },

        error: (error) => {

          console.error(
            'Error al eliminar inscripción:',
            error
          );

          this.errorMessage =
            'No fue posible eliminar la inscripción.';

          this.deletingId = null;
        },
      });
  }

  private showSuccessMessage(
    message: string
  ): void {

    this.successMessage = message;

    setTimeout(() => {
      this.successMessage = '';
    }, 4000);
  }
}