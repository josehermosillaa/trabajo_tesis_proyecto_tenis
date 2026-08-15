import { TestBed } from '@angular/core/testing';

import { Competition } from './competition';

describe('Competition', () => {
  let service: Competition;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Competition);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
