import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { HealthResponse } from '../models/health-response.model';

@Injectable({
  providedIn: 'root',
})
export class HealthService {

  private http = inject(HttpClient);

  private apiUrl = `${environment.apiUrl}/health/`;

  getHealth(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(this.apiUrl);
  }

}