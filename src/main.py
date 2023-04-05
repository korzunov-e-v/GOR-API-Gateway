import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

# This path was added to solve some problems with absolute
# imports in order to run this script as an executable file.
sys.path.append(str(Path(__file__).parent.parent))

from src.core import RunMode, get_settings
from src.core.utils import lifespan
from src.api.routers import routers
from src.core.middlewares import RequestIDMiddleware, RequestLogMiddleware

settings = get_settings()


def get_application() -> FastAPI:
    """Get FastAPI app"""

    _app = FastAPI(
        title=settings.project_name,
        root_path=settings.root_path,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    _app.state.services = []
    _app.include_router(routers, prefix=settings.api_prefix)
    _app.add_middleware(RequestLogMiddleware)
    _app.add_middleware(RequestIDMiddleware)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    return _app


app = get_application()
Instrumentator().instrument(app).expose(app)


def main():
    uvicorn.run(**settings.uvicorn.dict())


if __name__ == "__main__":
    main()
