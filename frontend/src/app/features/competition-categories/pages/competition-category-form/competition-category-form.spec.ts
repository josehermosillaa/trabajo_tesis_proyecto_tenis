import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CompetitionCategoryForm } from './competition-category-form';

describe('CompetitionCategoryForm', () => {
  let component: CompetitionCategoryForm;
  let fixture: ComponentFixture<CompetitionCategoryForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CompetitionCategoryForm]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CompetitionCategoryForm);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
