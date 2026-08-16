import { TestBed } from '@angular/core/testing';

import { CompetitionCategory } from './competition-category';

describe('CompetitionCategory', () => {
  let service: CompetitionCategory;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CompetitionCategory);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
