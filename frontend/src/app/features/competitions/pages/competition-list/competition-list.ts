import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CompetitionService } from '../../services/competition';
import { Competition } from '../../models/competition.model';
import { Router } from '@angular/router';
import { TokenService } from '../../../../core/services/token';

@Component({
  selector: 'app-competition-list',
  imports: [CommonModule],
  templateUrl: './competition-list.html',
  styleUrl: './competition-list.scss',
})
export class CompetitionListComponent implements OnInit {
  private readonly competitionService = inject(CompetitionService);
  private readonly router = inject(Router);
  private readonly tokenService = inject(TokenService);

  isAdministrativeUser(): boolean {
    return this.tokenService.isAdministrativeUser();
  }

  competitions: Competition[] = [];

  loading = false;
  deletingId: number | null = null;
  errorMessage = '';
  successMessage = '';

  // Control del modal
  showDeleteModal = false;
  competitionToDelete: Competition | null = null;

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

    this.loadCompetitions();
  }

  private showSuccessMessage(
    message: string
  ): void {
    this.successMessage = message;

    setTimeout(() => {
      this.successMessage = '';
    }, 4000);
  }

  loadCompetitions(): void {
    this.loading = true;
    this.errorMessage = '';

    this.competitionService.getCompetitions().subscribe({
      next: (competitions) => {
        this.competitions = competitions;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar competencias:', error);

        this.errorMessage =
          'No fue posible cargar las competencias.';

        this.loading = false;
      },
    });
  }

  goToCreate(): void {
    this.router.navigate(['/competitions/new']);
  }

  goToEdit(id: number): void {
    this.router.navigate(['/competitions', id, 'edit']);
  }

  openDeleteModal(competition: Competition): void {
    this.competitionToDelete = competition;
    this.showDeleteModal = true;
    this.errorMessage = '';
  }

  closeDeleteModal(): void {
    if (this.deletingId !== null) {
      return;
    }

    this.showDeleteModal = false;
    this.competitionToDelete = null;
  }

  confirmDelete(): void {
    if (!this.competitionToDelete) {
      return;
    }

    const competition = this.competitionToDelete;

    this.deletingId = competition.id;
    this.errorMessage = '';

    this.competitionService
      .deleteCompetition(competition.id)
      .subscribe({
        next: () => {
        this.competitions = this.competitions.filter(
          (item) => item.id !== competition.id
        );

        this.deletingId = null;
        this.showDeleteModal = false;
        this.competitionToDelete = null;

        this.showSuccessMessage(
          'Competencia eliminada correctamente.'
        );
        },

        error: (error) => {
          console.error(
            'Error al eliminar competencia:',
            error
          );

          this.errorMessage =
            'No fue posible eliminar la competencia.';

          this.deletingId = null;
        },
      });
  }
  goToCategories(id: number): void {
  this.router.navigate([
    '/competitions',
    id,
    'categories',
  ]);
}
}
