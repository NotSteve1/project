from fastapi import FastAPI
from app.routers import auth_router, movie_router, rating_router, admin_router, user_router

app = FastAPI()

app = FastAPI(title="Movie Rating API", version="1.0.0", description="API for rating movies")


app.include_router(
    user_router.router
)

app.include_router(
    auth_router.router
)

app.include_router(
    movie_router.router
)

app.include_router(
    rating_router.router
)

app.include_router(
    admin_router.router
)