from fastapi import FastAPI
from db import Base, engine
from routers.auth import router as auth_router
from routers.posts import router as posts_router
from routers.comments import router as comments_router

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
                   
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(posts_router)         
