import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CompetitionCategoryList } from './competition-category-list';

describe('CompetitionCategoryList', () => {
  let component: CompetitionCategoryList;
  let fixture: ComponentFixture<CompetitionCategoryList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CompetitionCategoryList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CompetitionCategoryList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
