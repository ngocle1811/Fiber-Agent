from typing import Any

from sqlalchemy.orm import Session

from app.schemas.network_point import NetworkPointResponse
from app.services.network_point_service import NetworkPointService

def get_point_by_code_tool(
    db: Session,
    ma_diem: str,
) -> dict[str, Any]:
    """
    Tool lấy thông tin một điểm mạng theo mã điểm.

    Ví dụ:
    - AGG001
    - STA000001
    - POP000098
    - MS000102
    """

    service = NetworkPointService(db)
    point = service.get_point_by_code(ma_diem)

    return NetworkPointResponse.model_validate(point).model_dump(mode="json")


def list_points_tool(
    db: Session,
    loai_diem: str | None = None,
    ma_tuyen: str | None = None,
    tinh: str | None = None,
    trang_thai: str | None = None,
    thiet_bi: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, Any]:
    """
    Tool lấy danh sách điểm mạng theo bộ lọc.

    Dùng cho các câu hỏi kiểu:
    - Liệt kê POP trên tuyến X
    - Liệt kê điểm đang bảo trì
    - Liệt kê Router ở Hải Phòng
    """

    safe_limit = max(1, min(limit, 50))
    safe_offset = max(0, offset)

    service = NetworkPointService(db)

    points = service.list_points(
        loai_diem=loai_diem,
        ma_tuyen=ma_tuyen,
        tinh=tinh,
        trang_thai=trang_thai,
        thiet_bi=thiet_bi,
        limit=safe_limit,
        offset=safe_offset,
    )
    total = service.count_points(
        loai_diem=loai_diem,
        ma_tuyen=ma_tuyen,
        tinh=tinh,
        trang_thai=trang_thai,
        thiet_bi=thiet_bi,
    )

    data = [
        NetworkPointResponse.model_validate(point).model_dump(mode="json")
        for point in points
    ]

    return {
        "items": data,
        "meta": {
            "limit": safe_limit,
            "offset": safe_offset,
            "total": total,
        },
        "filters": {
            "loai_diem": loai_diem,
            "ma_tuyen": ma_tuyen,
            "tinh": tinh,
            "trang_thai": trang_thai,
            "thiet_bi": thiet_bi,
        },
    }


def count_points_tool(
    db: Session,
    loai_diem: str | None = None,
    ma_tuyen: str | None = None,
    tinh: str | None = None,
    trang_thai: str | None = None,
    thiet_bi: str | None = None,
) -> dict[str, Any]:
    """
    Tool đếm số lượng điểm mạng theo bộ lọc.

    Dùng cho các câu hỏi kiểu:
    - Có bao nhiêu POP trên tuyến X?
    - Có bao nhiêu Router?
    - Có bao nhiêu điểm đang bảo trì?
    """

    service = NetworkPointService(db)

    count = service.count_points(
        loai_diem=loai_diem,
        ma_tuyen=ma_tuyen,
        tinh=tinh,
        trang_thai=trang_thai,
        thiet_bi=thiet_bi,
    )

    return {
        "count": count,
        "filters": {
            "loai_diem": loai_diem,
            "ma_tuyen": ma_tuyen,
            "tinh": tinh,
            "trang_thai": trang_thai,
            "thiet_bi": thiet_bi,
        },
    }