import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';

import { Organizer } from '../../models/organizer.model';
import { OrganizerService } from '../../services/organizer';

@Component({
  selector: 'app-organizer-list',
  imports: [CommonModule],
  templateUrl: './organizer-list.html',
  styleUrl: './organizer-list.scss',
})
export class OrganizerListComponent implements OnInit {
  private readonly organizerService = inject(OrganizerService);
  private readonly router = inject(Router);

  organizers: Organizer[] = [];
  loading = false;
  changingState = false;
  errorMessage = '';
  successMessage = '';
  searchTerm = '';
  organizerToChange: Organizer | null = null;

  get filteredOrganizers(): Organizer[] {
    const term = this.searchTerm.trim().toLocaleLowerCase();

    return this.organizers.filter((organizer) => {
      if (!term) return true;

      const searchable = [
        organizer.first_name,
        organizer.last_name,
        organizer.username,
        organizer.email,
      ].join(' ').toLocaleLowerCase();

      return searchable.includes(term);
    });
  }

  getOrganizerName(organizer: Organizer): string {
    return `${organizer.first_name} ${organizer.last_name}`.trim() || '—';
  }

  ngOnInit(): void {
    const navigationMessage = history.state?.successMessage;
    if (typeof navigationMessage === 'string') {
      this.successMessage = navigationMessage;
      history.replaceState({}, document.title);
    }
    this.loadOrganizers();
  }

  loadOrganizers(): void {
    this.loading = true;
    this.errorMessage = '';
    this.organizerService.getOrganizers().subscribe({
      next: (organizers) => {
        this.organizers = organizers;
        this.loading = false;
      },
      error: (error) => {
        this.errorMessage = this.getBackendError(error);
        this.loading = false;
      },
    });
  }

  goToCreate(): void {
    this.router.navigate(['/organizers/new']);
  }

  goToEdit(id: number): void {
    this.router.navigate(['/organizers', id, 'edit']);
  }

  openStateModal(organizer: Organizer): void {
    this.organizerToChange = organizer;
    this.errorMessage = '';
  }

  closeStateModal(): void {
    if (!this.changingState) {
      this.organizerToChange = null;
    }
  }

  confirmStateChange(): void {
    if (!this.organizerToChange || this.changingState) {
      return;
    }
    const organizer = this.organizerToChange;
    const active = !organizer.is_active;
    this.changingState = true;
    this.errorMessage = '';
    this.organizerService.setOrganizerActive(organizer.id, active).subscribe({
      next: () => {
        this.changingState = false;
        this.organizerToChange = null;
        this.successMessage = active
          ? 'Organizador activado correctamente.'
          : 'Organizador desactivado correctamente.';
        this.loadOrganizers();
      },
      error: (error) => {
        this.errorMessage = this.getBackendError(error);
        this.changingState = false;
      },
    });
  }

  private getBackendError(error: unknown): string {
    const body = (error as { error?: unknown })?.error;
    if (typeof body === 'string') return body;
    if (body && typeof body === 'object') {
      const detail = (body as { detail?: unknown }).detail;
      if (typeof detail === 'string') return detail;
    }
    return 'No fue posible completar la operación.';
  }
}
