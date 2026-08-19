from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """
    Dữ liệu người dùng gửi tới API chat.
    """

    message: str = Field(
        min_length=1,
        max_length=2000,
        description="Câu hỏi của người dùng",
        examples=[
            "Trạm STA000001 ở đâu?",
            "Có bao nhiêu Router?",
        ],
    )

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        """
        Xóa khoảng trắng thừa ở đầu và cuối câu hỏi.
        """

        cleaned = value.strip()
        if not cleaned:
            raise ValueError(
                "Câu hỏi không được để trống"
            )

        return cleaned

class ToolExecutionInfo(BaseModel):
    """
    Thông tin một tool đã được Agent gọi.
    """

    name: str
    arguments: dict[str, Any]
    success: bool
    duration_ms: float


class AgentTiming(BaseModel):
    """
    Thời gian xử lý của từng phần.

    llm_ms:
        tổng thời gian gọi mô hình ngôn ngữ.

    tool_ms:
        tổng thời gian chạy các tool.

    total_ms:
        tổng thời gian của toàn bộ yêu cầu.
    """

    llm_ms: float
    tool_ms: float
    total_ms: float


class ChatResponseData(BaseModel):
    """
    Dữ liệu trả về từ Agent.
    """

    answer: str
    model: str
    execution_path: Literal["direct_database", "agent"]
    tools_used: list[ToolExecutionInfo]
    timing: AgentTiming
