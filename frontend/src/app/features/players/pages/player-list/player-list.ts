import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import {
  Category,
  PlayerService,
} from '../../services/player';

import { Player } from '../../models/player.model';

@Component({
  selector: 'app-player-list',
  imports: [CommonModule],
  templateUrl: './player-list.html',
  styleUrl: './player-list.scss',
})
export class PlayerListComponent implements OnInit {

  private readonly playerService =
    inject(PlayerService);

  private readonly router =
    inject(Router);

  players: Player[] = [];
  categories: Category[] = [];

  loading = false;
  deletingId: number | null = null;

  errorMessage = '';
  successMessage = '';

  // Modal eliminación
  showDeleteModal = false;
  playerToDelete: Player | null = null;

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

    this.playerService
      .getCategories()
      .subscribe({

        next: (categories) => {

          this.categories = categories;

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

          this.players = players;

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

  goToCreate(): void {

    this.router.navigate([
      '/players/new',
    ]);
  }

  goToEdit(id: number): void {

    this.router.navigate([
      '/players',
      id,
      'edit',
    ]);
  }

  openDeleteModal(
    player: Player
  ): void {

    this.playerToDelete = player;
    this.showDeleteModal = true;
    this.errorMessage = '';
  }

  closeDeleteModal(): void {

    if (this.deletingId !== null) {
      return;
    }

    this.showDeleteModal = false;
    this.playerToDelete = null;
  }

  confirmDelete(): void {

    if (!this.playerToDelete) {
      return;
    }

    const player =
      this.playerToDelete;

    this.deletingId = player.id;
    this.errorMessage = '';

    this.playerService
      .deletePlayer(player.id)
      .subscribe({

        next: () => {

          this.players =
            this.players.filter(
              (item) =>
                item.id !== player.id
            );

          this.deletingId = null;

          this.showDeleteModal = false;
          this.playerToDelete = null;

          this.showSuccessMessage(
            'Jugador eliminado correctamente.'
          );
        },

        error: (error) => {

          console.error(
            'Error al eliminar jugador:',
            error
          );

          this.errorMessage =
            'No fue posible eliminar el jugador.';

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