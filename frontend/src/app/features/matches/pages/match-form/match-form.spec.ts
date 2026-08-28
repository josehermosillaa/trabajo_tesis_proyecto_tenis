import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MatchForm } from './match-form';

describe('MatchForm', () => {
  let component: MatchForm;
  let fixture: ComponentFixture<MatchForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatchForm]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MatchForm);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
