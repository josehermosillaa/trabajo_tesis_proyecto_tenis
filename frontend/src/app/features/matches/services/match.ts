import {
  Injectable,
  inject,
} from '@angular/core';

import {
  HttpClient,
} from '@angular/common/http';

import {
  Observable,
} from 'rxjs';

import {
  environment,
} from '../../../../environments/environment';

import {
  Match,
  CreateMatchRequest,
  UpdateMatchRequest,
  ResolveMatchRequest
} from '../models/match.model';

import {
  MatchSet,
  CreateMatchSetRequest,
  UpdateMatchSetRequest,
} from '../models/match-set.model';

import {
  Competition,
} from '../../registrations/models/registration.model';

import {
  CompetitionCategory,
} from '../../competition-categories/models/competition-category.model';

import {
  Category,
} from '../../competition-categories/services/competition-category';

import {
  Player,
} from '../../players/models/player.model';


export interface Court {
  id: number;

  name: string;

  status:
    | 'AVAILABLE'
    | 'OCCUPIED'
    | 'MAINTENANCE';
}


@Injectable({
  providedIn: 'root',
})
export class MatchService {

  private readonly http =
    inject(HttpClient);


  // =====================================================
  // ENDPOINTS
  // =====================================================

  private readonly matchesUrl =
    `${environment.apiUrl}/matches`;

  private readonly matchSetsUrl =
    `${environment.apiUrl}/match-sets`;

  private readonly competitionsUrl =
    `${environment.apiUrl}/competitions`;

  private readonly competitionCategoriesUrl =
    `${environment.apiUrl}/competition-categories`;

  private readonly categoriesUrl =
    `${environment.apiUrl}/categories`;

  private readonly playersUrl =
    `${environment.apiUrl}/players`;

  private readonly courtsUrl =
    `${environment.apiUrl}/courts`;


  // =====================================================
  // MATCH
  // =====================================================

  getMatches():
    Observable<Match[]> {

    return this.http.get<Match[]>(
      `${this.matchesUrl}/`
    );
  }


  getMatch(
    id: number
  ): Observable<Match> {

    return this.http.get<Match>(
      `${this.matchesUrl}/${id}/`
    );
  }


  createMatch(
    data: CreateMatchRequest
  ): Observable<Match> {

    return this.http.post<Match>(
      `${this.matchesUrl}/`,
      data
    );
  }


  updateMatch(
    id: number,
    data: UpdateMatchRequest
  ): Observable<Match> {

    return this.http.patch<Match>(
      `${this.matchesUrl}/${id}/`,
      data
    );
  }


  deleteMatch(
    id: number
  ): Observable<void> {

    return this.http.delete<void>(
      `${this.matchesUrl}/${id}/`
    );
  }

    // =====================================================
  // RESOLUCIÓN DE PARTIDO
  // =====================================================

  walkover(
    id: number,
    data: ResolveMatchRequest
  ): Observable<Match> {

    return this.http.post<Match>(
      `${this.matchesUrl}/${id}/walkover/`,
      data
    );
  }


  retirement(
    id: number,
    data: ResolveMatchRequest
  ): Observable<Match> {

    return this.http.post<Match>(
      `${this.matchesUrl}/${id}/retirement/`,
      data
    );
  }
  resetResolution(id: number): Observable<Match> {
  return this.http.post<Match>(
    `${this.matchesUrl}/${id}/reset-resolution/`,
    {}
  );
}


  // =====================================================
  // MATCH SET
  // =====================================================

  getMatchSets():
    Observable<MatchSet[]> {

    return this.http.get<MatchSet[]>(
      `${this.matchSetsUrl}/`
    );
  }


  getMatchSet(
    id: number
  ): Observable<MatchSet> {

    return this.http.get<MatchSet>(
      `${this.matchSetsUrl}/${id}/`
    );
  }


  createMatchSet(
    data: CreateMatchSetRequest
  ): Observable<MatchSet> {

    return this.http.post<MatchSet>(
      `${this.matchSetsUrl}/`,
      data
    );
  }


  updateMatchSet(
    id: number,
    data: UpdateMatchSetRequest
  ): Observable<MatchSet> {

    return this.http.patch<MatchSet>(
      `${this.matchSetsUrl}/${id}/`,
      data
    );
  }


  deleteMatchSet(
    id: number
  ): Observable<void> {

    return this.http.delete<void>(
      `${this.matchSetsUrl}/${id}/`
    );
  }


  // =====================================================
  // COMPETITIONS
  // =====================================================

  getCompetitions():
    Observable<Competition[]> {

    return this.http.get<Competition[]>(
      `${this.competitionsUrl}/`
    );
  }


  // =====================================================
  // COMPETITION CATEGORIES
  // =====================================================

  getCompetitionCategories():
    Observable<CompetitionCategory[]> {

    return this.http.get<
      CompetitionCategory[]
    >(
      `${this.competitionCategoriesUrl}/`
    );
  }


  getCompetitionCategory(
    id: number
  ): Observable<CompetitionCategory> {

    return this.http.get<CompetitionCategory>(
      `${this.competitionCategoriesUrl}/${id}/`
    );
  }


  // =====================================================
  // CATEGORIES
  // =====================================================

  getCategories():
    Observable<Category[]> {

    return this.http.get<Category[]>(
      `${this.categoriesUrl}/`
    );
  }


  // =====================================================
  // PLAYERS
  // =====================================================

  getPlayers():
    Observable<Player[]> {

    return this.http.get<Player[]>(
      `${this.playersUrl}/`
    );
  }


  getPlayer(
    id: number
  ): Observable<Player> {

    return this.http.get<Player>(
      `${this.playersUrl}/${id}/`
    );
  }


  // =====================================================
  // COURTS
  // =====================================================

  getCourts():
    Observable<Court[]> {

    return this.http.get<Court[]>(
      `${this.courtsUrl}/`
    );
  }


  getCourt(
    id: number
  ): Observable<Court> {

    return this.http.get<Court>(
      `${this.courtsUrl}/${id}/`
    );
  }
}