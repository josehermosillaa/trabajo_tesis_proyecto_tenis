import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

import {
  Category,
  CompetitionCategoryService,
} from '../../services/competition-category';

import { CompetitionCategory } from '../../models/competition-category.model';

@Component({
  selector: 'app-competition-category-list',
  imports: [CommonModule],
  templateUrl: './competition-category-list.html',
  styleUrl: './competition-category-list.scss',
})
export class CompetitionCategoryListComponent implements OnInit {
  private readonly competitionCategoryService = inject(
    CompetitionCategoryService
  );

  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  competitionId: number | null = null;

  competitionCategories: CompetitionCategory[] = [];
  categories: Category[] = [];

  loading = false;
  errorMessage = '';

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');

    if (!id) {
      this.errorMessage =
        'No se especificó la competencia.';

      return;
    }

    this.competitionId = Number(id);

    this.loadData();
  }

  loadData(): void {
    if (this.competitionId === null) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.competitionCategoryService
      .getCompetitionCategories()
      .subscribe({
        next: (competitionCategories) => {
          this.competitionCategories =
            competitionCategories.filter(
              (item) =>
                item.competition === this.competitionId
            );

          this.loadCategories();
        },
        error: (error) => {
          console.error(
            'Error al cargar categorías de competencia:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las categorías.';

          this.loading = false;
        },
      });
  }

  private loadCategories(): void {
    this.competitionCategoryService
      .getCategories()
      .subscribe({
        next: (categories) => {
          this.categories = categories;
          this.loading = false;
        },
        error: (error) => {
          console.error(
            'Error al cargar categorías:',
            error
          );

          this.errorMessage =
            'No fue posible cargar las categorías.';

          this.loading = false;
        },
      });
  }

  getCategoryName(categoryId: number): string {
    const category = this.categories.find(
      (item) => item.id === categoryId
    );

    return category?.name ?? `Categoría ${categoryId}`;
  }

  goBack(): void {
    this.router.navigate(['/competitions']);
  }

  goToEdit(id: number): void {
    this.router.navigate([
      '/competitions',
      this.competitionId,
      'categories',
      id,
      'edit',
    ]);
  }
}