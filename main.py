from fastapi import FastAPI
from app.api.v1.wallets import router as wallet_router
from app.api.v1.operations import router as operations_router
from app.api.v1.users import router as users_router 
from app.api.v1.stats import router as stats_router
from app.exception_handlers import register_exception_handlers


app = FastAPI()
register_exception_handlers(app)
app.include_router(wallet_router, prefix="/api/v1", tags=["wallet"])
app.include_router(operations_router, prefix="/api/v1", tags=["operations"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(stats_router, prefix="/api/v1", tags=["stats"])
