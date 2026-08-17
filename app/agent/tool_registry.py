from typing import Any, Callable

from sqlalchemy.orm import Session
#File này dùng để ánh xạ: tên tool -> hàm Python thật
from app.tools.point_tools import (
    count_points_tool,
    get_point_by_code_tool,
    list_points_tool,
)
from app.tools.spatial_tools import (
    calculate_distance_tool,
    find_nearest_point_tool,
    find_points_within_radius_tool,
)

ToolFunction = Callable[..., dict[str, Any]]

TOOL_REGISTRY: dict[str, ToolFunction] = {
    "get_point_by_code": get_point_by_code_tool,
    "list_points": list_points_tool,
    "count_points": count_points_tool,
    "calculate_distance": calculate_distance_tool,
    "find_nearest_point": find_nearest_point_tool,
    "find_points_within_radius": find_points_within_radius_tool,
}

def list_available_tools() -> list[str]:
    """
    Trả về danh sách tool đang có trong hệ thống.
    """

    return list(TOOL_REGISTRY.keys())


def get_tool_function(tool_name: str) -> ToolFunction:
    """
    Lấy hàm Python thật theo tên tool.

    Ví dụ:
    tool_name = "get_point_by_code"
    -> trả về hàm get_point_by_code_tool
    """

    tool_function = TOOL_REGISTRY.get(tool_name)

    if tool_function is None:
        raise ValueError(f"Tool không tồn tại: {tool_name}")

    return tool_function


def execute_tool(
    tool_name: str,
    db: Session,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Thực thi tool theo tên và tham số.

    Hàm này sau này sẽ được Agent gọi.

    Ví dụ:
    execute_tool(
        tool_name="get_point_by_code",
        db=db,
        arguments={"ma_diem": "AGG001"}
    )
    """

    tool_function = get_tool_function(tool_name)

    return tool_function(
        db=db,
        **arguments,
    )