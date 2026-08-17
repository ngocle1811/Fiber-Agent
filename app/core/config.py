from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Settings = nơi chứa cấu hình toàn hệ thống.
    File này chỉ nên chứa cấu hình, không chứa logic xử lý nghiệp vụ.
    """
    APP_NAME: str = "fiber_Agent"
    #Literal nghĩa là biến này chỉ được nhận một số giá trị cố định.
    APP_ENV: Literal["development", "testing", "production"] = "development"
    APP_DEBUG: bool = True
    DATABASE_URL: str

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Khóa dùng để gọi Gemini API (miễn phí tại aistudio.google.com).
    # Giá trị mặc định rỗng để backend vẫn có thể khởi động
    # ngay cả khi chưa cấu hình khóa.
    GEMINI_API_KEY: str = ""

    # Model mặc định dùng cho Agent.
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # Base URL của Gemini OpenAI-compatible endpoint.
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # Timeout = thời gian chờ tối đa cho một lần gọi API.
    OPENAI_TIMEOUT_SECONDS: float = 60.0

    # Số vòng gọi tool tối đa trong một câu hỏi.
    # Giới hạn này ngăn Agent gọi tool lặp vô hạn.
    AGENT_MAX_TOOL_ROUNDS: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True, #biến trong .env phải đúng chữ hoa/chữ thường
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Trả về object Settings.
    lru_cache giúp app chỉ đọc cấu hình một lần trong quá trình chạy.
    """
    return Settings()
