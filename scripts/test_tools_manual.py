import json

from app.agent.tool_registry import execute_tool, list_available_tools
from app.core.database import SessionLocal


def print_result(title: str, data):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    print("Available tools:")
    for tool_name in list_available_tools():
        print(f"- {tool_name}")

    with SessionLocal() as db:
        result = execute_tool(
            tool_name="get_point_by_code",
            db=db,
            arguments={
                "ma_diem": "STA000001",
            },
        )
        print_result("Tool: get_point_by_code", result)

        result = execute_tool(
            tool_name="count_points",
            db=db,
            arguments={
                "thiet_bi": "Router",
            },
        )
        print_result("Tool: count_points", result)

        result = execute_tool(
            tool_name="list_points",
            db=db,
            arguments={
                "loai_diem": "Măng xông",
                "limit": 5,
            },
        )
        print_result("Tool: list_points", result)

        result = execute_tool(
            tool_name="find_nearest_point",
            db=db,
            arguments={
                "from_code": "STA000001",
                "target_type": "Măng xông",
            },
        )
        print_result("Tool: find_nearest_point", result)

        result = execute_tool(
            tool_name="find_points_within_radius",
            db=db,
            arguments={
                "from_code": "STA000001",
                "target_type": "Măng xông",
                "radius_m": 500,
                "limit": 10,
            },
        )
        print_result("Tool: find_points_within_radius", result)


if __name__ == "__main__":
    main()