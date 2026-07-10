import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { Router } from '@angular/router';

import { AuthService } from '../../../../core/services/auth';
import { TokenService } from '../../../../core/services/token';
@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss'
})
export class LoginComponent {

  private readonly fb = inject(FormBuilder);

  private readonly authService = inject(AuthService);
  private readonly tokenService = inject(TokenService);
  private readonly router = inject(Router);

  readonly loginForm = this.fb.nonNullable.group({
    username: ['', Validators.required],
    password: ['', Validators.required]
  });

  onSubmit(): void {
  console.log('Entró al onSubmit');
  if (this.loginForm.invalid) {
    this.loginForm.markAllAsTouched();
    return;
  }
  const credentials = this.loginForm.getRawValue();

  this.authService.login(credentials).subscribe({
  next: (response) => {

    this.tokenService.saveTokens(
      response.access,
      response.refresh
    );

    // console.log('Tokens guardados correctamente');
    this.router.navigate(['/dashboard']);

  },
  error: (error) => {
    console.error(error);
  }

});

}


}