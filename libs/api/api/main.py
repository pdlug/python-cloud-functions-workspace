from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from .routes import documents, hello

VERSION = "0.0.9"

app: FastAPI = FastAPI(title="API", version=VERSION)

# Include route modules
app.include_router(hello.router)
app.include_router(documents.router)


@app.exception_handler(ValidationError)
async def validation_exception_handler(
    _request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=422, content={"detail": "Validation error", "errors": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="healthy", version=VERSION)
