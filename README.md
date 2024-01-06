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
