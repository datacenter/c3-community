import { TestBed, inject } from '@angular/core/testing';
import { PurchasesService } from './purchases.service';

describe('PurchasesService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [PurchasesService]
    });
  });

  it('should ...', inject([PurchasesService], (service: PurchasesService) => {
    expect(service).toBeTruthy();
  }));
});
