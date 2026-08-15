import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { Competition } from '../models/competition.model';

@Injectable({
  providedIn: 'root',
})
export class CompetitionService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl = `${environment.apiUrl}/competitions`;

  getCompetitions(): Observable<Competition[]> {
    return this.http.get<Competition[]>(`${this.apiUrl}/`);
  }

  getCompetition(id: number): Observable<Competition> {
    return this.http.get<Competition>(
      `${this.apiUrl}/${id}/`
    );
  }

  createCompetition(
    competition: Omit<Competition, 'id'>
  ): Observable<Competition> {
    return this.http.post<Competition>(
      `${this.apiUrl}/`,
      competition
    );
  }

  updateCompetition(
    id: number,
    competition: Omit<Competition, 'id'>
  ): Observable<Competition> {
    return this.http.patch<Competition>(
      `${this.apiUrl}/${id}/`,
      competition
    );
  }
  deleteCompetition(id: number): Observable<void> {
  return this.http.delete<void>(
    `${this.apiUrl}/${id}/`
  );
}
}