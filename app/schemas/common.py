#Schema là lớp định dạng dữ liệu request/response API.
#File này tạo ra mẫu response dùng chung cho API.
from typing import Generic, TypeVar
from pydantic import BaseModel


T = TypeVar("T")

class PaginationMeta(BaseModel):
    """
    Metadata phân trang.
    Metadata = thông tin phụ đi kèm dữ liệu chính.
    """

    limit: int  #limit là số bản ghi muốn lấy trong một lần.
    offset: int #offset là vị trí bắt đầu lấy dữ liệu.
    total: int | None = None

class SuccessResponse(BaseModel, Generic[T]):
    """
    Response thành công dùng chung.

    Ví dụ:
    {
        "success": true,
        "data": {...}
    }
    """

    success: bool = True
    data: T


class ListResponse(BaseModel, Generic[T]):
    """
    Response danh sách dùng chung.

    Ví dụ:
    {
        "success": true,
        "data": [...],
        "meta": {
            "limit": 20,
            "offset": 0
        }
    }
    """

    success: bool = True
    data: list[T]
    meta: PaginationMeta