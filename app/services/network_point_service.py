from sqlalchemy.orm import Session
"""
Session là phiên làm việc với database.
Session chính là đối tượng giúp:gửi câu truy vấn xuống database, lấy kết quả về, quản lý giao dịch nếu có thêm/sửa/xóa dữ liệu
"""
from app.core.exceptions import NotFoundException
from app.core.logging_config import get_logger
from app.models.network_point import NetworkPoint
from app.repositories.network_point_repository import NetworkPointRepository


logger = get_logger(__name__)

class NetworkPointService:
    """
    Service xử lý nghiệp vụ liên quan đến điểm mạng.
    Service = lớp xử lý logic chính.
    Repository chỉ truy vấn database.
    """

    def __init__(self, db: Session):
        self.repository = NetworkPointRepository(db)

    def get_point_by_code(self, ma_diem: str) -> NetworkPoint:
        """
        Lấy thông tin một điểm mạng theo mã điểm.

        Ví dụ:
        STA000001
        AGG001
        POP001
        """

        normalized_code = ma_diem.strip().upper()

        logger.info("Get network point by code=%s", normalized_code)

        point = self.repository.get_by_code(normalized_code)

        if point is None:
            raise NotFoundException(
                message=f"Không tìm thấy điểm mạng có mã: {normalized_code}"
            )

        return point

    def list_points(
        self,
        loai_diem: str | None = None,
        ma_tuyen: str | None = None,
        tinh: str | None = None,
        trang_thai: str | None = None,
        thiet_bi: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[NetworkPoint]:
        """
        Lấy danh sách điểm mạng.

        Hàm này chuẩn hóa input trước khi gọi repository.
        """

        return self.repository.list_points(
            loai_diem=self._clean_text(loai_diem),
            ma_tuyen=self._clean_code(ma_tuyen),
            tinh=self._clean_text(tinh),
            trang_thai=self._clean_text(trang_thai),
            thiet_bi=self._clean_text(thiet_bi),
            limit=limit,
            offset=offset,
        )

    def count_points(
        self,
        loai_diem: str | None = None,
        ma_tuyen: str | None = None,
        tinh: str | None = None,
        trang_thai: str | None = None,
        thiet_bi: str | None = None,
    ) -> int:
        """
        Đếm số điểm mạng theo bộ lọc.
        """

        return self.repository.count_points(
            loai_diem=self._clean_text(loai_diem),
            ma_tuyen=self._clean_code(ma_tuyen),
            tinh=self._clean_text(tinh),
            trang_thai=self._clean_text(trang_thai),
            thiet_bi=self._clean_text(thiet_bi),
        )

    @staticmethod
    def _clean_text(value: str | None) -> str | None:
        """
        Xóa khoảng trắng thừa ở đầu/cuối chuỗi.
        """

        if value is None:
            return None

        cleaned = value.strip()
        return cleaned if cleaned else None

    @staticmethod
    def _clean_code(value: str | None) -> str | None:
        """
        Chuẩn hóa mã tuyến, mã điểm.

        Ví dụ:
        " tuyen-0001 " -> "TUYEN-0001"
        """

        if value is None:
            return None

        cleaned = value.strip().upper()
        return cleaned if cleaned else None