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
  CompetitionCategory,
  CreateRegistrationRequest,
  UpdateRegistrationRequest,
} from '../../models/registration.model';

import { Player } from '../../../players/models/player.model';

@Component({
  selector: 'app-registration-form',
  imports: [ReactiveFormsModule],
  templateUrl: './registration-form.html',
  styleUrl: './registration-form.scss',
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

      status: this.fb.nonNullable.control<
      'PENDIENTE' | 'CONFIRMADA' | 'CANCELADA'
        >(
          'PENDIENTE',
          Validators.required
      ),

      seed: [
        null as number | null,
      ],

    });

  ngOnInit(): void {

    this.loadBaseData();

    const id =
      this.route.snapshot.paramMap.get(
        'id'
      );

    if (id) {

      this.isEditMode = true;

      this.registrationId =
        Number(id);

    }

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

          if (
            this.isEditMode &&
            this.registrationId !== null
          ) {

            this.loadRegistration(
              this.registrationId
            );

          } else {

            this.applyQueryParams();

            this.loading = false;
          }

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

          this.filteredCompetitionCategories =
            this.competitionCategories.filter(
              (item) =>
                item.competition ===
                competitionCategory.competition
            );

          this.filteredPlayers =
            this.players.filter(
              (player) =>
                player.category ===
                competitionCategory.category
            );

          this.registrationForm.patchValue({

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

          }, {
            emitEvent: false,
          });

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
      this.players.filter(
        (player) =>
          player.category ===
          category.category
      );

    this.registrationForm.patchValue(
      {
        competition_category:
          competitionCategoryId,

        player: 0,
      },
      {
        emitEvent: false,
      }
    );
  }

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

    this.registrationForm.patchValue(
      {
        competition_category: 0,
        player: 0,
      },
      {
        emitEvent: false,
      }
    );
  }

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

      this.registrationForm.patchValue(
        {
          player: 0,
        },
        {
          emitEvent: false,
        }
      );

      return;
    }

    this.filteredPlayers =
      this.players.filter(
        (player) =>
          player.category ===
          competitionCategory.category
      );

    this.registrationForm.patchValue(
      {
        player: 0,
      },
      {
        emitEvent: false,
      }
    );
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

  getPlayerName(
    player: Player
  ): string {

    return (
      `${player.first_name} ${player.last_name}`
    );
  }

  onSubmit(): void {

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
      this.isEditMode &&
      this.registrationId !== null
    ) {

      this.updateRegistration();

      return;
    }

    this.createRegistration();
  }

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

  cancel(): void {

    this.router.navigate([
      '/registrations',
    ]);
  }
}