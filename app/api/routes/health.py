from fastapi import APIRouter

from app.core.config import get_settings
from app.core.database import check_database_connection


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    """
    Health check = kiểm tra tình trạng hệ thống.

    API này dùng để biết:
    - backend có chạy không
    - backend có kết nối được database không
    """

    settings = get_settings()
    database_ok = check_database_connection()

    return {
        "success": True,
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "connected" if database_ok else "disconnected",
    }