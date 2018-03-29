import { Component, Input, Output, OnInit } from '@angular/core';
import {ShelvesService} from '../shelves/shelves.service';
import {Book, Shelf} from '../externs';

@Component({
  selector: 'book-list',
  templateUrl: './book-list.component.html',
  styleUrls: ['./book-list.component.css']
})
export class BookListComponent implements OnInit {

  books: Array<Book>;
  shelves: Array<Shelf>;

  constructor(private shelvesService: ShelvesService) { }

  ngOnInit() {
    this.books = [];
    this.shelves = [];

    this.shelvesService.getAllBooksAndShelves().then(({shelves, books}) => {
      this.books = books;
      this.shelves = shelves;
    });
  }

  getShelfForBook(book){
    return this.shelves.find(shelf => shelf.id === book.shelf);
  }

}
