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
  Category,
  PlayerService,
} from '../../services/player';

import {
  CreatePlayerRequest,
  UpdatePlayerRequest,
} from '../../models/player.model';

@Component({
  selector: 'app-player-form',
  imports: [ReactiveFormsModule],
  templateUrl: './player-form.html',
  styleUrl: './player-form.scss',
})
export class PlayerFormComponent implements OnInit {

  private readonly fb =
    inject(FormBuilder);

  private readonly playerService =
    inject(PlayerService);

  private readonly router =
    inject(Router);

  private readonly route =
    inject(ActivatedRoute);

  loading = false;
  loadingCategories = false;

  errorMessage = '';

  isEditMode = false;

  playerId: number | null = null;

  categories: Category[] = [];
  readonly maxBirthDate =
  this.getMaxBirthDate();

  readonly playerForm =
    this.fb.nonNullable.group({

      username: [
        '',
        Validators.required,
      ],

      email: [
        '',
        [
          Validators.required,
          Validators.email,
        ],
      ],

      password: [
        '',
      ],

      category: [
        0,
        Validators.required,
      ],

      rut: [
        '',
        Validators.required,
      ],

      first_name: [
        '',
        Validators.required,
      ],

      last_name: [
        '',
        Validators.required,
      ],

      birth_date: [
        '',
      ],

      phone: [
        '',
        [
          Validators.pattern(/^\d{8}$/),
        ],
      ],
    });

  ngOnInit(): void {

    this.loadCategories();

    const id =
      this.route.snapshot.paramMap.get(
        'id'
      );

    if (id) {

      this.isEditMode = true;

      this.playerId =
        Number(id);

      this.loadPlayer(
        this.playerId
      );

    }

  }

  private loadCategories(): void {

    this.loadingCategories = true;

    this.playerService
      .getCategories()
      .subscribe({

        next: (categories) => {

          this.categories =
            categories;

          this.loadingCategories =
            false;

        },

        error: (error) => {

          console.error(
            'Error al cargar categorías:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las categorías.';

          this.loadingCategories =
            false;

        },

      });

  }

  private loadPlayer(
    id: number
  ): void {

    this.loading = true;

    this.errorMessage = '';

    this.playerService
      .getPlayer(id)
      .subscribe({

        next: (player) => {

          this.playerForm.patchValue({

            username:
              player.username,

            email:
              player.email,

            category:
              player.category,

            rut:
              player.rut,

            first_name:
              player.first_name,

            last_name:
              player.last_name,

            birth_date:
              player.birth_date ?? '',

            phone:
              player.phone?.startsWith('+569')
                ? player.phone.substring(4)
                : player.phone,

          });

          this.loading = false;

        },

        error: (error) => {

          console.error(
            'Error al cargar jugador:',
            error
          );

          this.errorMessage =
            'No fue posible cargar el jugador.';

          this.loading = false;

        },

      });

  }

/* ============================= */
/* VALIDACIÓN Y FORMATO DEL RUT */
/* ============================= */

isValidRut(rutValue: string): boolean {

    const rut = rutValue
      .replace(/\./g, '')
      .replace(/-/g, '')
      .trim()
      .toUpperCase();

    if (rut.length < 2) {
      return false;
    }

    const body = rut.slice(0, -1);
    const verifier = rut.slice(-1);

    if (!/^\d+$/.test(body)) {
      return false;
    }

    let total = 0;
    let multiplier = 2;

    for (
      let i = body.length - 1;
      i >= 0;
      i--
    ) {

      total +=
        Number(body[i]) * multiplier;

      multiplier++;

      if (multiplier > 7) {
        multiplier = 2;
      }
    }

    const remainder =
      11 - (total % 11);

    let expectedVerifier: string;

    if (remainder === 11) {

      expectedVerifier = '0';

    } else if (remainder === 10) {

      expectedVerifier = 'K';

    } else {

      expectedVerifier =
        String(remainder);

    }

    return verifier === expectedVerifier;
  }


  private normalizeRut(
    rutValue: string
  ): string {

    const rut = rutValue
      .replace(/\./g, '')
      .replace(/-/g, '')
      .trim()
      .toUpperCase();

    const body =
      rut.slice(0, -1);

    const verifier =
      rut.slice(-1);

    return `${body}-${verifier}`;
  }



  onSubmit(): void {

    this.errorMessage = '';

    if (
      this.playerForm.invalid
    ) {

      this.playerForm
        .markAllAsTouched();

      return;

    }

    const formValue =
      this.playerForm.getRawValue();
    if (!this.isValidRut(formValue.rut)) {

      this.errorMessage =
        'El RUT ingresado no es válido.';

      return;
    }
    if (
      formValue.birth_date &&
      formValue.birth_date >
        this.maxBirthDate
      ) {
        this.errorMessage =
          'El jugador debe tener al menos 10 años.';

        return;
      }

    if (
      formValue.category <= 0
    ) {

      this.errorMessage =
        'Debes seleccionar una categoría.';

      return;

    }

    /*
     * En creación la contraseña
     * temporal es obligatoria.
     */
    if (
      !this.isEditMode &&
      !formValue.password
    ) {

      this.errorMessage =
        'La contraseña temporal es obligatoria.';

      return;

    }

    if (
      this.isEditMode &&
      this.playerId !== null
    ) {

      this.updatePlayer();

      return;

    }

    this.createPlayer();

  }

  private createPlayer(): void {

    this.loading = true;

    this.errorMessage = '';

    const formValue =
      this.playerForm.getRawValue();

    const player:
      CreatePlayerRequest = {

      username:
        formValue.username,

      email:
        formValue.email,

      password:
        formValue.password,

      category:
        formValue.category,

      rut:
        this.normalizeRut(
          formValue.rut
        ),

      first_name:
        formValue.first_name,

      last_name:
        formValue.last_name,

      birth_date:
        formValue.birth_date || null,

      phone:
        formValue.phone
          ? `+569${formValue.phone}`
          : '',

    };

    this.playerService
      .createPlayer(player)
      .subscribe({

        next: () => {

          this.router.navigate(
            ['/players'],
            {
              state: {
                successMessage:
                  'Jugador creado correctamente.',
              },
            }
          );

        },

        error: (error) => {

          console.error(
            'Error al crear jugador:',
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

  private updatePlayer(): void {

    this.loading = true;

    this.errorMessage = '';

    const formValue =
      this.playerForm.getRawValue();

    const player:
      UpdatePlayerRequest = {

      username:
        formValue.username,

      email:
        formValue.email,

      category:
        formValue.category,

      rut:
        this.normalizeRut(
          formValue.rut
        ),

      first_name:
        formValue.first_name,

      last_name:
        formValue.last_name,

      birth_date:
        formValue.birth_date || null,

      phone:
        formValue.phone
          ? `+569${formValue.phone}`
          : '',

    };

    this.playerService
      .updatePlayer(
        this.playerId!,
        player
      )
      .subscribe({

        next: () => {

          this.router.navigate(
            ['/players'],
            {
              state: {
                successMessage:
                  'Jugador actualizado correctamente.',
              },
            }
          );

        },

        error: (error) => {

          console.error(
            'Error al actualizar jugador:',
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
  private getMaxBirthDate(): string {

    const today = new Date();

    const maxDate = new Date(
      today.getFullYear() - 10,
      today.getMonth(),
      today.getDate()
    );

    const year =
      maxDate.getFullYear();

    const month =
      String(
        maxDate.getMonth() + 1
      ).padStart(2, '0');

    const day =
      String(
        maxDate.getDate()
      ).padStart(2, '0');

    return `${year}-${month}-${day}`;
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
      '/players',
    ]);

  }

}