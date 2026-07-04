from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_db_and_tables
from app.routers import auth, heroes, missions


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Secure Hero Missions API",
    description="FastAPI application with SQLModel, JWT protection and business rules Validation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(heroes.router)
app.include_router(missions.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Secure Hero Missions API. Head over to /docs for Swagger UI."
    }
