import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core import RunMode, get_settings
from src.api.routers import routers
from src.core.middlewares import RequestIDMiddleware

# This path was added to solve some problems with absolute
# imports in order to run this script as an executable file.
sys.path.append(str(Path(__file__).parent.parent))

import uvicorn


settings = get_settings()


def get_application() -> FastAPI:
    """Get FastAPI app"""

    _app = FastAPI(
        title=settings.project_name,
        root_path=settings.root_path,
        version=settings.app_version,
        debug=settings.debug
    )

    _app.state.services = []
    _app.include_router(routers, prefix=settings.api_prefix)
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


def main():
    uvicorn.run(**settings.uvicorn.dict())


if __name__ == "__main__":
    main()
