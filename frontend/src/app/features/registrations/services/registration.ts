import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';

import {
  Registration,
  CreateRegistrationRequest,
  UpdateRegistrationRequest,
  CompetitionCategory,
  Competition,
} from '../models/registration.model';

import { Player } from '../../players/models/player.model';

export interface Category {
  id: number;
  name: string;
}

@Injectable({
  providedIn: 'root',
})
export class RegistrationService {

  private readonly http = inject(HttpClient);

  private readonly registrationsUrl =
    `${environment.apiUrl}/registrations`;

  private readonly competitionsUrl =
    `${environment.apiUrl}/competitions`;

  private readonly competitionCategoriesUrl =
    `${environment.apiUrl}/competition-categories`;

  private readonly playersUrl =
    `${environment.apiUrl}/players`;

  private readonly categoriesUrl =
    `${environment.apiUrl}/categories`;

  getRegistrations(): Observable<Registration[]> {
    return this.http.get<Registration[]>(
      `${this.registrationsUrl}/`
    );
  }

  getRegistration(
    id: number
  ): Observable<Registration> {
    return this.http.get<Registration>(
      `${this.registrationsUrl}/${id}/`
    );
  }

  createRegistration(
    registration: CreateRegistrationRequest
  ): Observable<Registration> {
    return this.http.post<Registration>(
      `${this.registrationsUrl}/`,
      registration
    );
  }

  updateRegistration(
    id: number,
    registration: UpdateRegistrationRequest
  ): Observable<Registration> {
    return this.http.patch<Registration>(
      `${this.registrationsUrl}/${id}/`,
      registration
    );
  }

  deleteRegistration(
    id: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.registrationsUrl}/${id}/`
    );
  }

  getCompetitions(): Observable<Competition[]> {
    return this.http.get<Competition[]>(
      `${this.competitionsUrl}/`
    );
  }

  getCompetitionCategories():
    Observable<CompetitionCategory[]> {

    return this.http.get<CompetitionCategory[]>(
      `${this.competitionCategoriesUrl}/`
    );
  }

  getPlayers(): Observable<Player[]> {
    return this.http.get<Player[]>(
      `${this.playersUrl}/`
    );
  }

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(
      `${this.categoriesUrl}/`
    );
  }
}