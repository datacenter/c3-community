import { Injectable } from '@angular/core';
import {Http} from '@angular/http';
import {Purchases, User, Purchase, Book} from '../externs';


@Injectable()
export class PurchasesService {
  private allPurchases: Promise<Purchases>;

  constructor(private http: Http) {
    this.allPurchases = this.http.get('/purchases')
      .toPromise()
      .then(response => JSON.parse(response.json()))
      .then(({purchases}) => {
        purchases.forEach(purchase => {
          let userId = purchase.user.match(/http:\/\/.*:\d\d\d\d\/users\/(\d+)/)[1];
          purchase.user = parseInt(userId);
          let bookId = purchase.book.match(/http:\/\/.*:\d\d\d\d\/shelves\/\d+\/books\/(\d+)/)[1];
          purchase.book = parseInt(bookId);
        });
        return {purchases};
      });
  }

  getAllPurchases(): Promise<Purchases>{
    return this.allPurchases;
  }

  getAllPurchasesForUser(user: User | Promise<User>): Promise<Array<Purchase>>{
    let promiseAll = Promise.all([Promise.resolve(user), this.getAllPurchases()]) as Promise<[User, Purchases]>;
    return promiseAll.then(
        ([user, {purchases}]) =>
            purchases.filter(purchase => purchase.user === user.id));
  }

  purchaseBook(user: User | Promise<User>, book: Book | Promise<Book>) {
    let promiseAll = Promise.all([
      Promise.resolve(user), Promise.resolve(book)]) as Promise<[User, Book]>;
    promiseAll.then(([user, book]) => {
      let postBody = {book: `/shelves/${book.shelf}/books/${book.id}`, user: `/users/${user.id}`}
      this.http.post('/purchases', postBody).toPromise().then((response) => {
        window.location.reload();
      })
    });
  }

  isPurchased(user: User | Promise<User>, book: Book | Promise<Book>): Promise<boolean> {
    let promiseAll = Promise.all([
      Promise.resolve(user), Promise.resolve(book), this.allPurchases
    ]) as Promise<[User, Book, Purchases]>;
    return promiseAll.then(
        ([user, book, {purchases}]) => !!purchases.find(
            purchase =>
                purchase.book === book.id && purchase.user === user.id));
  }
}
