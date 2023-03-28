import sys
from pathlib import Path

from fastapi import FastAPI

from src.core import RunMode, get_settings
from src.api.routers import routers

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
    return _app


app = get_application()


def main():
    uvicorn.run(**settings.uvicorn.dict())


if __name__ == "__main__":
    main()
