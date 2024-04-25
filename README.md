# Python + Angular

It's a simple full stack project with Angular frontend and Python backend.

[Live demo](https://ap-basic-fnobcck2ma-ew.a.run.app/)

## Create directory and standard projects

Create parent folder for both projects.

```bash
mkdir my_project
cd my_project
```

### Frontend - Angular + Material

Create Angular project with Material library.

```bash
ng new frontend --routing
cd frontend
ng add @angular/material
cd ..
```

You can run it.

```bash
cd frontend
ng serve --open
cd ..
```

Default web browser will open automatically and you see
Angular Hello page.

### Backend - Python + FastAPI

Create Python project with FastAPI library.

```bash
mkdir backend
cd backend
python -m venv .env
.env\Scripts\activate
python -m pip install --upgrade pip
pip install "fastapi[all]"
pip install "uvicorn[standard]"
pip install gunicorn
cd ..
```

Create `main.py` file with simple API endpoints.

```python
from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/api")
async def read_root():
    return {"Hello": "World"}


@app.get("/api/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

You can run it.

```bash
cd backend
uvicorn main:app --reload
cd ..
```

Now you can go to <http://127.0.0.1:8000/api> to see results
You will see automatic documentation here: <http://127.0.0.1:8000/docs>
or <http://127.0.0.1:8000/redoc>.

## Serve Angular files by Python

You can compile Angular part you can build with command:

```bash
cd frontend
ng build
```

Compiled files will be written in `frontend/dist/frontend`.
Let's copy them to `backend/static`.

```bash
cp -r frontend/dist/frontend/* backend/static/
```

Set python to serve these files - modify `main.py`.

```python
from static_files import static_file_response

# Angular static files - it have to be at the end of file
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(_: Request, full_path: str):
    return static_file_response("static/browser", full_path)
```

Add `static_files.py` where Angular startic files are served.
It adds proper `Content-Type` header and returns main `index.html`
if URL path does'n exists.

```python
"""This module provides a function to return static files or index.html from a base directory."""

import os
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import HTMLResponse


def static_file_response(base_dir: str, uri_path: str) -> HTMLResponse:
    """Return a static files (if exists) or index.html (if exists) from the base_dir"""
    file_path = Path(base_dir) / uri_path
    if file_path.exists() and file_path.is_file():
        return HTMLResponse(
            content=get_file_content(file_path),
            status_code=200,
            headers=get_file_headers(file_path),
        )
    index_path = Path(base_dir) / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Page not found")
    return HTMLResponse(content=index_path.read_text(), status_code=200)


def get_file_content(file_path: Path):
    """Return the file content"""
    file_extension = os.path.splitext(file_path)[1]
    if file_extension in [
        ".js",
        ".css",
        ".html",
        ".json",
        ".yaml",
        ".yml",
        ".xml",
        ".csv",
        ".txt",
    ]:
        return file_path.read_text()
    else:
        return file_path.read_bytes()


def get_file_headers(file_path: Path) -> dict[str, str]:
    """Return the file headers (Content-Type) based on the file extension"""
    file_extension = os.path.splitext(file_path)[1]
    match file_extension:
        case ".js":
            media_type = "text/javascript"
        case ".css":
            media_type = "text/css"
        case ".ico":
            media_type = "image/x-icon"
        case ".png":
            media_type = "image/png"
        case ".jpg":
            media_type = "image/jpeg"
        case ".jpeg":
            media_type = "image/jpeg"
        case ".svg":
            media_type = "image/svg+xml"
        case _:
            media_type = "text/html"
    return {"Content-Type": media_type}
```

If `unicorn` still running at <http://127.0.0.1:8000/> you see Angular default page.

## Dockerize it all

Create `requirements.txt` file for python:

```bash
cd backend
pip freeze > requirements.txt
cd ..
```

Create multistaging `Dockerfile` where in first stage is Angular project built
and the ditribution files is copied to Python project and then the final image
is built.

```Dockerfile
# ------ Stage 1: Angular project ------
    FROM node:20 AS angular-build
    WORKDIR /app

    COPY frontend/package.json frontend/package-lock.json ./
    RUN npm install
    
    COPY frontend/ .
    RUN npm run build
    
# ------ Stage 2: Python/FastAPI project ------
    FROM python:3.11.7-slim
    WORKDIR /app
    
    # Keeps Python from generating .pyc files in the container
    ENV PYTHONDONTWRITEBYTECODE=1
    # Turns off buffering for easier container logging
    ENV PYTHONUNBUFFERED=1
    RUN python -m pip install --upgrade pip
    # Install pip requirements
    COPY backend/requirements.txt .
    RUN python -m pip install -r requirements.txt
    
    COPY ./backend/ /app
    # Copy Angular build to FastAPI static folder
    COPY --from=angular-build /app/dist/frontend /app/static
    
    # Creates a non-root user with an explicit UID and adds permission to access the /app folder
    # For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
    RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
    USER appuser
    # During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
    EXPOSE 8080
    CMD ["gunicorn", "--bind", "0.0.0.0:8080", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
```

And standard `.dockerignore` file.

```text
**/__pycache__
**/.venv
**/.classpath
**/.dockerignore
**/.env
**/.git
**/.gitignore
**/.project
**/.settings
**/.toolstarget
**/.vs
**/.vscode
**/*.*proj.user
**/*.dbmdl
**/*.jfm
**/bin
**/charts
**/docker-compose*
**/compose*
**/Dockerfile*
**/node_modules
**/npm-debug.log
**/obj
**/secrets.dev.yaml
**/values.dev.yaml
LICENSE
README.md
```

Build docker image.

```bash
docker build -t leliw/ap-basic .
```

Then run built image.

```bash
docker run -p 8080:8080 leliw/ap-basic
```

Go <http://localhost:8080/>.

### Build docker image with Github Action

Create `.github\workflows\main.yaml` with content:

```yaml
name: CI

on:
  push:
    branches:
      - main
      - release/*
  pull_request:
    branches:
      - main
  
jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.19'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Build frontend
        run: |
          cd frontend
          npm run build
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          context: .
          tags:  ghcr.io/${{ github.repository }}:latest
```

It's run someone push changes into `main` or `release/*` branch or
make pull request. It:

- checkout source from git
- setup node version
- install dependencies (in frontend directory)
- build Angular part (in frontend directory)
- build docker image (where pip modules are istalled)
- push this image into GitHub Packages (ghcr.io)

Now you can pull and run this image:

```bash
docker pull ghcr.io/leliw/ap-basic:latest
docker run -p 8000:8000 ghcr.io/leliw/ap-basic:latest
```

## Run in development environment

Create a file `frontend/src/proxy.conf.json`.
Mind that `localhost` and `127.0.0.1` is not the same
in Node v. 17 (see: <https://angular.io/guide/build>).

```json
{
    "/api": {
        "target": "http://127.0.0.1:8000",
        "secure": false,
        "changeOrigin": true,
        "logLevel": "debug"
    }
}
```

Run backend in one terminal,

```bash
cd backend
uvicorn main:app --reload
```

and frontend in another terminal.

```bash
cd frontend
ng serve --proxy-config=src/proxy.conf.json
```

Modify main component to get data from backend and
see the effect - change `app.component.ts`,

```typescript
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';

export interface Hello {
    Hello: string;
}
@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterOutlet, HttpClientModule],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})

export class AppComponent {

    title = 'frontend';
    hello = '';

    constructor(private http: HttpClient) {
        this.http.get<Hello>('/api').subscribe(data => {
            this.hello = data.Hello;
        });
    }

}
```

 and `app.component.html`.

```html
<h1>Hello, {{hello}} - {{ title }}</h1>
<p>Congratulations! Your app is running. 🎉</p>
<router-outlet></router-outlet>
```

You can also modify `angular.json` and add
`"proxyConfig": "src/proxy.conf.json"` in
`projects->frontend->architect->serve->development`
instead of `--proxy-config=src/proxy.conf.json` parameter.

## Config data

Usually config is set by system variables on backend server
and default values are stored in special `config.yaml` file.
Sometimes some config variables has to be used in frontend.

### Backend config

Install `pyaml-env` library

```bash
pip install pyaml-env
```

add reading config and endpoint returning this config.

```python
from pyaml_env import parse_config

app = FastAPI()
config = parse_config('./config.yaml')

@app.get("/api/config")
async def read_config():
    return config
```

Now you have to define default config in `config.yaml` file.
Something like this.

```yaml
title: !ENV ${TITLE:Marcin}
version: 1.0.0
organization:
  name: "My Organization"
  address: "123 Main St"
```

If the `$TITLE` environment variable is set then its value is returned in the config.
If it is not set then the default value is returned specified after a colon.

<https://dev.to/mkaranasou/python-yaml-configuration-with-environment-variables-parsing-2ha6>

### Frontend config

Generate config service

```bash
ng generate service config/config
```

and update it like this

```typescript
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map, of } from 'rxjs';

export interface Config {
    title: string;
    version: string;
}

@Injectable({
  providedIn: 'root',
})
export class ConfigService {

    private url = "/api/config"
    private static config: Config | undefined = undefined;

    constructor(private http: HttpClient) { }
    
    public getConfig(): Observable<Config> {
        if (!ConfigService.config)
            return this.http.get<Config>(this.url)
                .pipe(map(c => {
                    if (!c.version)
                        c.version = "0.0.1";
                    ConfigService.config = c;
                    return c;
                }));
        else
            return of(ConfigService.config);
    }

}
```

You have also provide `HttpClient` - modify `app.config.ts`.

```TypeScript
import {provideHttpClient} from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [provideRouter(routes), provideAnimations(), provideHttpClient()]
};
```

And now you can use config in components.

```TypeScript
export class AppComponent {

    title = 'frontend';
    version = '';

    constructor(private config: ConfigService) {
        this.config.getConfig().subscribe(c => {
            this.title = c.title;
            this.version = c.version;
        })
    }
}
```

## Common used elements

Below are recipes for creating commonly used elements.

### Table (client side)

List of records (dictionaries) send to the client at once.
The client (Angular) can paginate, sort and filter these records.
In this example it is a list of movies.

#### REST Api endpoint

Define `pydantic` model in `movies.py` file.

```python
from pydantic import BaseModel

class Movie(BaseModel):
    title: str
    year: int
    studio: str
    director: str
```

Add in `main.py` imports and endpoint befora `catch_all` definition.

```python
import json
from typing import List, Union
from movies import Movie

...

@app.get("/api/movies", response_model=List[Movie])
async def get_all_movies():
    with open("movies.json", "r", encoding="utf-8") as file:
        movies_data = json.load(file)   
    return [Movie(**movie) for movie in movies_data]
```

Now you can open <http://127.0.0.1:8000/docs> and see `/api/movies`
endpoint. It returns sample data from JSON file.

#### Frontend - generate Angular Material component

Let's generate standard component for movies table.
I use `-table` suffix to distinguish between various types
of components related to the same data. The componens path is
consistent with the API path.

```bash
$ ng generate @angular/material:table movies/movies-table
CREATE src/app/movies/movies-table/movies-table-datasource.ts (3665 bytes)
CREATE src/app/movies/movies-table/movies-table.component.css (37 bytes)
CREATE src/app/movies/movies-table/movies-table.component.html (882 bytes)
CREATE src/app/movies/movies-table/movies-table.component.spec.ts (744 bytes)
CREATE src/app/movies/movies-table/movies-table.component.ts (1138 bytes)
```

Add this commponent to routing table in `app.routes.ts`.

```typescript
import { Routes } from '@angular/router';
import { MoviesTableComponent } from './movies/movies-table/movies-table.component';

export const routes: Routes = [
    { path: 'movies', component: MoviesTableComponent },
];
```

Add link in `app.component.html` to this table.

```html
<a routerLink="/movies">Movies</a>
```

And add `RouterModule` in `app.component.ts`.

```typescript
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterOutlet } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { ConfigService } from './config/config.service';

export interface Hello {
    Hello: string;
}
@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterOutlet, HttpClientModule, RouterModule],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})

...
```

#### Frontend - service

We need a service which delivers data for component.
So let's start with default one.

```bash
$ ng generate service movies/movies
CREATE src/app/movies/movies.service.spec.ts (357 bytes)
CREATE src/app/movies/movies.service.ts (135 bytes)
```

Create interface for delivered data (you can use <https://transform.tools/json-to-typescript>)
and insert it into generated service.

```typescript
export interface Movie {
  title: string
  year: number
  studio: string
  director: string
}
```

Add `HttpClient` parameter into constuctor and add mehod `getAll()`.

```typescript
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
```

#### Frontend - couple component with service

Generated table component has its own `DataSource` class
with sample data in `movies-table-datasource.ts` file.
It has to be changed to get data from backend (Python).

Replace all `MoviesTableItem` with just `Movie` and import
this interae from service.

Add service in constructor and use it in `connect()` method.

```typescript
    constructor(private service: MoviesService) {
        super();
    }

    connect(): Observable<Movie[]> {
        if (this.paginator && this.sort) {
            return merge(this.service.getAll().pipe(map(data => this.data = data))),
                this.paginator.page, this.sort.sortChange)
                .pipe(map(() => {
                    return this.getPagedData(this.getSortedData([...this.data]));
                }));
        } else {
            throw Error('Please set the paginator and sort on the data source before connecting.');
        }
    }
```

Correct getSortedData method with proper fields.

```typescript
    private getSortedData(data: Movie[]): Movie[] {
        if (!this.sort || !this.sort.active || this.sort.direction === '') {
            return data;
        }

        return data.sort((a, b) => {
            const isAsc = this.sort?.direction === 'asc';
            switch (this.sort?.active) {
                case 'title': return compare(a.title, b.title, isAsc);
                case 'year': return compare(+a.year, +b.year, isAsc);
                case 'studio': return compare(a.studio, b.studio, isAsc);
                case 'director': return compare(a.director, b.director, isAsc);
                default: return 0;
            }
        });
```

In `movies-table.component.ts` replace all `MoviesTableItem` with `Movie` as previous.
Add constructor with injected service and create dataSource object in it.
Correct `displayedColumns` property,

```typescript
    ...
    dataSource!: MoviesTableDataSource;
    service: MoviesService;

    constructor(service: MoviesService) {
        this.service = service;
        this.dataSource = new MoviesTableDataSource(service);
    }   

    displayedColumns = ['title', 'year', 'studio', 'director'];

    ...
```

Correct and add columns in `movies-table.component.html`. Each column
should look like this.

```html
<ng-container matColumnDef="title">
    <th mat-header-cell *matHeaderCellDef mat-sort-header>Title</th>
    <td mat-cell *matCellDef="let row">{{row.title}}</td>
</ng-container>
```

Now all works but without filtering.

#### Frontend - filter

In `movies-table-datasource.ts` add properties:

```typescript
    filter: string = "";
    filterChange = new EventEmitter<string>();
```

And add filtering method using filter property where all data
fields are specified.

```typescript
    private getFilteredData(data: Movie[]): Movie[] {
        if (this.filter)
            return data.filter(movie =>
                movie.title.toLowerCase().includes(this.filter) ||
                movie.year.toLowerCase().includes(this.filter) ||
                movie.studio.toLowerCase().includes(this.filter) ||
                movie.director.toLowerCase().includes(this.filter)
            );
        else
            return data;
    }
```

Modify connect() method to use getFilteredData() and react to the event:

```typescript
    connect(): Observable<Movie[]> {
        if (this.paginator && this.sort) {
            return merge(this.service.getAll().pipe(map(data => this.data = data)),
                this.paginator.page, this.sort.sortChange, this.filterChange)
                .pipe(map(() => {
                    return this.getPagedData(this.getSortedData(this.getFilteredData([...this.data])));
                }));
        } else {
            throw Error('Please set the paginator and sort on the data source before connecting.');
        }
    }
```

In `movies-table.component.html` add at the begginig input box.

```html
<div class="mat-elevation-z8">

    <mat-form-field>
        <input matInput (keyup)="applyFilter($event)" placeholder="Filter">
    </mat-form-field>
    <table mat-table class="full-width-table" matSort aria-label="Elements">
    ...
```

In `movie-table.component.ts` add imports and `applyFilter()` method.

```typescript
...
import { MatFormField } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';   


@Component({
    selector: 'app-movies-table',
    templateUrl: './movies-table.component.html',
    styleUrl: './movies-table.component.css',
    standalone: true,
    imports: [MatTableModule, MatPaginatorModule, MatSortModule, MatFormField, MatInputModule ]
})

...

    applyFilter(event: Event) {
        const filterValue = (event.target as HTMLInputElement).value;
        this.dataSource.filter = filterValue.trim().toLowerCase();
        this.dataSource.filterChange.emit(filterValue);
        console.log(this.dataSource.filter);
        if (this.dataSource.paginator) {
            this.dataSource.paginator.firstPage();
        }
    }
```

In `movies-table.component.css` add

```css
.filter {
    width: 100%;
    margin-bottom: -22px;
}

.filter input {
    width: 100%;
}
```

### CRUD - Create, Read, Update, Delete

Let's add basic operations on records from table above.

#### REST API endpoint

First, let's make the `movies` global dictionary.

```python
with open("movies.json", "r", encoding="utf-8") as file:
    movies_data = json.load(file)
movies = {f"{movie['title']}_{movie['year']}": Movie(**movie) for movie in movies_data}

@app.get("/api/movies", response_model=List[Movie])
async def get_all_movies():
    return [movie for movie in movies.values()]
```

Then add post method. The primary key of movies will be
title and the year. It returns code 201 and `Location`
response header.

```python
@app.post("/api/movies", response_model=Movie)
async def add_movie(movie: Movie):
    key = f"{movie.title}_{movie.year}"
    movies[key] = movie.model_dump()
    location = f"/api/movies/{key}"
    return Response(status_code=201, headers={"Location": location})
```

And the rest of methods (GET, PUT, DELETE).

```python
@app.get("/api/movies/{key}", response_model=Movie)
async def get_movie(key: str):
    if key not in movies:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movies[key]
    
@app.put("/api/movies/{key}")
async def update_movie(key: str, movie: Movie):
    if key not in movies:
        raise HTTPException(status_code=404, detail="Movie not found")
    movies[key] = movie.model_dump()

@app.delete("/api/movies/{key}")
async def update_movie(key: str):
    if key not in movies:
        raise HTTPException(status_code=404, detail="Movie not found")
    movies.pop(key)
```

#### Frontend - service

Frontend service has to changed in similar way.

```typescript
    private endpoint = '/api/movies'

    getAll(): Observable<Movie[]> {
        return this.http.get<Movie[]>(this.endpoint);
    }

    post(movie: Movie): Observable<void> {
        return this.http.post<void>(this.endpoint, movie);
    }

    get(key: string): Observable<Movie> {
        const eKey = encodeURIComponent(key);
        return this.http.get<Movie>(`${this.endpoint}/${eKey}`);
    }

    put(key: string, movie: Movie): Observable<void> {
        const eKey = encodeURIComponent(key);
        return this.http.put<void>(`${this.endpoint}/${eKey}`, movie);
    }

    delete(key: string): Observable<void> {
        const eKey = encodeURIComponent(key);
        return this.http.delete<void>(`${this.endpoint}/${eKey}`);
    }
```

#### Frontend - edit form

Data editing can be done in two ways: a modal window in the
current page or a separate page. Let's do the second way.

Generate standard component.

```bash
ng generate component movies/movie-form
```

Add this commponent to routing table in `app.routes.ts`.

```typescript
export const routes: Routes = [
    { path: 'movies', component: MoviesTableComponent },
    { path: 'movies/:key', component: MovieFormComponent },
];
```

Create form with `FormBuilder`,

```typescript
...
    form = this.fb.group({
        title: ['', [Validators.required, Validators.minLength(5)]],
        year: [0, [Validators.required]],
        studio: "",
        director: ['', [Validators.required, Validators.minLength(5)]]
      });
    

    constructor(
        private fb: FormBuilder,
...
```

Add video loading based on key in path.

```typescript
    key!: string;
    movie!: Movie;

    constructor(
        private route: ActivatedRoute,
        private service: MoviesService
    ) {
        this.route.params.subscribe(params => {
            this.key = params['key'];
            if (this.key && this.key !== '__NEW__')
                this.service.get(this.key).subscribe(movie => {
                    this.movie = movie;
                    this.form.setValue(movie);
                });
          });
    }
```

Add `onSubmit()` method.

```typescript
    onSubmit() {
        if (this.form.invalid) return;
        const movie = this.form.getRawValue() as Movie;
        if (this.key === '__NEW__') {
            this.service.post(movie).subscribe(() => {
                this.form.reset();
            });
        } else {
            this.service.put(this.key, movie).subscribe(() => {
                this.form.reset();
            });
        }
    }
```

And `movie-form.component.ts`

```html
<form [formGroup]="form" novalidate (ngSubmit)="onSubmit()">
    <mat-card>
        <mat-card-header>
            <mat-card-title>Movie Information</mat-card-title>
        </mat-card-header>
        <mat-card-content>
            <div class="row">
                <div class="col">
                    <mat-form-field class="full-width">
                        <input matInput placeholder="Title" formControlName="title">
                        @if (form.controls['title'].hasError('required')) {
                        <mat-error>Movie title is <strong>required</strong></mat-error>
                        }
                    </mat-form-field>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <mat-form-field class="full-width">
                        <input matInput maxlength="4" placeholder="Year" formControlName="year" type="number">
                    </mat-form-field>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <mat-form-field class="full-width">
                        <input matInput placeholder="Studio" formControlName="studio">
                    </mat-form-field>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <mat-form-field class="full-width">
                        <input matInput placeholder="Director" formControlName="director">
                    </mat-form-field>
                </div>
            </div>
        </mat-card-content>
        <mat-card-actions>
            <button mat-raised-button color="primary" type="submit">Submit</button>
        </mat-card-actions>
    </mat-card>
</form>
```

#### Frontend - couple table with edit form

Add action buttons in `movie-table.component.html`.

```html
...
        <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef>Actions
              <button mat-icon-button matTooltip="Click to Edit" class="iconbutton" color="primary" routerLink="/movies/__NEW__">
                <mat-icon aria-label="Add">add</mat-icon>
              </button>      
            </th>
            <td mat-cell *matCellDef="let row">
              <button mat-icon-button matTooltip="Click to Edit" class="iconbutton" color="primary" [routerLink]="['/movies', row.title + '_' + row.year]">
                <mat-icon aria-label="Edit">edit</mat-icon>
              </button>
              <button mat-icon-button matTooltip="Click to Delete" class="iconbutton" color="primary" (click)="delete(row)">
                <mat-icon aria-label="Delete">delete</mat-icon>
              </button>
            </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
    </table>
...
```

Add 'actions' column and delete method in `movies-table.component.ts`.

```typescript
...
    constructor(service: MoviesService) {
        this.dataSource = new MoviesTableDataSource(service);
    }
    
    displayedColumns = ['title', 'year', 'studio', 'director', 'actions'];

    ngAfterViewInit(): void {
...
    delete(movie: Movie) {
        this.service.delete(movie.title + "_" + movie.year).subscribe(() => {
            this.dataSource.data = this.dataSource.data.filter(m => m !== movie);
            this.dataSource.filterChange.emit("");
        });
    }
...
```

That's all folks.
