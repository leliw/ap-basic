"""Main file for FastAPI server"""
from typing import Union
from fastapi import FastAPI
from pyaml_env import parse_config

from my_starlette.staticfiles import StaticFiles

app = FastAPI()
config = parse_config('./config.yaml')

@app.get("/api/config")
async def read_config():
    """Return config from yaml file"""
    return config

@app.get("/api")
async def read_root():
    """Return Hello World"""
    return {"Hello": "World"}

@app.get("/api/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    """Return item_id and q"""
    return {"item_id": item_id, "q": q}

# Angular static files - it have to be at the end of file
app.mount("/", StaticFiles(directory="static/browser", html = True), name="static")
