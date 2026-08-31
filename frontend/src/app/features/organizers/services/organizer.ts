import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import {
  CreateOrganizerRequest,
  Organizer,
  UpdateOrganizerRequest,
} from '../models/organizer.model';

@Injectable({ providedIn: 'root' })
export class OrganizerService {
  private readonly http = inject(HttpClient);
  private readonly url = `${environment.apiUrl}/organizers`;

  getOrganizers(): Observable<Organizer[]> {
    return this.http.get<Organizer[]>(`${this.url}/`);
  }

  getOrganizer(id: number): Observable<Organizer> {
    return this.http.get<Organizer>(`${this.url}/${id}/`);
  }

  createOrganizer(request: CreateOrganizerRequest): Observable<Organizer> {
    return this.http.post<Organizer>(`${this.url}/`, request);
  }

  updateOrganizer(id: number, request: UpdateOrganizerRequest): Observable<Organizer> {
    return this.http.patch<Organizer>(`${this.url}/${id}/`, request);
  }

  setOrganizerActive(id: number, active: boolean): Observable<Organizer> {
    return this.http.post<Organizer>(`${this.url}/${id}/set-active/`, { active });
  }
}
