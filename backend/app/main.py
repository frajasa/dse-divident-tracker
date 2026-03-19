import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers import alerts, analytics, assistant, auth, companies, dividends, education, portfolio, sync, tax, watchlist
from app.scheduler import setup_scheduler, shutdown_scheduler

# ─── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dse")

# ─── Create tables ────────────────────────────────────────────────
# Import SyncLog so its table is registered with Base.metadata
from app.models.sync_log import SyncLog  # noqa: F401

Base.metadata.create_all(bind=engine)


# ─── Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting scheduler...")
    setup_scheduler()
    yield
    logger.info("Shutting down scheduler...")
    shutdown_scheduler()


# ─── App ──────────────────────────────────────────────────────────
app = FastAPI(
    title="DSE Dividend Tracker",
    description="Dividend tracking, tax calculation, and portfolio projection for Dar es Salaam Stock Exchange",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

# ─── CORS — reads allowed origins from config ────────────────────
origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global exception handler ────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ─── Routers ──────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(dividends.router)
app.include_router(tax.router)
app.include_router(portfolio.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(assistant.router)
app.include_router(education.router)
app.include_router(watchlist.router)
app.include_router(sync.router)


# ─── Health check ─────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {
        "name": "DSE Dividend Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "companies": "/api/companies",
            "dividends": "/api/dividends",
            "yields": "/api/dividends/yields",
            "upcoming": "/api/dividends/upcoming",
            "tax_calculator": "/api/tax/calculate",
            "portfolio_tax": "/api/tax/portfolio",
            "portfolio": "/api/portfolio",
            "alerts": "/api/alerts/preferences",
            "analytics": "/api/analytics/overview",
            "analytics_aristocrats": "/api/analytics/aristocrats",
            "analytics_movers": "/api/analytics/movers",
            "analytics_risk": "/api/analytics/risk-metrics",
            "assistant": "/api/assistant/ask",
            "education": "/api/education/categories",
            "watchlist": "/api/watchlist",
            "sync": "/api/sync/status",
        },
    }
