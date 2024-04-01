from fastapi import FastAPI
from .routers import teams, matches, users, auth
import os
# if not os.path.exists('../database.db'):
#     os.system('./init_db.py')

from .database import engine, Base
# from app.models import User, Team, Match

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(matches.router)