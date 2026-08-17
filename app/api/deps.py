"""nếu ko có file này thì sẽ bị lặp code db = SessionLocal() ở mỗi api
                                            ...
                                            db.close()
"""
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Cung cấp database session cho mỗi request API.

    Mỗi request sẽ có một session riêng.
    Sau khi xử lý xong, session luôn được đóng.
    Nếu có lỗi, rollback để hủy các thay đổi chưa commit.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()