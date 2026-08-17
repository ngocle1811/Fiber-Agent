import logging
from logging.config import dictConfig
from pathlib import Path

from app.core.config import get_settings


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logging() -> None:
    """
    Cấu hình logging cho toàn bộ ứng dụng.

    Logging = ghi lại hoạt động của hệ thống.

    File này giúp ghi:
    - log ra terminal khi chạy app
    - log chung vào logs/app.log
    - log lỗi vào logs/error.log

    Sau này khi làm AI Agent, ta sẽ dùng logging để ghi:
    - câu hỏi người dùng
    - tool được gọi
    - SQL được thực thi
    - thời gian truy vấn database
    - thời gian gọi LLM
    - lỗi nếu có
    """

    settings = get_settings()
    log_level = settings.LOG_LEVEL.upper()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,

            "formatters": {
                "console": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "file": {
                    "format": (
                        "%(asctime)s | %(levelname)s | %(name)s | "
                        "%(filename)s:%(lineno)d | %(message)s"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            #quy định log được ghi đi đâu.Handler nghĩa là nơi nhận log.
            "handlers": {
                "console": {    #Handler này ghi log ra terminal.
                    "class": "logging.StreamHandler",
                    "level": log_level,
                    "formatter": "console",
                },
                "app_file": {   #Handler này ghi log vào file: logs/app.log
                    "class": "logging.handlers.RotatingFileHandler",    #RotatingFileHandler là kiểu ghi log vào file nhưng có giới hạn dung lượng.
                    "level": log_level,
                    "formatter": "file",
                    "filename": str(LOG_DIR / "app.log"),
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 5,
                    "encoding": "utf-8",
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "file",
                    "filename": str(LOG_DIR / "error.log"),
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 5,
                    "encoding": "utf-8",
                },
            },

            "root": {   #root: logger gốc của toàn app
                "level": log_level,
                "handlers": ["console", "app_file", "error_file"],
            },

            "loggers": {
                "uvicorn": {
                    "level": log_level,
                    "handlers": ["console", "app_file", "error_file"],
                    "propagate": False, #không truyền nhật ký SQLAlchemy lên bộ ghi nhật ký gốc.
                },
                "uvicorn.error": {
                    "level": log_level,
                    "handlers": ["console", "app_file", "error_file"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": log_level,
                    "handlers": ["console", "app_file"],
                    "propagate": False,
                },
                "sqlalchemy.engine": {
                    "level": "WARNING",
                    "handlers": ["console", "app_file", "error_file"],
                    "propagate": False,
                },
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Tạo logger cho từng file.

    Ví dụ dùng trong file khác:

        logger = get_logger(__name__)
        logger.info("App started")
        logger.error("Database error")

    __name__ giúp biết log này đến từ file/module nào.
    """
    return logging.getLogger(name)