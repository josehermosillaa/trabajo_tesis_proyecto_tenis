import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { CompetitionCategory, 
        CreateCompetitionCategoryRequest,
        UpdateCompetitionCategoryRequest } from '../models/competition-category.model';



export interface Category {
  id: number;
  name: string;
}

@Injectable({
  providedIn: 'root',
})
export class CompetitionCategoryService {
  private readonly http = inject(HttpClient);

  private readonly competitionCategoriesUrl =
    `${environment.apiUrl}/competition-categories`;

  private readonly categoriesUrl =
    `${environment.apiUrl}/categories`;

  getCompetitionCategories(): Observable<CompetitionCategory[]> {
    return this.http.get<CompetitionCategory[]>(
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

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(
      `${this.categoriesUrl}/`
    );
  }

 createCompetitionCategory(
  data: CreateCompetitionCategoryRequest
): Observable<CompetitionCategory> {

  return this.http.post<CompetitionCategory>(
    `${this.competitionCategoriesUrl}/`,
    data
  );
}

  updateCompetitionCategory(
    id: number,
    data: UpdateCompetitionCategoryRequest
  ): Observable<CompetitionCategory> {

    return this.http.patch<CompetitionCategory>(
      `${this.competitionCategoriesUrl}/${id}/`,
      data
    );
  }
}