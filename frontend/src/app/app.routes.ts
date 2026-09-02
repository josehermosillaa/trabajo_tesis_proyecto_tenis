import { Routes } from '@angular/router';

import {
  LoginComponent
} from './features/authentication/pages/login/login';

import {
  HomeComponent
} from './features/dashboard/pages/home/home';

import {
  authGuard
} from './core/guards/auth-guard';
import { adminGuard } from './core/guards/admin-guard';
import { managementGuard } from './core/guards/management-guard';
import { OrganizerListComponent } from './features/organizers/pages/organizer-list/organizer-list';
import { OrganizerFormComponent } from './features/organizers/pages/organizer-form/organizer-form';

import {
  CompetitionListComponent
} from './features/competitions/pages/competition-list/competition-list';

import {
  CompetitionFormComponent
} from './features/competitions/pages/competition-form/competition-form';

import {
  CompetitionCategoryListComponent
} from './features/competition-categories/pages/competition-category-list/competition-category-list';

import {
  CompetitionCategoryDetailComponent
} from './features/competition-categories/pages/competition-category-detail/competition-category-detail';

import {
  PlayerListComponent
} from './features/players/pages/player-list/player-list';

import {
  PlayerFormComponent
} from './features/players/pages/player-form/player-form';

import {
  RegistrationListComponent
} from './features/registrations/pages/registration-list/registration-list';

import {
  RegistrationFormComponent
} from './features/registrations/pages/registration-form/registration-form';

import {
  MatchListComponent
} from './features/matches/pages/match-list/match-list';

import {
  MatchFormComponent
} from './features/matches/pages/match-form/match-form';

import {
  MatchResultComponent
} from './features/matches/pages/match-result/match-result';


export const routes: Routes = [

  // =====================================================
  // AUTH
  // =====================================================

  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full',
  },

  {
    path: 'login',
    component: LoginComponent,
  },


  // =====================================================
  // DASHBOARD
  // =====================================================

  {
    path: 'dashboard',
    component: HomeComponent,
    canActivate: [
      authGuard,
    ],
  },


  // =====================================================
  // COMPETITIONS
  // =====================================================

  {
    path: 'competitions',
    component: CompetitionListComponent,
    canActivate: [
      authGuard,
    ],
  },

  {
    path: 'competitions/new',
    component: CompetitionFormComponent,
    canActivate: [managementGuard],
  },

  {
    path: 'competitions/:id/edit',
    component: CompetitionFormComponent,
    canActivate: [managementGuard],
  },

  {
    path: 'competitions/:id/categories',
    component: CompetitionCategoryListComponent,
    canActivate: [
      authGuard,
    ],
  },

  /*
   * Vista deportiva de una categoría.
   *
   * ELIMINACION_DIRECTA:
   * muestra el cuadro.
   *
   * Más adelante esta misma estructura
   * nos servirá para Ranking en ESCALERILLA.
   */
  {
    path:
      'competitions/:competitionId/categories/:competitionCategoryId/matches',
    component:
      CompetitionCategoryDetailComponent,
    data: {
      ladderMatchManagement: true,
    },
    canActivate: [managementGuard],
  },

  // =====================================================
  // ORGANIZERS (SOLO ADMINISTRADOR)
  // =====================================================

  {
    path: 'organizers',
    component: OrganizerListComponent,
    canActivate: [adminGuard],
  },
  {
    path: 'organizers/new',
    component: OrganizerFormComponent,
    canActivate: [adminGuard],
  },
  {
    path: 'organizers/:id/edit',
    component: OrganizerFormComponent,
    canActivate: [adminGuard],
  },

  {
    path:
      'competitions/:competitionId/categories/:competitionCategoryId',

    component:
      CompetitionCategoryDetailComponent,

    canActivate: [
      authGuard,
    ],
  },


  // =====================================================
  // PLAYERS
  // =====================================================

  {
    path: 'players',
    component: PlayerListComponent,
    canActivate: [
      authGuard,
    ],
  },

  {
    path: 'players/new',
    component: PlayerFormComponent,
    canActivate: [managementGuard],
  },

  {
    path: 'players/:id/edit',
    component: PlayerFormComponent,
    canActivate: [managementGuard],
  },


  // =====================================================
  // REGISTRATIONS
  // =====================================================

  {
    path: 'registrations',
    component: RegistrationListComponent,
    canActivate: [
      adminGuard,
    ],
  },

  {
    path: 'registrations/new',
    component: RegistrationFormComponent,
    canActivate: [managementGuard],
  },

  {
    path: 'registrations/:id/edit',
    component: RegistrationFormComponent,
    canActivate: [managementGuard],
  },


  // =====================================================
  // MATCHES
  // =====================================================

  {
    path: 'matches',
    component: MatchListComponent,
    canActivate: [
      adminGuard,
    ],
  },

  {
    path: 'matches/new',
    component: MatchFormComponent,
    canActivate: [managementGuard],
  },

  {
    path: 'matches/:id/edit',
    component: MatchFormComponent,
    canActivate: [managementGuard],
  },

  {
    path: 'matches/:id/result',
    component: MatchResultComponent,
    canActivate: [managementGuard],
  },

];
