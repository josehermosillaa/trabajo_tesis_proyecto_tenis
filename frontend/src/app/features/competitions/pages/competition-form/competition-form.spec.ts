import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';

import { TokenService } from '../../../../core/services/token';
import { CompetitionCategoryService } from '../../../competition-categories/services/competition-category';
import { CompetitionService } from '../../services/competition';
import { CompetitionFormComponent } from './competition-form';

describe('CompetitionFormComponent navigation', () => {
  let component: CompetitionFormComponent;
  let fixture: ComponentFixture<CompetitionFormComponent>;
  let router: jasmine.SpyObj<Router>;
  let routeId: string | null;

  beforeEach(async () => {
    routeId = null;
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);

    const competitionService = jasmine.createSpyObj<CompetitionService>(
      'CompetitionService',
      ['getCompetition']
    );
    competitionService.getCompetition.and.returnValue(of({
      id: 5,
      name: 'Torneo',
      type: 'ELIMINACION_DIRECTA',
      start_date: '2026-09-01',
      end_date: '2026-09-15',
      status: 'PENDIENTE',
      registration_deadline: '2026-08-25',
    }));

    const categoryService = jasmine.createSpyObj<CompetitionCategoryService>(
      'CompetitionCategoryService',
      ['getCategories', 'getCompetitionCategories']
    );
    categoryService.getCategories.and.returnValue(of([]));
    categoryService.getCompetitionCategories.and.returnValue(of([]));

    const tokenService = jasmine.createSpyObj<TokenService>(
      'TokenService',
      ['isAdministrativeUser']
    );
    tokenService.isAdministrativeUser.and.returnValue(true);

    await TestBed.configureTestingModule({
      imports: [CompetitionFormComponent],
      providers: [
        { provide: CompetitionService, useValue: competitionService },
        { provide: CompetitionCategoryService, useValue: categoryService },
        { provide: TokenService, useValue: tokenService },
        { provide: Router, useValue: router },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) => key === 'id' ? routeId : null,
              },
            },
          },
        },
      ],
    }).compileComponents();
  });

  it('returns to the same competition detail after a successful update', () => {
    createComponent('5');

    completeUpdate();

    expect(router.navigate).toHaveBeenCalledWith(
      ['/competitions', 5, 'categories'],
      {
        state: {
          successMessage: 'Competencia actualizada correctamente.',
        },
      }
    );
  });

  it('returns to the same competition detail when cancelling an edit', () => {
    createComponent('5');

    component.cancel();

    expect(router.navigate).toHaveBeenCalledWith([
      '/competitions',
      5,
      'categories',
    ]);
  });

  it('keeps the competition list destination after successful creation', () => {
    createComponent(null);

    completeCreation();

    expect(router.navigate).toHaveBeenCalledWith(
      ['/competitions'],
      {
        state: {
          successMessage: 'Competencia creada correctamente.',
        },
      }
    );
  });

  it('keeps the competition list destination when cancelling creation', () => {
    createComponent(null);

    component.cancel();

    expect(router.navigate).toHaveBeenCalledWith(['/competitions']);
  });

  function createComponent(id: string | null): void {
    routeId = id;
    fixture = TestBed.createComponent(CompetitionFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  function completeUpdate(): void {
    const target = component as unknown as {
      updateNextCategory(requests: never[], index: number): void;
    };
    target.updateNextCategory([], 0);
  }

  function completeCreation(): void {
    const target = component as unknown as {
      createNextCategory(requests: never[], index: number): void;
    };
    target.createNextCategory([], 0);
  }
});
