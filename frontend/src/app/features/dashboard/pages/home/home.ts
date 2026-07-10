import { Component, inject } from '@angular/core';

import { Router } from '@angular/router';

import { AuthService } from '../../../../core/services/auth';

@Component({
  selector: 'app-home',
  imports: [],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class HomeComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  logout(): void {

    this.authService.logout();

    this.router.navigate(['/login']);

  }
}
