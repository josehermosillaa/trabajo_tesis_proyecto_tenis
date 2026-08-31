import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import {
  CreateOrganizerRequest,
  UpdateOrganizerRequest,
} from '../../models/organizer.model';
import { OrganizerService } from '../../services/organizer';

@Component({
  selector: 'app-organizer-form',
  imports: [ReactiveFormsModule],
  templateUrl: './organizer-form.html',
})
export class OrganizerFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly organizerService = inject(OrganizerService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  organizerId: number | null = null;
  isEditMode = false;
  loading = false;
  saving = false;
  errorMessage = '';

  readonly organizerForm = this.fb.nonNullable.group({
    first_name: ['', Validators.required],
    last_name: ['', Validators.required],
    username: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: [''],
    password_confirmation: [''],
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.organizerForm.controls.password.addValidators(Validators.required);
      this.organizerForm.controls.password_confirmation.addValidators(Validators.required);
      return;
    }

    this.organizerId = Number(id);
    this.isEditMode = true;
    this.loadOrganizer(this.organizerId);
  }

  save(): void {
    this.errorMessage = '';
    this.organizerForm.markAllAsTouched();
    if (this.organizerForm.invalid) {
      return;
    }

    const values = this.organizerForm.getRawValue();
    if (!this.isEditMode && values.password !== values.password_confirmation) {
      this.errorMessage = 'Las contraseñas no coinciden.';
      return;
    }

    this.saving = true;
    if (this.isEditMode && this.organizerId !== null) {
      const request: UpdateOrganizerRequest = {
        first_name: values.first_name,
        last_name: values.last_name,
        username: values.username,
        email: values.email,
      };
      this.organizerService.updateOrganizer(this.organizerId, request).subscribe({
        next: () => this.finish('Organizador actualizado correctamente.'),
        error: (error) => this.fail(error),
      });
      return;
    }

    const request: CreateOrganizerRequest = {
      first_name: values.first_name,
      last_name: values.last_name,
      username: values.username,
      email: values.email,
      password: values.password,
      password_confirmation: values.password_confirmation,
    };
    this.organizerService.createOrganizer(request).subscribe({
      next: () => this.finish('Organizador creado correctamente.'),
      error: (error) => this.fail(error),
    });
  }

  cancel(): void {
    this.router.navigate(['/organizers']);
  }

  private loadOrganizer(id: number): void {
    this.loading = true;
    this.organizerService.getOrganizer(id).subscribe({
      next: (organizer) => {
        this.organizerForm.patchValue({
          first_name: organizer.first_name,
          last_name: organizer.last_name,
          username: organizer.username,
          email: organizer.email,
        });
        this.loading = false;
      },
      error: (error) => {
        this.errorMessage = this.getBackendError(error);
        this.loading = false;
      },
    });
  }

  private finish(message: string): void {
    this.saving = false;
    this.router.navigate(['/organizers'], {
      state: { successMessage: message },
    });
  }

  private fail(error: unknown): void {
    this.errorMessage = this.getBackendError(error);
    this.saving = false;
  }

  private getBackendError(error: unknown): string {
    const body = (error as { error?: unknown })?.error;
    if (typeof body === 'string') return body;
    if (body && typeof body === 'object') {
      const record = body as Record<string, unknown>;
      const detail = record['detail'];
      if (typeof detail === 'string') return detail;
      for (const value of Object.values(record)) {
        if (typeof value === 'string') return value;
        if (Array.isArray(value) && typeof value[0] === 'string') return value[0];
      }
    }
    return 'No fue posible guardar el organizador.';
  }
}
