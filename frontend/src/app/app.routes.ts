import { Routes } from '@angular/router';

import { LoginComponent } from './features/authentication/pages/login/login';
import { HomeComponent } from './features/dashboard/pages/home/home';
import { authGuard } from './core/guards/auth-guard';
import { CompetitionListComponent } from './features/competitions/pages/competition-list/competition-list';
import { CompetitionFormComponent } from './features/competitions/pages/competition-form/competition-form';

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
  {
  path: 'competitions',
  component: CompetitionListComponent,
  canActivate: [authGuard],
},
{
  path: 'competitions/new',
  component: CompetitionFormComponent,
  canActivate: [authGuard],
},
{
  path: 'competitions/:id/edit',
  component: CompetitionFormComponent,
  canActivate: [authGuard],
},
];