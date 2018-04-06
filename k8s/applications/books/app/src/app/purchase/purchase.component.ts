import {Component, OnInit, Input} from '@angular/core';
import {Purchase, Book} from '../externs';
import {ShelvesService} from '../shelves/shelves.service';

@Component({
  selector: 'purchase',
  templateUrl: './purchase.component.html',
  styleUrls: ['./purchase.component.css']
})
export class PurchaseComponent implements OnInit {

  book: Book;

  constructor(private shelvesService: ShelvesService) { }

  ngOnInit() {
    this.book = null;
    this.shelvesService.getBook(this.purchase.book).then(book => {
      this.book = book;
    })
  }

  @Input() purchase: Purchase;
}
