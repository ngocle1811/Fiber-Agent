from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.chat import ChatRequest, ChatResponseData
from app.schemas.common import SuccessResponse
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=SuccessResponse[ChatResponseData],
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Gửi câu hỏi bằng ngôn ngữ tự nhiên tới Fiber Agent.

    Ví dụ:
    - Trạm STA000001 ở đâu?
    - Có bao nhiêu Router?
    - POP gần STA000001 nhất là POP nào?
    - Có măng xông nào trong bán kính 500m
      quanh STA000001 không?
    """

    service = ChatService(db)

    result = service.ask(
        message=request.message,
    )

    return {
        "success": True,
        "data": result,
    }