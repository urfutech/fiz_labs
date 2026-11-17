from fastapi import FastAPI
from .routers import auth, lab, user

app = FastAPI()

app.include_router(auth.router)
app.include_router(lab.router)
app.include_router(user.router)
