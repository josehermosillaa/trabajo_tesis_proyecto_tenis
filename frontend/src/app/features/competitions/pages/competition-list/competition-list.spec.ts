import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CompetitionList } from './competition-list';

describe('CompetitionList', () => {
  let component: CompetitionList;
  let fixture: ComponentFixture<CompetitionList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CompetitionList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CompetitionList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
