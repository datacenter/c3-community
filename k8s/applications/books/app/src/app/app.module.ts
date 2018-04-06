import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { MaterialModule } from '@angular/material';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { BookListComponent } from './book-list/book-list.component';
import { PurchaseListComponent } from './purchase-list/purchase-list.component';
import { BookComponent } from './book/book.component';
import { ShelvesService } from './shelves/shelves.service';
import {PurchasesService} from './purchases/purchases.service';
import {UsersService} from './users/users.service';
import { PurchaseComponent } from './purchase/purchase.component';

@NgModule({
  declarations: [
    AppComponent,
    BookListComponent,
    PurchaseListComponent,
    BookComponent,
    PurchaseComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    HttpModule,
    MaterialModule,
  ],
  providers: [ShelvesService, UsersService, PurchasesService],
  bootstrap: [AppComponent]
})
export class AppModule { }
