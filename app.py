from fastapi import FastAPI
from db import Base, engine
from auth import router as auth_router
from posts import router as posts_router
from comments import router as comments_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(posts_router)         
