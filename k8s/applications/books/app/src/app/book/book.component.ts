import { Component, Input, OnInit } from '@angular/core';
import { Book, Shelf } from '../externs';
import {UsersService} from '../users/users.service';
import {PurchasesService} from '../purchases/purchases.service';

@Component({
  selector: 'book',
  templateUrl: './book.component.html',
  styleUrls: ['./book.component.css']
})
export class BookComponent implements OnInit {
  private isPurchased_: boolean;

  constructor(private usersService: UsersService, private purchasesService: PurchasesService) { }

  ngOnInit() {
    this.isPurchased_ = false;
    this.purchasesService.isPurchased(
      this.usersService.getCurrentUser(), this.book).then( isPurchased => {
        this.isPurchased_ = isPurchased;
    })
  }

  isPurchased(): boolean{
    return this.isPurchased_;
  }

  purchaseBook() {
    this.purchasesService.purchaseBook(this.usersService.getCurrentUser(), this.book);
  }

  @Input() book: Book;
  @Input() shelf: Shelf;
}
