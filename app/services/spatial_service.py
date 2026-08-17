from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging_config import get_logger
from app.repositories.spatial_repository import SpatialRepository

logger = get_logger(__name__)

class SpatialService:
    """
    Service xử lý nghiệp vụ liên quan đến vị trí địa lý.

    Service này không tự viết SQL.
    Nó gọi SpatialRepository để truy vấn PostGIS.
    """
    def __init__(self, db: Session):
        self.repository = SpatialRepository(db)

    def calculate_distance(
        self,
        from_code: str,
        to_code: str,
    ) -> dict:
        """
        Tính khoảng cách giữa hai điểm mạng.
        """
        normalized_from_code = self._clean_code(from_code)
        normalized_to_code = self._clean_code(to_code)

        result = self.repository.calculate_distance_between_points(
            from_code=normalized_from_code,
            to_code=normalized_to_code,
        )

        if result is None:
            raise NotFoundException(
                message=(
                    f"Không tìm thấy một trong hai điểm: "
                    f"{normalized_from_code}, {normalized_to_code}"
                )
            )

        result["distance_m"] = round(float(result["distance_m"]), 2)
        return result

    def find_nearest_point(
        self,
        from_code: str,
        target_type: str,
    ) -> dict:
        """
        Tìm điểm gần nhất theo loại điểm.
        """
        normalized_from_code = self._clean_code(from_code)
        cleaned_target_type = self._clean_text(target_type)

        if cleaned_target_type is None:
            raise NotFoundException(message="Bạn cần truyền loại điểm cần tìm")

        result = self.repository.find_nearest_point(
            from_code=normalized_from_code,
            target_type=cleaned_target_type,
        )

        if result is None:
            raise NotFoundException(
                message=(
                    f"Không tìm thấy {cleaned_target_type} gần điểm "
                    f"{normalized_from_code}"
                )
            )

        result["distance_m"] = round(float(result["distance_m"]), 2)
        return result

    def find_points_within_radius(
        self,
        from_code: str,
        target_type: str,
        radius_m: float,
        limit: int = 20,
    ) -> list[dict]:
        """
        Tìm danh sách điểm trong bán kính.
        """
        normalized_from_code = self._clean_code(from_code)
        cleaned_target_type = self._clean_text(target_type)

        if cleaned_target_type is None:
            raise NotFoundException(message="Bạn cần truyền loại điểm cần tìm")

        results = self.repository.find_points_within_radius(
            from_code=normalized_from_code,
            target_type=cleaned_target_type,
            radius_m=radius_m,
            limit=limit,
        )

        for item in results:
            item["distance_m"] = round(float(item["distance_m"]), 2)

        return results

    @staticmethod
    def _clean_code(value: str) -> str:
        """
        Chuẩn hóa mã điểm.

        Ví dụ:
        " sta000001 " -> "STA000001"
        """

        return value.strip().upper()

    @staticmethod
    def _clean_text(value: str | None) -> str | None:
        """
        Xóa khoảng trắng thừa.
        """

        if value is None:
            return None

        cleaned = value.strip()
        return cleaned if cleaned else None