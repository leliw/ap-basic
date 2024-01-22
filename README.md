# Python + Angular

It's a simple full stack project with Angular frontend and Python backend.

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

### Serve Angular files by Python

At first change `outputPath` in `frontend/angular.json` from `"dist/frontend"` to `"../backend/static"`.

```json
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "frontend": {
      "projectType": "application",
      "schematics": {},
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:application",
          "options": {
            "outputPath": "../backend/static",
```

Now you can compile Angular part.

```bash
cd frontend
ng build
```

Compiled files will be written in `backend/static/browser`.
Set python to serve these files - modify `main.py`.

```python
from my_starlette.staticfiles import StaticFiles

# Angular static files - it have to be at the end of file
app.mount("/", StaticFiles(directory="static/browser", html = True), name="static")
```

The `my_starlette.staticfiles` is my modyfication of [Starlette](https://www.starlette.io/) where
CSS and JavaScrip files have haaders with proper `Content-type`. Just grab it from my repo.

If `unicorn` still running at <http://127.0.0.1:8000/> you see Angular default page.

### Dockerize it all

Create `requirements.txt` file for python:

```bash
cd backend
pip freeze > requirements.txt
cd ..
```

Create `Dockerfile`.

```Dockerfile
FROM python:3.11.7-slim
EXPOSE 8000
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
RUN python -m pip install --upgrade pip
# Install pip requirements
COPY backend/requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY ./backend/ /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
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
docker run -p 8088:8000 leliw/ap-basic
```

Go <http://localhost:8088/>.

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
