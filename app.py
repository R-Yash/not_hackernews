from fastapi import FastAPI
from db import Base, engine
from routers.auth import router as auth_router
from routers.posts import router as posts_router
from routers.comments import router as comments_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(posts_router)         
