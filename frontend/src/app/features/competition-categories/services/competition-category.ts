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
  CompetitionCategory,
  CreateCompetitionCategoryRequest,
  UpdateCompetitionCategoryRequest,
  BracketResponse,
  GenerateBracketResponse,
} from '../models/competition-category.model';

export interface Category {
  id: number;
  name: string;
}

@Injectable({
  providedIn: 'root',
})
export class CompetitionCategoryService {

  private readonly http = inject(
    HttpClient
  );

  private readonly competitionCategoriesUrl =
    `${environment.apiUrl}/competition-categories`;

  private readonly categoriesUrl =
    `${environment.apiUrl}/categories`;

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

    return this.http.get<
      CompetitionCategory
    >(
      `${this.competitionCategoriesUrl}/${id}/`
    );
  }

  createCompetitionCategory(
    data: CreateCompetitionCategoryRequest
  ): Observable<CompetitionCategory> {

    return this.http.post<
      CompetitionCategory
    >(
      `${this.competitionCategoriesUrl}/`,
      data
    );
  }

  updateCompetitionCategory(
    id: number,
    data: UpdateCompetitionCategoryRequest
  ): Observable<CompetitionCategory> {

    return this.http.patch<
      CompetitionCategory
    >(
      `${this.competitionCategoriesUrl}/${id}/`,
      data
    );
  }

  deleteCompetitionCategory(
    id: number
  ): Observable<void> {

    return this.http.delete<void>(
      `${this.competitionCategoriesUrl}/${id}/`
    );
  }

  // =====================================================
  // CATEGORIES
  // =====================================================

  getCategories():
    Observable<Category[]> {

    return this.http.get<
      Category[]
    >(
      `${this.categoriesUrl}/`
    );
  }

  // =====================================================
  // BRACKET
  // =====================================================

  getBracket(
    competitionCategoryId: number
  ): Observable<BracketResponse> {

    return this.http.get<
      BracketResponse
    >(
      `${this.competitionCategoriesUrl}/` +
      `${competitionCategoryId}/bracket/`
    );
  }

  generateBracket(
    competitionCategoryId: number
  ): Observable<GenerateBracketResponse> {

    return this.http.post<
      GenerateBracketResponse
    >(
      `${this.competitionCategoriesUrl}/` +
      `${competitionCategoryId}/generate-bracket/`,
      {}
    );
  }
}