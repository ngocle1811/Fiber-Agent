from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class SpatialRepository:
    """
    Repository xử lý truy vấn không gian bằng PostGIS.
    Spatial = không gian / vị trí địa lý.
    Repository này dùng SQL trực tiếp vì các hàm PostGIS như:
    - ST_Distance
    - ST_DWithin
    - KNN search
    viết bằng SQL sẽ rõ ràng hơn.
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_distance_between_points(
        self,
        from_code: str,
        to_code: str,
    ) -> dict[str, Any] | None:
        """
        Tính khoảng cách giữa hai điểm theo mã điểm.
        ST_Distance với geography sẽ trả về đơn vị mét.
        """

        sql = text(
            """
            SELECT
                p1.ma_diem AS from_code,
                p2.ma_diem AS to_code,
                ST_Distance(p1.geog, p2.geog) AS distance_m
            FROM network_points p1
            JOIN network_points p2 ON p2.ma_diem = :to_code
            WHERE p1.ma_diem = :from_code
              AND COALESCE(p1.is_deleted, false) = false
              AND COALESCE(p2.is_deleted, false) = false
            """
        )

        logger.info(
            "Calculate distance: from_code=%s, to_code=%s",
            from_code,
            to_code,
        )
        row = self.db.execute(
            sql,
            {
                "from_code": from_code,
                "to_code": to_code,
            },
        ).mappings().first()

        return dict(row) if row else None

    def find_nearest_point(
        self,
        from_code: str,
        target_type: str,
    ) -> dict[str, Any] | None:
        """
        Tìm điểm gần nhất theo loại điểm.
        Ví dụ:
        - POP gần STA000001 nhất
        - Măng xông gần AGG001 nhất

        KNN Search = tìm gần nhất bằng toán tử <-> trên cột geom.
        Sau đó vẫn dùng ST_Distance trên geog để tính khoảng cách theo mét.
        """

        sql = text(
            """
            WITH origin AS (
                SELECT ma_diem, geom, geog
                FROM network_points
                WHERE ma_diem = :from_code
                  AND COALESCE(is_deleted, false) = false
                LIMIT 1
            )
            SELECT
                p.ma_diem,
                p.ten_diem,
                p.loai_diem,
                p.vi_do,
                p.kinh_do,
                p.dia_chi,
                p.ma_tuyen,
                p.tinh,
                p.trang_thai,
                p.thiet_bi,
                ST_Distance(p.geog, origin.geog) AS distance_m
            FROM network_points p
            CROSS JOIN origin
            WHERE COALESCE(p.is_deleted, false) = false
              AND p.ma_diem <> origin.ma_diem
              AND p.loai_diem ILIKE :target_type_pattern
            ORDER BY p.geom <-> origin.geom
            LIMIT 1
            """
        )

        logger.info(
            "Find nearest point: from_code=%s, target_type=%s",
            from_code,
            target_type,
        )

        row = self.db.execute(
            sql,
            {
                "from_code": from_code,
                "target_type_pattern": f"%{target_type}%",
            },
        ).mappings().first()

        return dict(row) if row else None

    def find_points_within_radius(
        self,
        from_code: str,
        target_type: str,
        radius_m: float,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Tìm các điểm thuộc loại target_type nằm trong bán kính radius_m.

        ST_DWithin = kiểm tra hai điểm có nằm trong khoảng cách cho phép không.
        Với geography, đơn vị là mét.
        """

        sql = text(
            """
            WITH origin AS (
                SELECT ma_diem, geog
                FROM network_points
                WHERE ma_diem = :from_code
                  AND COALESCE(is_deleted, false) = false
                LIMIT 1
            )
            SELECT
                p.ma_diem,
                p.ten_diem,
                p.loai_diem,
                p.vi_do,
                p.kinh_do,
                p.dia_chi,
                p.ma_tuyen,
                p.tinh,
                p.trang_thai,
                p.thiet_bi,
                ST_Distance(p.geog, origin.geog) AS distance_m
            FROM network_points p
            CROSS JOIN origin
            WHERE COALESCE(p.is_deleted, false) = false
              AND p.ma_diem <> origin.ma_diem
              AND p.loai_diem ILIKE :target_type_pattern
              AND ST_DWithin(p.geog, origin.geog, :radius_m)
            ORDER BY distance_m ASC
            LIMIT :limit
            """
        )

        logger.info(
            "Find points within radius: from_code=%s, target_type=%s, radius_m=%s, limit=%s",
            from_code,
            target_type,
            radius_m,
            limit,
        )

        rows = self.db.execute(
            sql,
            {
                "from_code": from_code,
                "target_type_pattern": f"%{target_type}%",
                "radius_m": radius_m,
                "limit": limit,
            },
        ).mappings().all()

        return [dict(row) for row in rows]