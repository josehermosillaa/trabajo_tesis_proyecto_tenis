import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

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
  RegistrationService,
  Category,
} from '../../services/registration';

import {
  Competition,
  Registration,
  CreateRegistrationRequest,
  UpdateRegistrationRequest,
} from '../../models/registration.model';

import {
  CompetitionCategory,
} from '../../../competition-categories/models/competition-category.model';

import { Player } from '../../../players/models/player.model';
import { TokenService } from '../../../../core/services/token';




@Component({
  selector: 'app-registration-form',

  imports: [
    ReactiveFormsModule,
  ],

  templateUrl:
    './registration-form.html',

  styleUrl:
    './registration-form.scss',
})
export class RegistrationFormComponent
  implements OnInit {

  private readonly fb =
    inject(FormBuilder);

  private readonly registrationService =
    inject(RegistrationService);

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

  registrationId:
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

  registrations:
    Registration[] = [];

  playerSearchResults:
    Player[] = [];

  showPlayerResults = false;

  readonly playerSearchControl =
    this.fb.nonNullable.control('');


  readonly registrationForm =
    this.fb.nonNullable.group({

      competition: [
        0,
        Validators.required,
      ],

      competition_category: [
        0,
        Validators.required,
      ],

      player: [
        0,
        Validators.required,
      ],

      status:
        this.fb.nonNullable.control<
          'PENDIENTE'
          | 'CONFIRMADA'
          | 'CANCELADA'
        >(
          'CONFIRMADA',
          Validators.required
        ),

      seed: [
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

      this.registrationId =
        Number(id);
    }

    /*
     * Cargamos los datos después de determinar
     * si estamos en modo edición.
     */
    this.loadBaseData();


    /*
     * Cambio de competencia.
     */
    this.registrationForm
      .controls.competition
      .valueChanges
      .subscribe(
        (competitionId) => {

          this.onCompetitionChange(
            competitionId
          );
        }
      );


    /*
     * Cambio de categoría.
     */
    this.registrationForm
      .controls.competition_category
      .valueChanges
      .subscribe(
        (competitionCategoryId) => {

          this.onCompetitionCategoryChange(
            competitionCategoryId
          );
        }
      );
  }


  // =====================================================
  // CARGA DE DATOS
  // =====================================================

  private loadBaseData(): void {

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

          this.players =
            players;

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

          this.finishBaseDataLoad();
        },

        error: (error) => {

          console.error(
            'Error al cargar inscripciones:',
            error
          );

          this.registrations = [];

          this.finishBaseDataLoad();
        },
      });
  }


  private finishBaseDataLoad(): void {

    if (
      this.isEditMode
      && this.registrationId !== null
    ) {

      this.loadRegistration(
        this.registrationId
      );

      return;
    }

    this.applyQueryParams();

    this.loading = false;
  }


  // =====================================================
  // CARGAR INSCRIPCIÓN EN EDICIÓN
  // =====================================================

  private loadRegistration(
    id: number
  ): void {

    this.registrationService
      .getRegistration(id)
      .subscribe({

        next: (registration) => {

          const competitionCategory =
            this.competitionCategories.find(
              (item) =>
                item.id ===
                registration.competition_category
            );

          if (!competitionCategory) {

            this.errorMessage =
              'No fue posible identificar la categoría de la inscripción.';

            this.loading = false;

            return;
          }

          /*
           * Categorías disponibles
           * de la competencia actual.
           */
          this.filteredCompetitionCategories =
            this.competitionCategories.filter(
              (item) =>
                item.competition ===
                competitionCategory.competition
            );

          /*
           * En edición NO ocultamos inscritos,
           * porque necesitamos que el jugador
           * de la inscripción actual siga
           * apareciendo en el selector.
           */
          this.filteredPlayers =
            this.sortPlayersForCategory(
              competitionCategory
            );

          this.registrationForm.patchValue(
            {
              competition:
                competitionCategory.competition,

              competition_category:
                registration.competition_category,

              player:
                registration.player,

              status:
                registration.status,

              seed:
                registration.seed,
            },
            {
              emitEvent: false,
            }
          );

          const selectedPlayer =
            this.getSelectedPlayer();

          this.playerSearchControl.setValue(
            selectedPlayer
              ? this.getPlayerName(selectedPlayer)
              : '',
            { emitEvent: false }
          );

          this.loading = false;
        },

        error: (error) => {

          console.error(
            'Error al cargar inscripción:',
            error
          );

          this.errorMessage =
            'No fue posible cargar la inscripción.';

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

    /*
     * Preseleccionamos competencia.
     */
    this.filteredCompetitionCategories =
      this.competitionCategories.filter(
        (item) =>
          item.competition ===
          competitionId
      );

    this.registrationForm.patchValue(
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

    this.filteredPlayers =
      this.sortPlayersForCategory(
        category
      );

    this.registrationForm.patchValue(
      {
        competition_category:
          competitionCategoryId,

        player:
          0,
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

    this.playerSearchResults = [];

    this.playerSearchControl.setValue('');

    this.registrationForm.patchValue(
      {
        competition_category:
          0,

        player:
          0,
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

      this.playerSearchResults = [];

      this.playerSearchControl.setValue('');

      this.showPlayerResults = false;

      this.registrationForm.patchValue(
        {
          player:
            0,
        },
        {
          emitEvent: false,
        }
      );

      return;
    }


    this.filteredPlayers =
      this.sortPlayersForCategory(
        competitionCategory
      );

    this.playerSearchResults = [];

    this.playerSearchControl.setValue('');

    this.showPlayerResults = false;

    this.registrationForm.patchValue(
      {
        player:
          0,
      },
      {
        emitEvent: false,
      }
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


  getSelectedPlayer(): Player | null {

    const playerId =
      this.registrationForm.controls
        .player.value;

    return (
      this.players.find(
        (player) => player.id === playerId
      ) ?? null
    );
  }


  getSelectedCompetitionCategory():
    CompetitionCategory | null {

    const competitionCategoryId =
      this.registrationForm.controls
        .competition_category.value;

    return (
      this.competitionCategories.find(
        (item) =>
          item.id === competitionCategoryId
      ) ?? null
    );
  }


  isCategoryMatch(player: Player): boolean {

    const competitionCategory =
      this.getSelectedCompetitionCategory();

    return (
      competitionCategory !== null
      &&
      player.category ===
        competitionCategory.category
    );
  }


  isExceptionalCategorySelection(): boolean {

    const player = this.getSelectedPlayer();

    return (
      player !== null
      &&
      !this.isCategoryMatch(player)
    );
  }


  isPlayerRegisteredInCurrentCompetition(
    playerId: number
  ): boolean {

    const competitionId =
      this.registrationForm.controls
        .competition.value;

    const competitionCategoryIds =
      new Set(
        this.competitionCategories
          .filter(
            (item) =>
              item.competition === competitionId
          )
          .map((item) => item.id)
      );

    return this.registrations.some(
      (registration) =>
        registration.player === playerId
        &&
        registration.status !== 'CANCELADA'
        &&
        registration.id !== this.registrationId
        &&
        competitionCategoryIds.has(
          registration.competition_category
        )
    );
  }


  openPlayerSearch(): void {

    if (
      this.getSelectedCompetitionCategory() ===
      null
    ) {
      return;
    }

    this.showPlayerResults = true;

    this.updatePlayerSearchResults();
  }


  updatePlayerSearchResults(): void {

    const query = this.normalizeText(
      this.playerSearchControl.value
    );

    this.playerSearchResults =
      this.filteredPlayers.filter(
        (player) => {

          const fullName = this.normalizeText(
            `${player.first_name} ${player.last_name}`
          );

          const reversedName = this.normalizeText(
            `${player.last_name} ${player.first_name}`
          );

          return (
            !query
            ||
            fullName.includes(query)
            ||
            reversedName.includes(query)
          );
        }
      );

    this.showPlayerResults = true;
  }


  selectPlayer(player: Player): void {

    if (
      this.isPlayerRegisteredInCurrentCompetition(
        player.id
      )
    ) {
      return;
    }

    this.registrationForm.controls
      .player.setValue(player.id);

    this.playerSearchControl.setValue(
      this.getPlayerName(player),
      { emitEvent: false }
    );

    this.showPlayerResults = false;
  }


  clearSelectedPlayer(): void {

    this.registrationForm.controls
      .player.setValue(0);

    this.playerSearchControl.setValue('');

    this.openPlayerSearch();
  }


  private sortPlayersForCategory(
    competitionCategory:
      CompetitionCategory
  ): Player[] {

    return [...this.players].sort(
      (left, right) => {

        const categoryOrder =
          Number(
            right.category ===
              competitionCategory.category
          )
          -
          Number(
            left.category ===
              competitionCategory.category
          );

        if (categoryOrder !== 0) {
          return categoryOrder;
        }

        return this.getPlayerName(left)
          .localeCompare(
            this.getPlayerName(right),
            'es',
            { sensitivity: 'base' }
          );
      }
    );
  }


  private normalizeText(value: string): string {

    return value
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase('es')
      .trim();
  }


  // =====================================================
  // SUBMIT
  // =====================================================

  onSubmit(): void {

    if (!this.isAdministrativeUser()) {
      return;
    }

    this.errorMessage = '';

    if (
      this.registrationForm.invalid
    ) {

      this.registrationForm
        .markAllAsTouched();

      return;
    }

    const formValue =
      this.registrationForm
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
      formValue.player <= 0
    ) {

      this.errorMessage =
        'Debes seleccionar un jugador.';

      return;
    }


    if (
      this.isEditMode
      && this.registrationId !== null
    ) {

      this.updateRegistration();

      return;
    }

    this.createRegistration();
  }


  // =====================================================
  // CREAR INSCRIPCIÓN
  // =====================================================

  private createRegistration(): void {

    this.loading = true;

    this.errorMessage = '';

    const formValue =
      this.registrationForm
        .getRawValue();

    const registration:
      CreateRegistrationRequest = {

      competition_category:
        formValue.competition_category,

      player:
        formValue.player,

      status:
        formValue.status,

      seed:
        formValue.seed,
    };

    this.registrationService
      .createRegistration(
        registration
      )
      .subscribe({

        next: () => {

          /*
           * Si llegamos desde:
           *
           * Competencia
           * → Categorías
           * → Inscribir jugador
           *
           * volvemos a la misma competencia.
           */
          const competitionId =
            this.route.snapshot
              .queryParamMap
              .get('competition');

          if (competitionId) {

            this.router.navigate(
              [
                '/competitions',
                Number(competitionId),
                'categories',
              ],
              {
                state: {
                  successMessage:
                    'Jugador inscrito correctamente.',
                },
              }
            );

            return;
          }

          /*
           * Si llegamos desde el listado
           * general de inscripciones,
           * volvemos a /registrations.
           */
          this.router.navigate(
            ['/registrations'],
            {
              state: {
                successMessage:
                  'Inscripción creada correctamente.',
              },
            }
          );
        },

        error: (error) => {

          console.error(
            'Error al crear inscripción:',
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
  // ACTUALIZAR INSCRIPCIÓN
  // =====================================================

  private updateRegistration(): void {

    this.loading = true;

    this.errorMessage = '';

    const formValue =
      this.registrationForm
        .getRawValue();

    const registration:
      UpdateRegistrationRequest = {

      competition_category:
        formValue.competition_category,

      player:
        formValue.player,

      status:
        formValue.status,

      seed:
        formValue.seed,
    };

    this.registrationService
      .updateRegistration(
        this.registrationId!,
        registration
      )
      .subscribe({

        next: () => {

          this.router.navigate(
            ['/registrations'],
            {
              state: {
                successMessage:
                  'Inscripción actualizada correctamente.',
              },
            }
          );
        },

        error: (error) => {

          console.error(
            'Error al actualizar inscripción:',
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

    /*
     * Si llegamos desde una competencia,
     * Cancelar también debe volver a ella.
     */
    const competitionId =
      this.route.snapshot
        .queryParamMap
        .get('competition');

    if (competitionId) {

      this.router.navigate([
        '/competitions',
        Number(competitionId),
        'categories',
      ]);

      return;
    }

    this.router.navigate([
      '/registrations',
    ]);
  }
}
