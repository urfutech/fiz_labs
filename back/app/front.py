from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")
app.frontend("/", directory="front_part")
