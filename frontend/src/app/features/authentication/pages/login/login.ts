import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

import {
  ReactiveFormsModule,
  FormBuilder,
  Validators,
} from '@angular/forms';

import { Router } from '@angular/router';

import { AuthService } from '../../../../core/services/auth';
import { TokenService } from '../../../../core/services/token';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class LoginComponent implements OnInit {
  private readonly fb = inject(FormBuilder);

  private readonly authService = inject(AuthService);

  private readonly tokenService = inject(TokenService);

  private readonly router = inject(Router);

  loading = false;

  errorMessage = '';

  readonly loginForm = this.fb.nonNullable.group({
    username: ['', Validators.required],
    password: ['', Validators.required],
  });

  ngOnInit(): void {
    if (history.state?.sessionExpired) {
      this.errorMessage =
        'Tu sesión ha expirado. Vuelve a iniciar sesión.';

      history.replaceState(
        {},
        document.title
      );
    }
  }

  onSubmit(): void {
    this.errorMessage = '';

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.loading = true;

    const credentials =
      this.loginForm.getRawValue();

    this.authService
      .login(credentials)
      .subscribe({
        next: (response) => {
          this.tokenService.saveTokens(
            response.access,
            response.refresh
          );

          this.router.navigate([
            '/dashboard',
          ]);
        },

        error: (error) => {
          console.error(
            'Error de login:',
            error
          );

          if (error.status === 401) {
            this.errorMessage =
              'Usuario o contraseña incorrectos.';
          } else if (error.status === 0) {
            this.errorMessage =
              'No fue posible conectar con el servidor.';
          } else {
            this.errorMessage =
              'No fue posible iniciar sesión. Intenta nuevamente.';
          }

          this.loading = false;
        },
      });
  }
}