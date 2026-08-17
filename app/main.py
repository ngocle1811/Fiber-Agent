from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.network_points import (
    router as network_points_router,
)
from app.api.routes.spatial import router as spatial_router
from app.core.config import get_settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
)
from app.core.logging_config import (
    get_logger,
    setup_logging,
)


def create_app() -> FastAPI:
    """
    Tạo FastAPI application.

    Đây là nơi:
    - cấu hình logging
    - tạo ứng dụng FastAPI
    - đăng ký bộ xử lý lỗi
    - đăng ký các nhóm API
    """

    setup_logging()

    settings = get_settings()
    logger = get_logger(__name__)

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
    )

    static_dir = Path(__file__).resolve().parent / "static"
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static",
    )

    @app.get("/", include_in_schema=False)
    def web_interface() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    app.add_exception_handler(
        AppException,
        app_exception_handler,
    )

    app.include_router(
        health_router,
        prefix="/api",
    )

    app.include_router(
        network_points_router,
        prefix="/api",
    )

    app.include_router(
        spatial_router,
        prefix="/api",
    )

    app.include_router(
        chat_router,
        prefix="/api",
    )

    logger.info(
        "Fiber Agent app started environment=%s",
        settings.APP_ENV,
    )

    return app


app = create_app()
