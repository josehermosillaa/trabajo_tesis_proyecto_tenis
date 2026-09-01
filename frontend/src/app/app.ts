import {
  Component,
  HostListener,
  OnDestroy,
  OnInit,
  inject,
} from '@angular/core';

import {
  Router,
  RouterLink,
  RouterOutlet,
} from '@angular/router';

import { AuthService } from './core/services/auth';
import { TokenService } from './core/services/token';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit, OnDestroy {

  private readonly authService = inject(AuthService);
  private readonly tokenService = inject(TokenService);
  private readonly router = inject(Router);

  private inactivityTimer:
    ReturnType<typeof setTimeout> | null = null;

  navigationOpen = false;

  // 1 minuto solamente para probar
  private readonly inactivityTime = 20*60 * 1000;

  ngOnInit(): void {
    if (this.tokenService.isAuthenticated()) {
      this.resetInactivityTimer();
    }
  }

  ngOnDestroy(): void {
    this.clearInactivityTimer();
  }

  isAuthenticated(): boolean {
    return (
      this.tokenService.isAuthenticated() &&
      !this.router.url.startsWith('/login')
    );
  }

  isAdministrativeUser(): boolean {
    return this.tokenService.isAdministrativeUser();
  }

  isAdminUser(): boolean {
    return this.tokenService.isAdminUser();
  }

  logout(): void {
    this.navigationOpen = false;
    this.clearInactivityTimer();

    this.authService.logout();

    this.router.navigate(['/login']);
  }

  toggleNavigation(): void {
    this.navigationOpen = !this.navigationOpen;
  }

  closeNavigation(): void {
    this.navigationOpen = false;
  }

  @HostListener('document:mousemove')
  @HostListener('document:keydown')
  @HostListener('document:click')
  @HostListener('document:scroll')
  onUserActivity(): void {

    if (this.tokenService.isAuthenticated()) {
      this.resetInactivityTimer();
    }
  }

  private resetInactivityTimer(): void {

    this.clearInactivityTimer();

    if (!this.tokenService.isAuthenticated()) {
      return;
    }

    this.inactivityTimer = setTimeout(() => {
      this.logoutByInactivity();
    }, this.inactivityTime);
  }

  private clearInactivityTimer(): void {

    if (this.inactivityTimer !== null) {
      clearTimeout(this.inactivityTimer);

      this.inactivityTimer = null;
    }
  }

  private logoutByInactivity(): void {

    this.clearInactivityTimer();

    this.authService.logout();

    this.router.navigate(
      ['/login'],
      {
        state: {
          inactivityExpired: true,
        },
      }
    );
  }
}
