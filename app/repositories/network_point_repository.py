from sqlalchemy import String, cast, func, select
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.network_point import NetworkPoint

logger = get_logger(__name__)

class NetworkPointRepository:
    """
    Repository xử lý truy vấn bảng network_points.
    Repository = lớp chuyên làm việc với database.
    Service sẽ gọi repository, route không gọi database trực tiếp.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, ma_diem: str) -> NetworkPoint | None:
        """
        Tìm một điểm mạng theo mã điểm.
        Ví dụ:
        ma_diem = "STA000001"
        """

        stmt = (
            select(NetworkPoint)
            .where(NetworkPoint.ma_diem == ma_diem)
            .where(NetworkPoint.is_deleted == False)
        )

        logger.info("Query network point by ma_diem=%s", ma_diem)

        return self.db.execute(stmt).scalar_one_or_none()

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
        Lấy danh sách điểm mạng theo bộ lọc.

        Bộ lọc có thể gồm:
        - loại điểm
        - mã tuyến
        - tỉnh
        - trạng thái
        - thiết bị
        """

        stmt = select(NetworkPoint).where(NetworkPoint.is_deleted == False)

        if loai_diem:
            stmt = stmt.where(
                cast(NetworkPoint.loai_diem, String).ilike(f"%{loai_diem}%")
            )

        if ma_tuyen:
            stmt = stmt.where(NetworkPoint.ma_tuyen == ma_tuyen)

        if tinh:
            stmt = stmt.where(NetworkPoint.tinh.ilike(f"%{tinh}%"))

        if trang_thai:
            stmt = stmt.where(NetworkPoint.trang_thai.ilike(f"%{trang_thai}%"))

        if thiet_bi:
            stmt = stmt.where(NetworkPoint.thiet_bi.ilike(f"%{thiet_bi}%"))

        stmt = stmt.order_by(NetworkPoint.ma_diem).limit(limit).offset(offset)

        logger.info(
            "List network points with filters: loai_diem=%s, ma_tuyen=%s, tinh=%s, "
            "trang_thai=%s, thiet_bi=%s, limit=%s, offset=%s",
            loai_diem,
            ma_tuyen,
            tinh,
            trang_thai,
            thiet_bi,
            limit,
            offset,
        )

        return list(self.db.execute(stmt).scalars().all())

    def count_points(
        self,
        loai_diem: str | None = None,
        ma_tuyen: str | None = None,
        tinh: str | None = None,
        trang_thai: str | None = None,
        thiet_bi: str | None = None,
    ) -> int:
        """
        Đếm số lượng điểm mạng theo bộ lọc.

        API này phục vụ các câu hỏi kiểu:
        - Có bao nhiêu POP trên tuyến X?
        - Có bao nhiêu Router?
        - Có bao nhiêu điểm đang bảo trì?
        """

        stmt = select(func.count()).select_from(NetworkPoint)
        stmt = stmt.where(NetworkPoint.is_deleted == False)

        if loai_diem:
            stmt = stmt.where(
                cast(NetworkPoint.loai_diem, String).ilike(f"%{loai_diem}%")
            )

        if ma_tuyen:
            stmt = stmt.where(NetworkPoint.ma_tuyen == ma_tuyen)

        if tinh:
            stmt = stmt.where(NetworkPoint.tinh.ilike(f"%{tinh}%"))

        if trang_thai:
            stmt = stmt.where(NetworkPoint.trang_thai.ilike(f"%{trang_thai}%"))

        if thiet_bi:
            stmt = stmt.where(NetworkPoint.thiet_bi.ilike(f"%{thiet_bi}%"))

        logger.info(
            "Count network points with filters: loai_diem=%s, ma_tuyen=%s, tinh=%s, "
            "trang_thai=%s, thiet_bi=%s",
            loai_diem,
            ma_tuyen,
            tinh,
            trang_thai,
            thiet_bi,
        )

        return int(self.db.execute(stmt).scalar_one())