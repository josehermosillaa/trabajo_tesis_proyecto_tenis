import { Routes } from '@angular/router';

import { LoginComponent } from './features/authentication/pages/login/login';
import { HomeComponent } from './features/dashboard/pages/home/home';
import { authGuard } from './core/guards/auth-guard';
import { CompetitionListComponent } from './features/competitions/pages/competition-list/competition-list';
import { CompetitionFormComponent } from './features/competitions/pages/competition-form/competition-form';
import { CompetitionCategoryListComponent } from './features/competition-categories/pages/competition-category-list/competition-category-list';
import { PlayerListComponent } from './features/players/pages/player-list/player-list';
import { PlayerFormComponent } from './features/players/pages/player-form/player-form';
import {
  RegistrationListComponent
} from './features/registrations/pages/registration-list/registration-list';

import {
  RegistrationFormComponent
} from './features/registrations/pages/registration-form/registration-form';

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
{
  path: 'competitions/:id/categories',
  component: CompetitionCategoryListComponent,
  canActivate: [authGuard],
},
{
  path: 'players',
  component: PlayerListComponent,
  canActivate: [authGuard],
},
{
  path: 'players/new',
  component: PlayerFormComponent,
  canActivate: [authGuard],
},
{
  path: 'players/:id/edit',
  component: PlayerFormComponent,
  canActivate: [authGuard],
},
{
  path: 'registrations',
  component: RegistrationListComponent,
  canActivate: [authGuard],
},
{
  path: 'registrations/new',
  component: RegistrationFormComponent,
  canActivate: [authGuard],
},
{
  path: 'registrations/:id/edit',
  component: RegistrationFormComponent,
  canActivate: [authGuard],
},
];