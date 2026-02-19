from fastapi import FastAPI

from app.api.v1 import factories, machines, measurements, organizations
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# Register routers
app.include_router(
    organizations.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    factories.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    machines.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(measurements.router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "version": settings.VERSION}
