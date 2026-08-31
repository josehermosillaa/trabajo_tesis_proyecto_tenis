import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { forkJoin } from 'rxjs';

import { TokenService } from '../../../../core/services/token';
import { CompetitionCategory } from '../../../competition-categories/models/competition-category.model';
import { Category, CompetitionCategoryService } from '../../../competition-categories/services/competition-category';
import { Competition } from '../../../competitions/models/competition.model';
import { CompetitionService } from '../../../competitions/services/competition';
import { Match, MatchSetSummary } from '../../../matches/models/match.model';
import { Court, MatchService } from '../../../matches/services/match';
import { Player } from '../../../players/models/player.model';
import { PlayerService } from '../../../players/services/player';
import { Registration } from '../../../registrations/models/registration.model';
import { RegistrationService } from '../../../registrations/services/registration';

interface PlayerMatchView {
  match: Match;
  rival: string;
  competition: string;
  category: string;
  court: string;
}

interface PlayerTournamentView {
  registration: Registration;
  competition: Competition;
  category: string;
}

interface AvailableTournamentView {
  competition: Competition;
  competitionCategory: CompetitionCategory;
  category: string;
}

interface PlayerResultView extends PlayerMatchView {
  result: 'Victoria' | 'Derrota';
  sets: string[];
}

@Component({
  selector: 'app-home',
  imports: [CommonModule],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class HomeComponent implements OnInit {
  private readonly tokenService = inject(TokenService);
  private readonly competitionService = inject(CompetitionService);
  private readonly registrationService = inject(RegistrationService);
  private readonly matchService = inject(MatchService);
  private readonly playerService = inject(PlayerService);
  private readonly competitionCategoryService = inject(CompetitionCategoryService);
  private readonly router = inject(Router);

  loading = false;
  registeringCategoryId: number | null = null;
  errorMessage = '';
  successMessage = '';
  currentPlayer: Player | null = null;
  nextMatch: PlayerMatchView | null = null;
  myTournaments: PlayerTournamentView[] = [];
  availableTournaments: AvailableTournamentView[] = [];
  previousResults: PlayerResultView[] = [];
  upcomingCompetitions: Competition[] = [];
  ongoingCompetitions: Competition[] = [];

  ngOnInit(): void {
    if (this.isPlayerUser()) {
      this.loadPlayerDashboard();
    } else if (this.isAdministrativeUser()) {
      this.loadAdministrativeDashboard();
    }
  }

  isPlayerUser(): boolean {
    return this.tokenService.getCurrentUserRole() === 'Jugador';
  }

  isAdministrativeUser(): boolean {
    return this.tokenService.isAdministrativeUser();
  }

  navigateTo(route: string): void {
    this.router.navigate([route]);
  }

  register(item: AvailableTournamentView): void {
    if (this.registeringCategoryId !== null) {
      return;
    }

    this.errorMessage = '';
    this.successMessage = '';
    this.registeringCategoryId = item.competitionCategory.id;
    this.registrationService.createRegistration({
      competition_category: item.competitionCategory.id,
    }).subscribe({
      next: () => {
        this.registeringCategoryId = null;
        this.successMessage = 'Inscripción realizada correctamente.';
        this.loadPlayerDashboard(false);
      },
      error: (error) => {
        console.error('Error al realizar inscripción:', error);
        this.errorMessage = this.getBackendErrorMessage(error);
        this.registeringCategoryId = null;
      },
    });
  }

  private loadPlayerDashboard(showLoading = true): void {
    if (showLoading) {
      this.loading = true;
    }
    this.errorMessage = '';

    forkJoin({
      players: this.playerService.getPlayers(),
      competitions: this.competitionService.getCompetitions(),
      registrations: this.registrationService.getRegistrations(),
      matches: this.matchService.getMatches(),
      competitionCategories: this.competitionCategoryService.getCompetitionCategories(),
      categories: this.competitionCategoryService.getCategories(),
      courts: this.matchService.getCourts(),
    }).subscribe({
      next: (data) => {
        const userId = this.tokenService.getCurrentUserId();
        this.currentPlayer = data.players.find(
          (player) => Number(player.user) === Number(userId)
        ) ?? null;

        if (!this.currentPlayer) {
          this.clearDashboard();
          this.errorMessage = 'No fue posible identificar el perfil del jugador autenticado.';
          this.loading = false;
          return;
        }

        this.buildDashboard(
          data.competitions,
          data.registrations,
          data.matches,
          data.competitionCategories,
          data.categories,
          data.players,
          data.courts
        );
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar el dashboard del jugador:', error);
        this.errorMessage = 'No fue posible cargar la información del dashboard.';
        this.loading = false;
      },
    });
  }

  private loadAdministrativeDashboard(): void {
    this.loading = true;
    this.errorMessage = '';

    this.competitionService.getCompetitions().subscribe({
      next: (competitions) => {
        this.upcomingCompetitions = competitions
          .filter((competition) =>
            competition.status === 'PENDIENTE' || competition.status === 'ABIERTA'
          )
          .sort((left, right) => left.start_date.localeCompare(right.start_date));
        this.ongoingCompetitions = competitions
          .filter((competition) => competition.status === 'EN_CURSO')
          .sort((left, right) => left.start_date.localeCompare(right.start_date));
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar el dashboard administrativo:', error);
        this.errorMessage = 'No fue posible cargar la información del dashboard.';
        this.loading = false;
      },
    });
  }

  private buildDashboard(
    competitions: Competition[],
    registrations: Registration[],
    matches: Match[],
    competitionCategories: CompetitionCategory[],
    categories: Category[],
    players: Player[],
    courts: Court[]
  ): void {
    const player = this.currentPlayer!;
    const competitionsById = new Map(competitions.map((item) => [item.id, item]));
    const competitionCategoriesById = new Map(
      competitionCategories.map((item) => [item.id, item])
    );
    const categoriesById = new Map(categories.map((item) => [item.id, item.name]));
    const playersById = new Map(players.map((item) => [item.id, item]));
    const courtsById = new Map(courts.map((item) => [item.id, item.name]));
    const playerMatches = matches.filter(
      (match) => match.player1 === player.id || match.player2 === player.id
    );
    const now = new Date();
    const upcomingMatches = playerMatches
      .filter((match) =>
        match.status === 'PROGRAMADO' &&
        match.scheduled_date_time !== null &&
        new Date(match.scheduled_date_time).getTime() > now.getTime()
      )
      .sort((left, right) =>
        new Date(left.scheduled_date_time!).getTime() -
        new Date(right.scheduled_date_time!).getTime()
      );

    this.nextMatch = upcomingMatches.length > 0
      ? this.toMatchView(
          upcomingMatches[0], player, competitionCategoriesById, competitionsById,
          categoriesById, playersById, courtsById
        )
      : null;

    const validRegistrations = registrations.filter((registration) =>
      registration.player === player.id &&
      (registration.status === 'PENDIENTE' || registration.status === 'CONFIRMADA')
    );
    this.myTournaments = validRegistrations
      .map((registration) => {
        const competitionCategory = competitionCategoriesById.get(registration.competition_category);
        const competition = competitionCategory
          ? competitionsById.get(competitionCategory.competition)
          : undefined;
        return competition && competitionCategory
          ? {
              registration,
              competition,
              category: categoriesById.get(competitionCategory.category) ?? 'Sin categoría',
            }
          : null;
      })
      .filter((item): item is PlayerTournamentView => item !== null)
      .sort((left, right) => left.competition.start_date.localeCompare(right.competition.start_date));

    const registeredCompetitionIds = new Set(
      validRegistrations
        .map((registration) => competitionCategoriesById.get(registration.competition_category))
        .filter((item): item is CompetitionCategory => item !== undefined)
        .map((item) => item.competition)
    );
    const today = this.toLocalDateString(now);
    this.availableTournaments = competitionCategories
      .filter((competitionCategory) => {
        const competition = competitionsById.get(competitionCategory.competition);
        return competition?.status === 'ABIERTA' &&
          competition.registration_deadline >= today &&
          competitionCategory.category === player.category &&
          competitionCategory.available_slots > 0 &&
          !registeredCompetitionIds.has(competitionCategory.competition);
      })
      .map((competitionCategory) => ({
        competition: competitionsById.get(competitionCategory.competition)!,
        competitionCategory,
        category: categoriesById.get(competitionCategory.category) ?? 'Sin categoría',
      }))
      .sort((left, right) => left.competition.start_date.localeCompare(right.competition.start_date));

    this.previousResults = playerMatches
      .filter((match) => match.status === 'FINALIZADO')
      .sort((left, right) => this.matchTimestamp(right) - this.matchTimestamp(left))
      .map((match) => {
        const view = this.toMatchView(
          match, player, competitionCategoriesById, competitionsById,
          categoriesById, playersById, courtsById
        );
        return {
          ...view,
          result: match.winner_player === player.id ? 'Victoria' : 'Derrota',
          sets: (match.sets ?? []).map((set) => this.formatSet(set, match, player)),
        };
      });
  }

  private toMatchView(
    match: Match,
    currentPlayer: Player,
    competitionCategoriesById: Map<number, CompetitionCategory>,
    competitionsById: Map<number, Competition>,
    categoriesById: Map<number, string>,
    playersById: Map<number, Player>,
    courtsById: Map<number, string>
  ): PlayerMatchView {
    const competitionCategory = competitionCategoriesById.get(match.competition_category);
    const competition = competitionCategory
      ? competitionsById.get(competitionCategory.competition)
      : undefined;
    const rivalId = match.player1 === currentPlayer.id ? match.player2 : match.player1;
    const rival = rivalId === null ? undefined : playersById.get(rivalId);
    return {
      match,
      rival: rival ? `${rival.first_name} ${rival.last_name}` : 'Por definir',
      competition: competition?.name ?? 'Competencia no disponible',
      category: competitionCategory
        ? categoriesById.get(competitionCategory.category) ?? 'Sin categoría'
        : 'Sin categoría',
      court: match.court === null ? 'Por definir' : courtsById.get(match.court) ?? 'Por definir',
    };
  }

  private formatSet(set: MatchSetSummary, match: Match, player: Player): string {
    return match.player1 === player.id
      ? `${set.games_player1}-${set.games_player2}`
      : `${set.games_player2}-${set.games_player1}`;
  }

  private matchTimestamp(match: Match): number {
    return match.scheduled_date_time ? new Date(match.scheduled_date_time).getTime() : 0;
  }

  private toLocalDateString(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private clearDashboard(): void {
    this.nextMatch = null;
    this.myTournaments = [];
    this.availableTournaments = [];
    this.previousResults = [];
  }

  private getBackendErrorMessage(error: any): string {
    const backendError = error?.error;
    if (!backendError) {
      return 'No fue posible realizar la inscripción.';
    }
    if (typeof backendError === 'string') {
      return backendError;
    }
    const messages = Object.values(backendError).flatMap((value) =>
      Array.isArray(value) ? value : typeof value === 'string' ? [value] : []
    );
    return messages.length > 0 ? messages.join(' ') : 'No fue posible realizar la inscripción.';
  }
}
