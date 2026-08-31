import { Component, OnInit, inject } from '@angular/core';
import {
  FormBuilder,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';

import { ActivatedRoute, Router } from '@angular/router';

import { CompetitionService } from '../../services/competition';

import {
  Category,
  CompetitionCategoryService,
} from '../../../competition-categories/services/competition-category';

import { CompetitionCategory } from '../../../competition-categories/models/competition-category.model';
import { TokenService } from '../../../../core/services/token';
import { TemporalInputComponent } from '../../../../shared/date-time/temporal-input.component';

@Component({
  selector: 'app-competition-form',
  imports: [FormsModule, ReactiveFormsModule, TemporalInputComponent],
  templateUrl: './competition-form.html',
  styleUrl: './competition-form.scss',
})
export class CompetitionFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);

  private readonly competitionService = inject(
    CompetitionService
  );

  private readonly competitionCategoryService = inject(
    CompetitionCategoryService
  );

  private readonly router = inject(Router);

  private readonly route = inject(ActivatedRoute);
  private readonly tokenService = inject(TokenService);

  isAdministrativeUser(): boolean {
    return this.tokenService.isAdministrativeUser();
  }

  loading = false;

  loadingCategories = false;

  errorMessage = '';

  categoriesErrorMessage = '';

  isEditMode = false;

  competitionId: number | null = null;

  categories: Category[] = [];

  competitionCategories: CompetitionCategory[] = [];

  selectedCategories: number[] = [];

  /*
   * Categorías que ya existen en la competencia.
   *
   * Las usamos para diferenciar:
   *
   * - actualizar una CompetitionCategory existente
   * - crear una nueva CompetitionCategory
   */
  existingCategoryIds: number[] = [];

  categorySettings: {
    [categoryId: number]: {
      minimum_players: number;
      max_players: number;
    };
  } = {};

  readonly competitionForm = this.fb.nonNullable.group({
    name: ['', Validators.required],

    type: [
      'ELIMINACION_DIRECTA',
      Validators.required,
    ],

    start_date: ['', Validators.required],

    end_date: ['', Validators.required],

    status: [
      'PENDIENTE',
      Validators.required,
    ],

    registration_deadline: [
      '',
      Validators.required,
    ],
  });

  ngOnInit(): void {
    this.loadCategories();

    const id =
      this.route.snapshot.paramMap.get('id');

    if (id) {
      this.isEditMode = true;

      this.competitionId = Number(id);

      this.loadCompetition(
        this.competitionId
      );
    }
  }

  /*
   * =========================================================
   * CATEGORÍAS DISPONIBLES
   * =========================================================
   */

  loadCategories(): void {
    this.loadingCategories = true;

    this.categoriesErrorMessage = '';

    this.competitionCategoryService
      .getCategories()
      .subscribe({
        next: (categories) => {
          this.categories = categories;

          /*
           * Valores por defecto para una categoría
           * que todavía no ha sido configurada.
           */
          for (const category of categories) {
            this.categorySettings[
              category.id
            ] = {
              minimum_players: 4,
              max_players: 16,
            };
          }

          this.loadingCategories = false;

          /*
           * Si estamos editando y las CompetitionCategory
           * ya fueron cargadas, sincronizamos nuevamente.
           */
          if (this.isEditMode) {
            this.applyExistingCompetitionCategories();
          }
        },

        error: (error) => {
          console.error(
            'Error al cargar categorías:',
            error
          );

          this.categoriesErrorMessage =
            'No fue posible cargar las categorías.';

          this.loadingCategories = false;
        },
      });
  }

  /*
   * =========================================================
   * COMPETENCIA
   * =========================================================
   */

  loadCompetition(id: number): void {
    this.loading = true;

    this.errorMessage = '';

    this.competitionService
      .getCompetition(id)
      .subscribe({
        next: (competition) => {
          this.competitionForm.patchValue({
            name: competition.name,

            type: competition.type,

            start_date:
              competition.start_date,

            end_date:
              competition.end_date,

            status: competition.status,

            registration_deadline:
              competition.registration_deadline,
          });

          /*
           * Cargamos también las categorías asociadas
           * a esta competencia.
           */
          this.loadCompetitionCategories(
            id
          );
        },

        error: (error) => {
          console.error(
            'Error al cargar competencia:',
            error
          );

          this.errorMessage =
            'No fue posible cargar la competencia.';

          this.loading = false;
        },
      });
  }

  /*
   * =========================================================
   * COMPETITION CATEGORY
   * =========================================================
   */

  loadCompetitionCategories(
    competitionId: number
  ): void {
    this.competitionCategoryService
      .getCompetitionCategories()
      .subscribe({
        next: (competitionCategories) => {
          this.competitionCategories =
            competitionCategories.filter(
              (item) =>
                item.competition ===
                competitionId
            );

          this.existingCategoryIds =
            this.competitionCategories.map(
              (item) => item.category
            );

          /*
           * Las categorías que ya existen
           * quedan seleccionadas.
           */
          this.selectedCategories = [
            ...this.existingCategoryIds,
          ];

          this.applyExistingCompetitionCategories();

          this.loading = false;
        },

        error: (error) => {
          console.error(
            'Error al cargar categorías de la competencia:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las categorías de la competencia.';

          this.loading = false;
        },
      });
  }

  /*
   * Copia los valores existentes de
   * CompetitionCategory hacia categorySettings.
   */
  private applyExistingCompetitionCategories(): void {
    for (const competitionCategory of this.competitionCategories) {
      this.categorySettings[
        competitionCategory.category
      ] = {
        minimum_players:
          competitionCategory.minimum_players,

        max_players:
          competitionCategory.max_players,
      };
    }
  }

  /*
   * =========================================================
   * SELECCIÓN DE CATEGORÍAS
   * =========================================================
   */

  isCategorySelected(
    categoryId: number
  ): boolean {
    return this.selectedCategories.includes(
      categoryId
    );
  }

  /*
   * Indica si la categoría ya pertenece
   * a la competencia.
   */
  isExistingCategory(
    categoryId: number
  ): boolean {
    return this.existingCategoryIds.includes(
      categoryId
    );
  }

toggleCategory(
  categoryId: number
): void {

  if (
    this.isCategorySelected(
      categoryId
    )
  ) {

    this.selectedCategories =
      this.selectedCategories.filter(
        (id) =>
          id !== categoryId
      );

    return;
  }

  this.selectedCategories = [
    ...this.selectedCategories,
    categoryId,
  ];
}

  /*
   * =========================================================
   * SUBMIT
   * =========================================================
   */

  onSubmit(): void {
    if (!this.isAdministrativeUser()) {
      return;
    }

    if (this.competitionForm.invalid) {
      this.competitionForm.markAllAsTouched();

      return;
    }

    if (
      this.selectedCategories.length === 0
    ) {
      this.errorMessage =
        'Debes seleccionar al menos una categoría.';

      return;
    }

    /*
     * Validación de mínimo y máximo.
     */
    const invalidCategory =
      this.selectedCategories.find(
        (categoryId) => {
          const settings =
            this.categorySettings[
              categoryId
            ];

          return (
            !settings ||
            settings.minimum_players < 1 ||
            settings.max_players < 1 ||
            settings.minimum_players >
              settings.max_players
          );
        }
      );

    if (
      invalidCategory !== undefined
    ) {
      this.errorMessage =
        'Revisa los valores mínimo y máximo de jugadores de las categorías.';

      return;
    }

    if (
      this.isEditMode &&
      this.competitionId !== null
    ) {
      this.updateCompetition();

      return;
    }

    this.createCompetition();
  }

  /*
   * =========================================================
   * CREAR COMPETENCIA
   * =========================================================
   */

  private createCompetition(): void {
    this.loading = true;

    this.errorMessage = '';

    const competition =
      this.competitionForm.getRawValue();

    this.competitionService
      .createCompetition(competition)
      .subscribe({
        next: (createdCompetition) => {
          this.createCompetitionCategories(
            createdCompetition.id
          );
        },

        error: (error) => {
          console.error(
            'Error al crear competencia:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(error);

          this.loading = false;
        },
      });
  }

  /*
   * =========================================================
   * CREAR CATEGORÍAS DE UNA NUEVA COMPETENCIA
   * =========================================================
   */

  private createCompetitionCategories(
    competitionId: number
  ): void {
    const requests =
      this.selectedCategories.map(
        (categoryId) => {
          const settings =
            this.categorySettings[
              categoryId
            ];

          return this.competitionCategoryService
            .createCompetitionCategory({
              competition:
                competitionId,

              category:
                categoryId,

              minimum_players:
                settings.minimum_players,

              max_players:
                settings.max_players,
            });
        }
      );

    this.createNextCategory(
      requests,
      0
    );
  }

  private createNextCategory(
    requests: ReturnType<
      CompetitionCategoryService['createCompetitionCategory']
    >[],
    index: number
  ): void {
    if (index >= requests.length) {
  this.router.navigate(
    ['/competitions'],
    {
      state: {
        successMessage:
          'Competencia creada correctamente.',
      },
    }
  );

  return;
}

    requests[index].subscribe({
      next: () => {
        this.createNextCategory(
          requests,
          index + 1
        );
      },

      error: (error) => {
        console.error(
          'Error al crear categoría de competencia:',
          error
        );

        this.errorMessage =
          'La competencia fue creada, pero no fue posible configurar todas sus categorías.';

        this.loading = false;
      },
    });
  }

  /*
   * =========================================================
   * ACTUALIZAR COMPETENCIA
   * =========================================================
   */

  private updateCompetition(): void {
    this.loading = true;

    this.errorMessage = '';

    const competition =
      this.competitionForm.getRawValue();

    this.competitionService
      .updateCompetition(
        this.competitionId!,
        competition
      )
      .subscribe({
        next: () => {
          this.updateCompetitionCategories(
            this.competitionId!
          );
        },

        error: (error) => {
          console.error(
            'Error al actualizar competencia:',
            error
          );

          this.errorMessage =
            this.getBackendErrorMessage(error);

          this.loading = false;
        },
      });
  }

  /*
   * =========================================================
   * ACTUALIZAR / CREAR CATEGORÍAS
   * =========================================================
   */

  private updateCompetitionCategories(
    competitionId: number
  ): void {

    /*
    * Categorías que existían antes,
    * pero que el usuario desmarcó.
    */
    const categoriesToDelete =
      this.competitionCategories.filter(
        (competitionCategory) =>
          !this.selectedCategories.includes(
            competitionCategory.category
          )
      );

    /*
    * Primero intentamos eliminar
    * las categorías desmarcadas.
    */
    this.deleteRemovedCategories(
      categoriesToDelete,
      0,
      competitionId
    );
  }
  private deleteRemovedCategories(
    categoriesToDelete:
      CompetitionCategory[],
    index: number,
    competitionId: number
  ): void {

    /*
    * Ya eliminamos todas las
    * categorías desmarcadas.
    *
    * Ahora actualizamos o creamos
    * las seleccionadas.
    */
    if (
      index >=
      categoriesToDelete.length
    ) {

      this.saveSelectedCategories(
        competitionId
      );

      return;
    }

    const competitionCategory =
      categoriesToDelete[index];

    this.competitionCategoryService
      .deleteCompetitionCategory(
        competitionCategory.id
      )
      .subscribe({

        next: () => {

          this.deleteRemovedCategories(
            categoriesToDelete,
            index + 1,
            competitionId
          );
        },

        error: (error) => {

          console.error(
            'Error al eliminar categoría:',
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
private saveSelectedCategories(
    competitionId: number
  ): void {

    const requests =
      this.selectedCategories.map(
        (categoryId) => {

          const settings =
            this.categorySettings[
              categoryId
            ];

          /*
          * Si ya existía,
          * hacemos PATCH.
          */
          if (
            this.isExistingCategory(
              categoryId
            )
          ) {

            const existing =
              this.competitionCategories.find(
                (item) =>
                  item.category ===
                  categoryId
              );

            if (!existing) {

              throw new Error(
                'No se encontró la categoría existente.'
              );
            }

            return (
              this.competitionCategoryService
                .updateCompetitionCategory(
                  existing.id,
                  {
                    competition:
                      competitionId,

                    category:
                      categoryId,

                    minimum_players:
                      settings.minimum_players,

                    max_players:
                      settings.max_players,
                  }
                )
            );
          }

          /*
          * Si es una nueva categoría,
          * hacemos POST.
          */
          return (
            this.competitionCategoryService
              .createCompetitionCategory({
                competition:
                  competitionId,

                category:
                  categoryId,

                minimum_players:
                  settings.minimum_players,

                max_players:
                  settings.max_players,
              })
          );
        }
      );

    this.updateNextCategory(
      requests,
      0
    );
  }

  private updateNextCategory(
    requests: ReturnType<
      CompetitionCategoryService['updateCompetitionCategory']
    >[],
    index: number
  ): void {
    if (index >= requests.length) {
      this.router.navigate(
        [
          '/competitions',
          this.competitionId,
          'categories',
        ],
        {
          state: {
            successMessage:
              'Competencia actualizada correctamente.',
          },
        }
      );

      return;
    }

    requests[index].subscribe({
      next: () => {
        this.updateNextCategory(
          requests,
          index + 1
        );
      },

      error: (error) => {
        console.error(
          'Error al actualizar categoría de competencia:',
          error
        );

        this.errorMessage =
          'La competencia fue actualizada, pero no fue posible actualizar todas sus categorías.';

        this.loading = false;
      },
    });
  }
//backend error

  private getBackendErrorMessage(error: any): string {
  const backendError = error?.error;

  if (!backendError) {
    return 'Ocurrió un error inesperado.';
  }

  if (typeof backendError === 'string') {
    return backendError;
  }

  const messages: string[] = [];

  for (const key of Object.keys(backendError)) {
    const value = backendError[key];

    if (Array.isArray(value)) {
      messages.push(...value);
    } else if (typeof value === 'string') {
      messages.push(value);
    }
  }

  return messages.length > 0
    ? messages.join(' ')
    : 'Ocurrió un error inesperado.';
}

  /*
   * =========================================================
   * CANCELAR
   * =========================================================
   */

  cancel(): void {

    if (
      this.isEditMode
      &&
      this.competitionId !== null
    ) {

      this.router.navigate([
        '/competitions',
        this.competitionId,
        'categories',
      ]);

      return;
    }

    this.router.navigate([
      '/competitions',
    ]);
  }
}
