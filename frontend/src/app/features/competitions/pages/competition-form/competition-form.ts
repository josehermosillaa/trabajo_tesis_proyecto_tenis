import { Component, OnInit, inject } from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';

import { ActivatedRoute, Router } from '@angular/router';

import { CompetitionService } from '../../services/competition';

@Component({
  selector: 'app-competition-form',
  imports: [ReactiveFormsModule],
  templateUrl: './competition-form.html',
  styleUrl: './competition-form.scss',
})
export class CompetitionFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly competitionService = inject(CompetitionService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  loading = false;
  errorMessage = '';

  isEditMode = false;
  competitionId: number | null = null;

  readonly competitionForm = this.fb.nonNullable.group({
    name: ['', Validators.required],
    type: ['ELIMINACION_DIRECTA', Validators.required],
    start_date: ['', Validators.required],
    end_date: ['', Validators.required],
    status: ['PENDIENTE', Validators.required],
    registration_deadline: ['', Validators.required],
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');

    if (id) {
      this.isEditMode = true;
      this.competitionId = Number(id);

      this.loadCompetition(this.competitionId);
    }
  }

  loadCompetition(id: number): void {
    this.loading = true;
    this.errorMessage = '';

    this.competitionService.getCompetition(id).subscribe({
      next: (competition) => {
        this.competitionForm.patchValue({
          name: competition.name,
          type: competition.type,
          start_date: competition.start_date,
          end_date: competition.end_date,
          status: competition.status,
          registration_deadline:
            competition.registration_deadline,
        });

        this.loading = false;
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

  onSubmit(): void {
    if (this.competitionForm.invalid) {
      this.competitionForm.markAllAsTouched();
      return;
    }

    if (this.isEditMode && this.competitionId !== null) {
      this.updateCompetition();
      return;
    }

    this.createCompetition();
  }

  private createCompetition(): void {
    this.loading = true;
    this.errorMessage = '';

    const competition =
      this.competitionForm.getRawValue();

    this.competitionService
      .createCompetition(competition)
      .subscribe({
        next: () => {
          this.router.navigate(['/competitions']);
        },
        error: (error) => {
          console.error(
            'Error al crear competencia:',
            error
          );

          this.errorMessage =
            'No fue posible crear la competencia.';

          this.loading = false;
        },
      });
  }

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
          this.router.navigate(['/competitions']);
        },
        error: (error) => {
          console.error(
            'Error al actualizar competencia:',
            error
          );

          this.errorMessage =
            'No fue posible actualizar la competencia.';

          this.loading = false;
        },
      });
  }

  cancel(): void {
    this.router.navigate(['/competitions']);
  }
}