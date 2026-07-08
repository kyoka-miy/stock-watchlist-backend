import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.db.redis_cache import redis_cache
from app.exceptions.handlers import app_exception_handler, system_exception_handler, validation_exception_handler
from app.presentation.account_controller import router as account_router
from app.presentation.stock_controller import router as stock_router
from app.presentation.stock_list_controller import router as stock_list_router
from app.presentation.auth_controller import router as auth_router
from app.exceptions.app_exception import AppException


logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    connected = redis_cache.check_connection()
    if not connected:
        logger.warning("Application started without Redis connectivity")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://stock-watchlist-frontend-gamma.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-new-access-token"],
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler  # type: ignore
)

app.add_exception_handler(
    AppException,
    app_exception_handler  # type: ignore
)

app.add_exception_handler(
    Exception,
    system_exception_handler  # type: ignore
)

app.include_router(account_router)
app.include_router(stock_router)
app.include_router(stock_list_router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
