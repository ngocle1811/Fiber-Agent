from pydantic import BaseModel, Field

class DistanceResponse(BaseModel):
    """
    Response tính khoảng cách giữa hai điểm mạng.
    """
    from_code: str
    to_code: str
    distance_m: float = Field(description="Khoảng cách theo mét")

class NearestPointResponse(BaseModel):
    """
    Response điểm gần nhất.
    """

    ma_diem: str
    ten_diem: str | None = None
    loai_diem: str | None = None

    vi_do: float | None = None
    kinh_do: float | None = None
    dia_chi: str | None = None

    ma_tuyen: str | None = None
    tinh: str | None = None
    trang_thai: str | None = None
    thiet_bi: str | None = None

    distance_m: float


class NearbyPointResponse(BaseModel):
    """
    Response danh sách điểm nằm trong bán kính.
    """
    ma_diem: str
    ten_diem: str | None = None
    loai_diem: str | None = None

    vi_do: float | None = None
    kinh_do: float | None = None
    dia_chi: str | None = None

    ma_tuyen: str | None = None
    tinh: str | None = None
    trang_thai: str | None = None
    thiet_bi: str | None = None

    distance_m: float