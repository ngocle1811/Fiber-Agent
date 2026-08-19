import re
import unicodedata
from time import perf_counter
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.tools.point_tools import count_points_tool, get_point_by_code_tool


logger = get_logger(__name__)

POINT_CODE_PATTERN = re.compile(
    r"(?<![A-Z0-9])(?:STA|AGG|POP|MS)[-_]?\d{3,}(?![A-Z0-9])",
    re.IGNORECASE,
)


def _normalize_text(value: str) -> str:
    """Chuẩn hóa chữ thường và bỏ dấu để nhận diện ý định đơn giản."""

    decomposed = unicodedata.normalize(
        "NFD",
        value.lower().replace("đ", "d"),
    )
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )


class FastQueryService:
    """Xử lý các câu hỏi chắc chắn mà không cần gọi mô hình ngôn ngữ."""

    SIMPLE_POINT_INTENTS = (
        "o dau",
        "thong tin",
        "chi tiet",
        "trang thai",
        "thiet bi",
        "thuoc tuyen",
        "dia chi",
        "toa do",
    )
    COMPLEX_INTENTS = (
        "gan nhat",
        "gan ",
        "khoang cach",
        "ban kinh",
        "bao nhieu",
        "liet ke",
        "so sanh",
    )

    def __init__(self, db: Session):
        self.db = db

    def try_answer(self, message: str) -> dict[str, Any] | None:
        """Trả lời trực tiếp nếu nhận diện chắc chắn được loại truy vấn."""

        point_code = self._get_simple_point_code(message)
        if point_code is not None:
            return self._answer_point_lookup(point_code)

        count_filters = self._get_count_filters(message)
        if count_filters is not None:
            return self._answer_count(count_filters)

        return None

    def _answer_point_lookup(self, point_code: str) -> dict[str, Any]:
        """Chạy trực tiếp tool tra cứu một điểm mạng."""

        total_started_at = perf_counter()
        tool_started_at = perf_counter()
        point = get_point_by_code_tool(db=self.db, ma_diem=point_code)
        tool_duration_ms = (perf_counter() - tool_started_at) * 1000
        total_duration_ms = (perf_counter() - total_started_at) * 1000

        logger.info(
            "Fast query completed code=%s duration_ms=%.2f",
            point_code,
            total_duration_ms,
        )

        return {
            "answer": self._format_point_answer(point),
            "model": "direct-database",
            "execution_path": "direct_database",
            "tools_used": [
                {
                    "name": "get_point_by_code",
                    "arguments": {"ma_diem": point_code},
                    "success": True,
                    "duration_ms": round(tool_duration_ms, 2),
                }
            ],
            "timing": {
                "llm_ms": 0.0,
                "tool_ms": round(tool_duration_ms, 2),
                "total_ms": round(total_duration_ms, 2),
            },
        }

    def _answer_count(self, filters: dict[str, str]) -> dict[str, Any]:
        """Chạy trực tiếp tool đếm với các bộ lọc đã nhận diện chắc chắn."""

        total_started_at = perf_counter()
        tool_started_at = perf_counter()
        output = count_points_tool(db=self.db, **filters)
        tool_duration_ms = (perf_counter() - tool_started_at) * 1000
        total_duration_ms = (perf_counter() - total_started_at) * 1000

        logger.info(
            "Fast count query completed filters=%s duration_ms=%.2f",
            filters,
            total_duration_ms,
        )

        filter_description = ", ".join(filters.values())
        if filter_description:
            answer = (
                f"Theo dữ liệu hệ thống, có {output['count']} điểm mạng "
                f"phù hợp với điều kiện: {filter_description}."
            )
        else:
            answer = (
                f"Theo dữ liệu hệ thống, hiện có {output['count']} "
                "điểm mạng."
            )

        return {
            "answer": answer,
            "model": "direct-database",
            "execution_path": "direct_database",
            "tools_used": [
                {
                    "name": "count_points",
                    "arguments": filters,
                    "success": True,
                    "duration_ms": round(tool_duration_ms, 2),
                }
            ],
            "timing": {
                "llm_ms": 0.0,
                "tool_ms": round(tool_duration_ms, 2),
                "total_ms": round(total_duration_ms, 2),
            },
        }

    @classmethod
    def _get_simple_point_code(cls, message: str) -> str | None:
        codes = POINT_CODE_PATTERN.findall(message)
        if len(codes) != 1:
            return None

        normalized_message = _normalize_text(message)
        if any(intent in normalized_message for intent in cls.COMPLEX_INTENTS):
            return None

        has_simple_intent = any(
            intent in normalized_message for intent in cls.SIMPLE_POINT_INTENTS
        )
        normalized_code = codes[0].upper()
        code_only_pattern = re.compile(
            rf"^\s*(?:tram|diem)?\s*{re.escape(normalized_code.lower())}\s*"
            r"(?:la gi)?\s*[?.!]*\s*$",
            re.IGNORECASE,
        )
        if not has_simple_intent and not code_only_pattern.fullmatch(
            normalized_message
        ):
            return None

        return normalized_code

    @staticmethod
    def _get_count_filters(message: str) -> dict[str, str] | None:
        normalized_message = _normalize_text(message)
        count_intents = ("bao nhieu", "so luong", "dem ")
        if not any(intent in normalized_message for intent in count_intents):
            return None

        filters: dict[str, str] = {}

        device_values = {
            "router": "Router",
            "switch": "Switch",
            "olt": "OLT",
            "odf": "ODF",
        }
        for keyword, value in device_values.items():
            if re.search(rf"\b{keyword}\b", normalized_message):
                filters["thiet_bi"] = value
                break

        status_values = {
            "hoat dong": "Hoạt động",
            "bao tri": "Bảo trì",
            "su co": "Sự cố",
        }
        for keyword, value in status_values.items():
            if keyword in normalized_message:
                filters["trang_thai"] = value
                break

        type_values = {
            "mang xong": "Măng xông",
            "pop": "POP khách hàng",
            "tram": "Trạm",
        }
        for keyword, value in type_values.items():
            if re.search(rf"\b{keyword}\b", normalized_message):
                filters["loai_diem"] = value
                break

        route_match = re.search(r"\btuyen[-\s]?\d+\b", normalized_message)
        if route_match:
            route_number = re.search(r"\d+", route_match.group()).group()
            filters["ma_tuyen"] = f"TUYEN-{route_number}"

        return filters

    @staticmethod
    def _format_point_answer(point: dict[str, Any]) -> str:
        def display(value: Any) -> str:
            return "—" if value is None or value == "" else str(value)

        location = display(point.get("dia_chi"))
        if point.get("tinh"):
            location = f"{location} (Tỉnh/thành: {point['tinh']})"

        coordinates = "—"
        if point.get("vi_do") is not None and point.get("kinh_do") is not None:
            coordinates = f"{point['vi_do']}, {point['kinh_do']}"

        return "\n".join(
            [
                (
                    f"Theo dữ liệu hệ thống, điểm {display(point.get('ma_diem'))} "
                    f"({display(point.get('ten_diem'))}) có thông tin như sau:"
                ),
                "",
                f"- Địa chỉ: {location}",
                f"- Tọa độ: {coordinates}",
                f"- Tuyến: {display(point.get('ma_tuyen'))}",
                f"- Trạng thái: {display(point.get('trang_thai'))}",
                f"- Thiết bị: {display(point.get('thiet_bi'))}",
            ]
        )
