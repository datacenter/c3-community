


export declare class Shelf {
  public id: number;
  public theme: string;
}

export declare class Shelves {
  public shelves: Array<Shelf>;
}

export declare class Book {
  public id: number;
  public shelf: number;
  public theme: string;
  public author: string;
  public description: string;
  public title: string;
}

export declare class Books {
  public books: Array<Book>;
}

export declare class User {
  public name: string;
  public id: number;
}

export declare class Purchase {
  public id: number;
  public book: number;
  public user: number;
}

export declare class Purchases {
  public purchases: Array<Purchase>;
}
