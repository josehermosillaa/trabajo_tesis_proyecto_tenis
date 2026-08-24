import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';

import {
  Player,
  CreatePlayerRequest,
  UpdatePlayerRequest,
} from '../models/player.model';

export interface Category {
  id: number;
  name: string;
}

@Injectable({
  providedIn: 'root',
})
export class PlayerService {
  private readonly http = inject(HttpClient);

  private readonly playersUrl =
    `${environment.apiUrl}/players`;

  private readonly categoriesUrl =
    `${environment.apiUrl}/categories`;

  getPlayers(): Observable<Player[]> {
    return this.http.get<Player[]>(
      `${this.playersUrl}/`
    );
  }

  getPlayer(id: number): Observable<Player> {
    return this.http.get<Player>(
      `${this.playersUrl}/${id}/`
    );
  }

  createPlayer(
    player: CreatePlayerRequest
  ): Observable<Player> {
    return this.http.post<Player>(
      `${this.playersUrl}/`,
      player
    );
  }

  updatePlayer(
    id: number,
    player: UpdatePlayerRequest
  ): Observable<Player> {
    return this.http.patch<Player>(
      `${this.playersUrl}/${id}/`,
      player
    );
  }

  deletePlayer(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.playersUrl}/${id}/`
    );
  }

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(
      `${this.categoriesUrl}/`
    );
  }
}