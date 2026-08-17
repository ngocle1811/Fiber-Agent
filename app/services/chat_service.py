from typing import Any

from sqlalchemy.orm import Session

from app.agent.agent_runner import AgentRunner
from app.core.exceptions import AppException
from app.core.logging_config import get_logger


logger = get_logger(__name__)


class ChatService:
    """
    Service xử lý nghiệp vụ chat.

    Route chỉ nhận request.
    ChatService kiểm tra câu hỏi.
    AgentRunner điều phối OpenAI và các tool.
    """

    def __init__(self, db: Session):
        self.agent_runner = AgentRunner(db)

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

        return self.agent_runner.run(
            user_message=cleaned_message,
        )