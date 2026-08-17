from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.common import SuccessResponse
from app.schemas.spatial import (
    DistanceResponse,
    NearbyPointResponse,
    NearestPointResponse,
)
from app.services.spatial_service import SpatialService


router = APIRouter(prefix="/spatial", tags=["Spatial"])


@router.get(
    "/distance",
    response_model=SuccessResponse[DistanceResponse],
)
def calculate_distance(
    from_code: str = Query(description="Mã điểm thứ nhất, ví dụ: STA000001"),
    to_code: str = Query(description="Mã điểm thứ hai, ví dụ: MS000002"),
    db: Session = Depends(get_db),
):
    """
    Tính khoảng cách giữa hai điểm mạng.

    Ví dụ:
    /api/spatial/distance?from_code=STA000001&to_code=MS000002
    """

    service = SpatialService(db)

    result = service.calculate_distance(
        from_code=from_code,
        to_code=to_code,
    )

    return {
        "success": True,
        "data": result,
    }


@router.get(
    "/nearest",
    response_model=SuccessResponse[NearestPointResponse],
)
def find_nearest_point(
    from_code: str = Query(description="Mã điểm gốc, ví dụ: STA000001"),
    target_type: str = Query(description="Loại điểm cần tìm, ví dụ: POP, Măng xông, Trạm"),
    db: Session = Depends(get_db),
):
    """
    Tìm điểm gần nhất theo loại điểm.

    Ví dụ:
    /api/spatial/nearest?from_code=STA000001&target_type=POP
    /api/spatial/nearest?from_code=STA000001&target_type=Măng xông
    """

    service = SpatialService(db)

    result = service.find_nearest_point(
        from_code=from_code,
        target_type=target_type,
    )

    return {
        "success": True,
        "data": result,
    }


@router.get(
    "/within-radius",
    response_model=SuccessResponse[list[NearbyPointResponse]],
)
def find_points_within_radius(
    from_code: str = Query(description="Mã điểm gốc, ví dụ: STA000001"),
    target_type: str = Query(description="Loại điểm cần tìm, ví dụ: POP, Măng xông, Trạm"),
    radius_m: float = Query(
        default=500,
        gt=0,
        description="Bán kính tính theo mét",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Số kết quả tối đa",
    ),
    db: Session = Depends(get_db),
):
    """
    Tìm các điểm nằm trong bán kính.

    Ví dụ:
    /api/spatial/within-radius?from_code=STA000001&target_type=Măng xông&radius_m=500
    """

    service = SpatialService(db)

    results = service.find_points_within_radius(
        from_code=from_code,
        target_type=target_type,
        radius_m=radius_m,
        limit=limit,
    )

    return {
        "success": True,
        "data": results,
    }