from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.common import ListResponse, PaginationMeta, SuccessResponse
from app.schemas.network_point import (
    NetworkPointCountResponse,
    NetworkPointResponse,
)
from app.services.network_point_service import NetworkPointService

router = APIRouter(prefix="/network-points", tags=["Network Points"])


@router.get(
    "/count",
    response_model=SuccessResponse[NetworkPointCountResponse],
)
def count_network_points(
    loai_diem: str | None = Query(default=None, description="Loại điểm, ví dụ: Trạm, POP, Măng xông"),
    ma_tuyen: str | None = Query(default=None, description="Mã tuyến, ví dụ: TUYEN-0001"),
    tinh: str | None = Query(default=None, description="Tên tỉnh/thành phố"),
    trang_thai: str | None = Query(default=None, description="Trạng thái điểm mạng"),
    thiet_bi: str | None = Query(default=None, description="Thiết bị, ví dụ: Router, Switch"),
    db: Session = Depends(get_db),
):
    """
    Đếm số lượng điểm mạng theo bộ lọc.

    Ví dụ:
    /api/network-points/count?loai_diem=Trạm
    /api/network-points/count?ma_tuyen=TUYEN-0001
    /api/network-points/count?thiet_bi=Router
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
        "success": True,
        "data": {
            "count": count,
            "filters": {
                "loai_diem": loai_diem,
                "ma_tuyen": ma_tuyen,
                "tinh": tinh,
                "trang_thai": trang_thai,
                "thiet_bi": thiet_bi,
            },
        },
    }


@router.get(
    "",
    response_model=ListResponse[NetworkPointResponse],
)
def list_network_points(
    loai_diem: str | None = Query(default=None, description="Loại điểm, ví dụ: Trạm, POP, Măng xông"),
    ma_tuyen: str | None = Query(default=None, description="Mã tuyến, ví dụ: TUYEN-0001"),
    tinh: str | None = Query(default=None, description="Tên tỉnh/thành phố"),
    trang_thai: str | None = Query(default=None, description="Trạng thái điểm mạng"),
    thiet_bi: str | None = Query(default=None, description="Thiết bị, ví dụ: Router, Switch"),
    limit: int = Query(default=20, ge=1, le=100, description="Số dòng muốn lấy"),
    offset: int = Query(default=0, ge=0, description="Vị trí bắt đầu lấy dữ liệu"),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách điểm mạng.

    Ví dụ:
    /api/network-points
    /api/network-points?ma_tuyen=TUYEN-0001
    /api/network-points?loai_diem=Trạm
    /api/network-points?tinh=Hải Phòng
    """

    service = NetworkPointService(db)

    points = service.list_points(
        loai_diem=loai_diem,
        ma_tuyen=ma_tuyen,
        tinh=tinh,
        trang_thai=trang_thai,
        thiet_bi=thiet_bi,
        limit=limit,
        offset=offset,
    )
    total = service.count_points(
        loai_diem=loai_diem,
        ma_tuyen=ma_tuyen,
        tinh=tinh,
        trang_thai=trang_thai,
        thiet_bi=thiet_bi,
    )

    return {
        "success": True,
        "data": points,
        "meta": PaginationMeta(
            limit=limit,
            offset=offset,
            total=total,
        ),
    }


@router.get(
    "/{ma_diem}",
    response_model=SuccessResponse[NetworkPointResponse],
)
def get_network_point_by_code(
    ma_diem: str,
    db: Session = Depends(get_db),
):
    """
    Lấy chi tiết một điểm mạng theo mã điểm.

    Ví dụ:
    /api/network-points/STA000001
    """

    service = NetworkPointService(db)
    point = service.get_point_by_code(ma_diem)

    return {
        "success": True,
        "data": point,
    }
