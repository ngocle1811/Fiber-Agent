#File này tạo kết nối tới PostgreSQL.
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.core.config import get_settings

settings = get_settings() #lấy cấu hình từ file config.py

class Base(DeclarativeBase):
    """
    Base là lớp gốc cho tất cả model database.
    Các model như NetworkPoint sẽ kế thừa từ Base.
    SQLAlchemy sẽ dựa vào Base để hiểu class Python tương ứng bảng database.
    """
    pass

engine = create_engine(
    settings.DATABASE_URL,  #chuỗi kết nối database lấy từ .env
    pool_pre_ping=True,
    echo=settings.APP_DEBUG,
)

SessionLocal = sessionmaker(
    bind=engine, #kiểm tra xem kết nối cũ còn sống ko
    autoflush=False,
    autocommit=False,
)

def get_db() -> Session:
    """
    Tạo một session database cho mỗi request API.
    Sau khi request xử lý xong, session sẽ tự đóng.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """
    Kiểm tra database có kết nối được không.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.scalar_one() == 1
    except Exception:
        return False