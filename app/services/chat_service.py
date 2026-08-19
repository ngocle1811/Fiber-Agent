from typing import Any

from sqlalchemy.orm import Session

from app.agent.agent_runner import AgentRunner
from app.core.exceptions import AppException
from app.core.logging_config import get_logger
from app.services.fast_query_service import FastQueryService


logger = get_logger(__name__)


class ChatService:
    """
    Service xử lý nghiệp vụ chat.

    Route chỉ nhận request.
    ChatService kiểm tra câu hỏi.
    AgentRunner điều phối OpenAI và các tool.
    """

    def __init__(self, db: Session):
        self.db = db
        self.fast_query_service = FastQueryService(db)

    def ask(self, message: str) -> dict[str, Any]:
        """
        Gửi câu hỏi tới Agent và nhận kết quả.
        """

        cleaned_message = message.strip()

        if not cleaned_message:
            raise AppException(
                message="Câu hỏi không được để trống.",
                status_code=400,
                error_code="EMPTY_MESSAGE",
            )

        logger.info(
            "Chat service processing question=%s",
            cleaned_message,
        )

        fast_result = self.fast_query_service.try_answer(cleaned_message)
        if fast_result is not None:
            return fast_result

        # Chỉ khởi tạo client LLM khi câu hỏi không đi được đường trực tiếp.
        agent_runner = AgentRunner(self.db)
        result = agent_runner.run(
            user_message=cleaned_message,
        )
        result["execution_path"] = "agent"
        return result
