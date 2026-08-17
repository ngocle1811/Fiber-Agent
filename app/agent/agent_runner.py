import json
from time import perf_counter
from typing import Any

from openai import OpenAI, OpenAIError
from sqlalchemy.orm import Session

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tool_registry import execute_tool
from app.agent.tool_schemas import TOOL_SCHEMAS
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def _convert_tool_schemas(schemas: list[dict]) -> list[dict]:
    """
    Chuyển tool schema từ định dạng Responses API
    sang định dạng Chat Completions API.

    Responses API:
    {"type": "function", "name": "...", "parameters": {...}}

    Chat Completions API:
    {"type": "function", "function": {"name": "...", "parameters": {...}}}
    """
    tools = []
    for schema in schemas:
        tools.append({
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema.get("description", ""),
                "parameters": schema.get("parameters", {}),
            },
        })
    return tools


# Chuyển đổi một lần khi module được import.
CHAT_TOOL_SCHEMAS = _convert_tool_schemas(TOOL_SCHEMAS)


class AgentRunner:
    """
    Điều phối toàn bộ quá trình Agent xử lý một câu hỏi.

    Trách nhiệm:
    1. Gửi câu hỏi và danh sách tool cho Gemini (qua OpenAI-compatible API).
    2. Nhận yêu cầu gọi tool từ mô hình.
    3. Thực thi tool bằng Tool Registry.
    4. Gửi kết quả tool lại cho mô hình.
    5. Nhận câu trả lời cuối cùng.
    """

    def __init__(self, db: Session):
        self.db = db

        settings = get_settings()

        if not settings.GEMINI_API_KEY.strip():
            raise AppException(
                message=(
                    "Chưa cấu hình GEMINI_API_KEY trong file .env"
                ),
                status_code=500,
                error_code="GEMINI_API_KEY_MISSING",
            )

        self.model = settings.GEMINI_MODEL
        self.max_tool_rounds = settings.AGENT_MAX_TOOL_ROUNDS

        self.client = OpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url=settings.GEMINI_BASE_URL,
            timeout=settings.OPENAI_TIMEOUT_SECONDS,
            max_retries=2,
        )

    def run(self, user_message: str) -> dict[str, Any]:
        """
        Xử lý một câu hỏi của người dùng.
        Một câu hỏi có thể cần gọi nhiều tool liên tiếp.

        Ví dụ:
        - lấy thông tin điểm gốc
        - sau đó tìm măng xông gần nhất
        """

        total_started_at = perf_counter()

        total_llm_ms = 0.0
        total_tool_ms = 0.0

        tools_used: list[dict[str, Any]] = []

        # Danh sách messages gửi qua lại giữa ứng dụng và mô hình.
        # Chat Completions API dùng danh sách messages với role.
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        logger.info(
            "Agent received question=%s model=%s",
            user_message,
            self.model,
        )

        # Mỗi vòng có thể:
        # - nhận một yêu cầu gọi tool
        # - chạy tool
        # - gửi kết quả lại cho mô hình
        for round_index in range(self.max_tool_rounds + 1):
            llm_started_at = perf_counter()

            response = self._create_chat_completion(messages)

            llm_duration_ms = (
                perf_counter() - llm_started_at
            ) * 1000

            total_llm_ms += llm_duration_ms

            logger.info(
                "Gemini response completed round=%s duration_ms=%.2f",
                round_index + 1,
                llm_duration_ms,
            )

            message = response.choices[0].message

            # Giữ lại toàn bộ message của mô hình (bao gồm tool_calls).
            messages.append(message)

            tool_calls = message.tool_calls or []

            # Không còn yêu cầu gọi tool:
            # mô hình đã tạo câu trả lời cuối cùng.
            if not tool_calls:
                answer = (message.content or "").strip()

                if not answer:
                    answer = (
                        "Hệ thống chưa tạo được câu trả lời phù hợp."
                    )

                total_duration_ms = (
                    perf_counter() - total_started_at
                ) * 1000

                result = {
                    "answer": answer,
                    "model": self.model,
                    "tools_used": tools_used,
                    "timing": {
                        "llm_ms": round(total_llm_ms, 2),
                        "tool_ms": round(total_tool_ms, 2),
                        "total_ms": round(total_duration_ms, 2),
                    },
                }

                logger.info(
                    "Agent completed tools=%s llm_ms=%.2f "
                    "tool_ms=%.2f total_ms=%.2f",
                    [item["name"] for item in tools_used],
                    total_llm_ms,
                    total_tool_ms,
                    total_duration_ms,
                )

                return result

            # Đã vượt số vòng tool cho phép.
            if round_index >= self.max_tool_rounds:
                raise AppException(
                    message=(
                        "Agent đã vượt quá số vòng gọi công cụ cho phép."
                    ),
                    status_code=500,
                    error_code="AGENT_MAX_TOOL_ROUNDS_EXCEEDED",
                )

            for tool_call in tool_calls:
                tool_output, tool_info = self._execute_function_call(
                    tool_call=tool_call,
                )

                total_tool_ms += tool_info["duration_ms"]
                tools_used.append(tool_info)

                # Gửi kết quả tool lại cho mô hình.
                # Chat Completions API dùng role="tool".
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            tool_output,
                            ensure_ascii=False,
                            default=str,
                        ),
                    }
                )

        raise AppException(
            message="Agent không hoàn thành được câu hỏi.",
            status_code=500,
            error_code="AGENT_INCOMPLETE",
        )

    def _create_chat_completion(
        self,
        messages: list[dict[str, Any]],
    ):
        """
        Gọi Gemini API thông qua OpenAI-compatible Chat Completions endpoint.

        tool_choice='auto':
        mô hình tự quyết định có cần gọi tool hay không.
        """

        try:
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=CHAT_TOOL_SCHEMAS,
                tool_choice="auto",
                reasoning_effort="low",
            )

        except OpenAIError as exc:
            logger.exception(
                "Gemini API request failed model=%s",
                self.model,
            )

            raise AppException(
                message=(
                    "Không thể kết nối hoặc nhận phản hồi từ Gemini."
                ),
                status_code=502,
                error_code="GEMINI_API_ERROR",
            ) from exc

    def _execute_function_call(
        self,
        tool_call: Any,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Chuyển yêu cầu gọi tool của mô hình thành lời gọi hàm Python thật.

        Ví dụ mô hình trả:
        tool_call.function.name = count_points
        tool_call.function.arguments = {"thiet_bi": "Router"}

        Hàm này sẽ gọi:
        execute_tool(
            tool_name="count_points",
            arguments={"thiet_bi": "Router"}
        )
        """

        tool_name = tool_call.function.name

        try:
            arguments = json.loads(
                tool_call.function.arguments or "{}"
            )

            if not isinstance(arguments, dict):
                raise ValueError(
                    "Tool arguments phải là một object JSON"
                )

        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning(
                "Invalid tool arguments tool=%s arguments=%s",
                tool_name,
                tool_call.function.arguments,
            )

            output = {
                "success": False,
                "error": {
                    "code": "INVALID_TOOL_ARGUMENTS",
                    "message": (
                        "Tham số gọi công cụ không hợp lệ."
                    ),
                },
            }

            return output, {
                "name": tool_name,
                "arguments": {},
                "success": False,
                "duration_ms": 0.0,
            }

        tool_started_at = perf_counter()

        logger.info(
            "Executing tool=%s arguments=%s",
            tool_name,
            arguments,
        )

        try:
            output = execute_tool(
                tool_name=tool_name,
                db=self.db,
                arguments=arguments,
            )

            success = True

        except AppException as exc:
            # Ví dụ:
            # - không tìm thấy mã điểm
            # - không tìm thấy điểm gần nhất
            #
            # Ta không dừng toàn bộ Agent.
            # Ta gửi lỗi này lại cho mô hình để mô hình
            # trả lời rõ cho người dùng.
            output = {
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                },
            }

            success = False

        except Exception:
            logger.exception(
                "Unexpected tool error tool=%s arguments=%s",
                tool_name,
                arguments,
            )

            output = {
                "success": False,
                "error": {
                    "code": "TOOL_EXECUTION_ERROR",
                    "message": (
                        "Công cụ gặp lỗi khi truy vấn dữ liệu."
                    ),
                },
            }

            success = False

        tool_duration_ms = (
            perf_counter() - tool_started_at
        ) * 1000

        logger.info(
            "Tool completed tool=%s success=%s duration_ms=%.2f",
            tool_name,
            success,
            tool_duration_ms,
        )

        tool_info = {
            "name": tool_name,
            "arguments": arguments,
            "success": success,
            "duration_ms": round(tool_duration_ms, 2),
        }

        return output, tool_info
