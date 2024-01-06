from typing import Union
from fastapi import FastAPI
from my_starlette.staticfiles import StaticFiles

app = FastAPI()


@app.get("/api")
async def read_root():
    return {"Hello": "World"}


@app.get("/api/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Angular static files - it have to be at the end of file
app.mount("/", StaticFiles(directory="static/browser", html = True), name="static")