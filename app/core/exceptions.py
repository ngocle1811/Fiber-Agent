from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """
    Lỗi chung của ứng dụng.

    Dùng khi ta muốn tự ném lỗi có kiểm soát.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "APP_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class NotFoundException(AppException):
    """
    Lỗi không tìm thấy dữ liệu.
    Ví dụ:
    - Không tìm thấy điểm mạng AGG001
    - Không tìm thấy tuyến TUYEN-0001
    """

    def __init__(self, message: str = "Không tìm thấy dữ liệu"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
        )

async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """
    Chuyển AppException thành JSON response chuẩn.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            },
        },
    )