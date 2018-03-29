import { Component, OnInit } from '@angular/core';
import {UsersService} from '../users/users.service';
import {User, Purchase} from '../externs';
import {PurchasesService} from '../purchases/purchases.service';

@Component({
  selector: 'purchase-list',
  templateUrl: './purchase-list.component.html',
  styleUrls: ['./purchase-list.component.css']
})
export class PurchaseListComponent implements OnInit {

  public user: User;
  public purchases: Array<Purchase>;

  constructor(private usersService: UsersService, private purchasesService: PurchasesService) { }

  ngOnInit() {
    this.user = null;
    this.purchases = [];
    let userPromise = this.usersService.getCurrentUser();
    userPromise.then(user => {this.user = user;});
    this.purchasesService.getAllPurchasesForUser(userPromise).then(purchases => {this.purchases = purchases;});
  }
}
