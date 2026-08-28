import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MatchResult } from './match-result';

describe('MatchResult', () => {
  let component: MatchResult;
  let fixture: ComponentFixture<MatchResult>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatchResult]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MatchResult);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
