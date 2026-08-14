from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from app.db import Base, engine
from app.routers import auth, reports, tickets
from app.rules import RuleError
from app.services import NotFound

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FixIt",
    version="1.0.0",
    description="Campus maintenance requests: report, assign, fix, close.",
)
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(reports.router)


@app.exception_handler(RuleError)
def rule_error(_: Request, exc: RuleError) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=400)


@app.exception_handler(NotFound)
def not_found(_: Request, exc: NotFound) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=404)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")
