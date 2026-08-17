from datetime import date

from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class NetworkPoint(Base):
    """
    Model ánh xạ với bảng network_points trong PostgreSQL.

    Mỗi object NetworkPoint tương ứng với một dòng trong bảng network_points.
    """

    __tablename__ = "network_points"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    ma_diem: Mapped[str] = mapped_column(String, unique=True, index=True)
    ten_diem: Mapped[str | None] = mapped_column(Text, nullable=True)
    loai_diem: Mapped[str | None] = mapped_column(String, index=True, nullable=True)

    vi_do: Mapped[float | None] = mapped_column(Float, nullable=True)
    kinh_do: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Tạm thời chưa khai báo geom, geog ở đây.
    # Hai cột này là dữ liệu không gian của PostGIS.
    # Sau này khi làm tìm điểm gần nhất / bán kính / khoảng cách, ta xử lý riêng.

    dia_chi: Mapped[str | None] = mapped_column(Text, nullable=True)
    ngay_van_hanh: Mapped[date | None] = mapped_column(Date, nullable=True)
    ghi_chu: Mapped[str | None] = mapped_column(Text, nullable=True)

    parent_id: Mapped[str | None] = mapped_column(String, nullable=True)
    ma_tuyen: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    thu_tu: Mapped[int | None] = mapped_column(Integer, nullable=True)

    station_ma: Mapped[str | None] = mapped_column(String, nullable=True)
    station_ten: Mapped[str | None] = mapped_column(Text, nullable=True)

    stt_start_point: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_deleted: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)

    tinh: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    trang_thai: Mapped[str | None] = mapped_column(String, index=True, nullable=True)

    loai_cap: Mapped[str | None] = mapped_column(String, nullable=True)
    so_soi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    thiet_bi: Mapped[str | None] = mapped_column(String, index=True, nullable=True)