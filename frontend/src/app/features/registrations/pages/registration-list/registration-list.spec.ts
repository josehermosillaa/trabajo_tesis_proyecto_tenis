import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RegistrationList } from './registration-list';

describe('RegistrationList', () => {
  let component: RegistrationList;
  let fixture: ComponentFixture<RegistrationList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegistrationList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RegistrationList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
