from typing import Any

from sqlalchemy.orm import Session

from app.services.spatial_service import SpatialService

def calculate_distance_tool(
    db: Session,
    from_code: str,
    to_code: str,
) -> dict[str, Any]:
    """
    Tool tính khoảng cách giữa hai điểm mạng.

    Ví dụ:
    - Khoảng cách giữa AGG001 và MS000102?
    - STA000001 cách POP000098 bao xa?
    """

    service = SpatialService(db)

    return service.calculate_distance(
        from_code=from_code,
        to_code=to_code,
    )


def find_nearest_point_tool(
    db: Session,
    from_code: str,
    target_type: str,
) -> dict[str, Any]:
    """
    Tool tìm điểm gần nhất theo loại điểm.

    Ví dụ:
    - POP gần AGG001 nhất?
    - Măng xông gần STA000001 nhất?
    """

    service = SpatialService(db)

    return service.find_nearest_point(
        from_code=from_code,
        target_type=target_type,
    )


def find_points_within_radius_tool(
    db: Session,
    from_code: str,
    target_type: str,
    radius_m: float,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Tool tìm các điểm nằm trong bán kính.

    Ví dụ:
    - Có măng xông nào trong bán kính 500m quanh AGG001 không?
    """

    safe_limit = max(1, min(limit, 100))

    service = SpatialService(db)

    results = service.find_points_within_radius(
        from_code=from_code,
        target_type=target_type,
        radius_m=radius_m,
        limit=safe_limit,
    )
    return {
        "items": results,
        "meta": {
            "radius_m": radius_m,
            "limit": safe_limit,
            "total_returned": len(results),
        },
    }