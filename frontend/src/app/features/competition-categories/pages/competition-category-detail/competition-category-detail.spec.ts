import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CompetitionCategoryDetail } from './competition-category-detail';

describe('CompetitionCategoryDetail', () => {
  let component: CompetitionCategoryDetail;
  let fixture: ComponentFixture<CompetitionCategoryDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CompetitionCategoryDetail]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CompetitionCategoryDetail);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
