import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';


export interface Movie {
  title: string
  year: number
  studio: string
  director: string
}

@Injectable({
  providedIn: 'root'
})
export class MoviesService {

  constructor(private http: HttpClient) { }
  
  getAll(): Observable<Movie[]> {
    return this.http.get<Movie[]>('/api/movies');
  }

}
