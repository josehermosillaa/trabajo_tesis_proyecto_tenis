import { Routes } from '@angular/router';

import { LoginComponent } from './features/authentication/pages/login/login';
import { HomeComponent } from './features/dashboard/pages/home/home';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full',
  },
  {
    path: 'login',
    component: LoginComponent,
  },
  {
    path: 'dashboard',
    component: HomeComponent,
    canActivate: [authGuard],
  },
];