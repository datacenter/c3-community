import { TestBed, inject } from '@angular/core/testing';
import { ShelvesService } from './shelves.service';

describe('ShelvesService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ShelvesService]
    });
  });

  it('should ...', inject([ShelvesService], (service: ShelvesService) => {
    expect(service).toBeTruthy();
  }));
});
