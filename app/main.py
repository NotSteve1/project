from fastapi import FastAPI
from app.routers import auth_router, movie_router, rating_router, admin_router, user_router
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)