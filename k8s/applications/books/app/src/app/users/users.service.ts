import { Injectable } from '@angular/core';
import {User} from '../externs';
import {Http} from '@angular/http';

@Injectable()
export class UsersService {
  private currentUser: Promise<User>;

  constructor(private http: Http) {
    this.currentUser = this.http.get('users/1').toPromise().then(
      response => JSON.parse(response.json()));
  }

  getCurrentUser(): Promise<User> {
    return this.currentUser;
  }
}
