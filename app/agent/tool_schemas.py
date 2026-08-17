"""
Mô tả các tool để OpenAI hiểu:

- tool có tên gì
- tool dùng để làm gì
- tool cần các tham số nào

Đây chỉ là phần mô tả.
Hàm Python thật được đăng ký trong tool_registry.py.
"""


TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "get_point_by_code",
        "description": (
            "Lấy thông tin chi tiết của một điểm mạng theo mã điểm. "
            "Dùng khi người dùng hỏi một điểm cụ thể ở đâu, "
            "thuộc tuyến nào, có thiết bị gì hoặc đang ở trạng thái nào."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ma_diem": {
                    "type": "string",
                    "description": (
                        "Mã điểm mạng, ví dụ: "
                        "AGG001, STA000001, POP000098 hoặc MS000102."
                    ),
                },
            },
            "required": ["ma_diem"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_points",
        "description": (
            "Lấy danh sách điểm mạng theo một hoặc nhiều bộ lọc. "
            "Dùng khi người dùng muốn liệt kê điểm theo loại điểm, "
            "mã tuyến, tỉnh, trạng thái hoặc thiết bị."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "loai_diem": {
                    "type": "string",
                    "description": (
                        "Loại điểm: Trạm, Măng xông hoặc POP khách hàng."
                    ),
                },
                "ma_tuyen": {
                    "type": "string",
                    "description": "Mã tuyến, ví dụ: TUYEN-0001.",
                },
                "tinh": {
                    "type": "string",
                    "description": "Tên tỉnh hoặc thành phố.",
                },
                "trang_thai": {
                    "type": "string",
                    "description": (
                        "Trạng thái: Hoạt động, Bảo trì hoặc Sự cố."
                    ),
                },
                "thiet_bi": {
                    "type": "string",
                    "description": (
                        "Tên thiết bị: Router, Switch, OLT hoặc ODF."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Số kết quả tối đa cần lấy.",
                    "default": 10,
                },
                "offset": {
                    "type": "integer",
                    "description": "Vị trí bắt đầu lấy dữ liệu.",
                    "default": 0,
                },
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "count_points",
        "description": (
            "Đếm số lượng điểm mạng theo một hoặc nhiều bộ lọc. "
            "Dùng cho câu hỏi như có bao nhiêu POP, "
            "bao nhiêu Router hoặc bao nhiêu điểm đang bảo trì."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "loai_diem": {
                    "type": "string",
                    "description": (
                        "Loại điểm: Trạm, Măng xông hoặc POP khách hàng."
                    ),
                },
                "ma_tuyen": {
                    "type": "string",
                    "description": "Mã tuyến, ví dụ: TUYEN-0001.",
                },
                "tinh": {
                    "type": "string",
                    "description": "Tên tỉnh hoặc thành phố.",
                },
                "trang_thai": {
                    "type": "string",
                    "description": (
                        "Trạng thái: Hoạt động, Bảo trì hoặc Sự cố."
                    ),
                },
                "thiet_bi": {
                    "type": "string",
                    "description": (
                        "Tên thiết bị: Router, Switch, OLT hoặc ODF."
                    ),
                },
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "calculate_distance",
        "description": (
            "Tính khoảng cách giữa hai điểm mạng theo mét. "
            "Dùng khi người dùng hỏi hai điểm cách nhau bao xa."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "from_code": {
                    "type": "string",
                    "description": "Mã điểm thứ nhất.",
                },
                "to_code": {
                    "type": "string",
                    "description": "Mã điểm thứ hai.",
                },
            },
            "required": ["from_code", "to_code"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "find_nearest_point",
        "description": (
            "Tìm điểm gần nhất thuộc một loại điểm xác định. "
            "Dùng để tìm POP, măng xông hoặc trạm gần nhất "
            "so với một mã điểm gốc."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "from_code": {
                    "type": "string",
                    "description": "Mã điểm gốc.",
                },
                "target_type": {
                    "type": "string",
                    "description": (
                        "Loại điểm cần tìm: "
                        "Trạm, Măng xông hoặc POP khách hàng."
                    ),
                },
            },
            "required": ["from_code", "target_type"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "find_points_within_radius",
        "description": (
            "Tìm các điểm thuộc một loại xác định nằm trong bán kính "
            "quanh một mã điểm gốc. "
            "Dùng cho câu hỏi như có măng xông nào trong bán kính "
            "500 mét quanh AGG001 hay không."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "from_code": {
                    "type": "string",
                    "description": "Mã điểm gốc.",
                },
                "target_type": {
                    "type": "string",
                    "description": (
                        "Loại điểm cần tìm: "
                        "Trạm, Măng xông hoặc POP khách hàng."
                    ),
                },
                "radius_m": {
                    "type": "number",
                    "description": "Bán kính tính theo mét.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Số kết quả tối đa cần lấy.",
                    "default": 20,
                },
            },
            "required": [
                "from_code",
                "target_type",
                "radius_m",
            ],
            "additionalProperties": False,
        },
    },
]