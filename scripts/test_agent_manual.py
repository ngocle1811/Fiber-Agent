import json

from app.core.database import SessionLocal
from app.services.chat_service import ChatService


def main():
    """
    Test Agent trực tiếp mà chưa cần gọi API.
    """

    question = "Có bao nhiêu Router?"

    print("=" * 80)
    print("Câu hỏi:")
    print(question)
    print("=" * 80)

    with SessionLocal() as db:
        service = ChatService(db)

        result = service.ask(
            message=question,
        )

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()