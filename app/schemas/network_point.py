from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict

class NetworkPointResponse(BaseModel):
    """
    Dữ liệu điểm mạng trả về cho client.
    Client = nơi gọi API, ví dụ frontend hoặc tool của Agent.
    """
    #SQLAlchemy lấy object NetworkPoint từ database -> Pydantic chuyển object đó thành JSON trả về API
    model_config = ConfigDict(from_attributes=True)

    id: str
    ma_diem: str
    ten_diem: str | None = None

    vi_do: float | None = None
    kinh_do: float | None = None

    dia_chi: str | None = None
    ngay_van_hanh: date | None = None
    ghi_chu: str | None = None

    parent_id: str | None = None
    ma_tuyen: str | None = None
    thu_tu: int | None = None

    loai_diem: str | None = None

    station_ma: str | None = None
    station_ten: str | None = None

    stt_start_point: int | None = None
    is_deleted: bool | None = None

    tinh: str | None = None
    trang_thai: str | None = None

    loai_cap: str | None = None
    so_soi: int | None = None
    thiet_bi: str | None = None


class NetworkPointCountResponse(BaseModel):
    """
    Response cho API đếm số lượng điểm mạng.
    """

    count: int
    filters: dict[str, Any]