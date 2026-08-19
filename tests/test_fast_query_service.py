import unittest
from unittest.mock import Mock, patch

from app.services.chat_service import ChatService
from app.services.fast_query_service import FastQueryService


POINT_DATA = {
    "id": "1",
    "ma_diem": "STA000001",
    "ten_diem": "Trạm 1",
    "dia_chi": "Hải Phòng - Khu vực 1",
    "tinh": "Hải Phòng",
    "vi_do": 15.194551,
    "kinh_do": 105.373322,
    "ma_tuyen": "TUYEN-0001",
    "trang_thai": "Hoạt động",
    "thiet_bi": "Switch",
}


class FastQueryServiceTest(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.service = FastQueryService(self.db)

    @patch(
        "app.services.fast_query_service.get_point_by_code_tool",
        return_value=POINT_DATA,
    )
    def test_simple_point_question_bypasses_llm(self, point_tool):
        result = self.service.try_answer("Trạm STA000001 ở đâu?")

        self.assertIsNotNone(result)
        self.assertEqual(result["execution_path"], "direct_database")
        self.assertEqual(result["timing"]["llm_ms"], 0.0)
        self.assertEqual(result["tools_used"][0]["name"], "get_point_by_code")
        point_tool.assert_called_once_with(db=self.db, ma_diem="STA000001")

    def test_complex_question_uses_agent_fallback(self):
        result = self.service.try_answer(
            "POP gần STA000001 nhất là điểm nào?"
        )
        self.assertIsNone(result)

    def test_question_with_two_codes_uses_agent_fallback(self):
        result = self.service.try_answer(
            "STA000001 cách POP000098 bao xa?"
        )
        self.assertIsNone(result)

    @patch(
        "app.services.fast_query_service.count_points_tool",
        return_value={"count": 42, "filters": {"thiet_bi": "Router"}},
    )
    def test_count_question_bypasses_llm(self, count_tool):
        result = self.service.try_answer("Có bao nhiêu Router?")

        self.assertEqual(result["execution_path"], "direct_database")
        self.assertEqual(result["timing"]["llm_ms"], 0.0)
        self.assertEqual(result["tools_used"][0]["name"], "count_points")
        count_tool.assert_called_once_with(db=self.db, thiet_bi="Router")


class ChatServiceRoutingTest(unittest.TestCase):
    @patch("app.services.chat_service.AgentRunner")
    @patch.object(FastQueryService, "try_answer")
    def test_fast_result_does_not_create_agent(self, try_answer, agent_runner):
        try_answer.return_value = {
            "answer": "Kết quả",
            "model": "direct-database",
            "execution_path": "direct_database",
            "tools_used": [],
            "timing": {"llm_ms": 0.0, "tool_ms": 1.0, "total_ms": 1.0},
        }

        result = ChatService(Mock()).ask("STA000001 ở đâu?")

        self.assertEqual(result["execution_path"], "direct_database")
        agent_runner.assert_not_called()

    @patch("app.services.chat_service.AgentRunner")
    @patch.object(FastQueryService, "try_answer", return_value=None)
    def test_complex_question_creates_agent(self, _try_answer, agent_runner):
        agent_runner.return_value.run.return_value = {
            "answer": "Kết quả Agent",
            "model": "gemini",
            "tools_used": [],
            "timing": {"llm_ms": 1.0, "tool_ms": 1.0, "total_ms": 2.0},
        }

        result = ChatService(Mock()).ask("Có bao nhiêu Router?")

        self.assertEqual(result["execution_path"], "agent")
        agent_runner.assert_called_once()


if __name__ == "__main__":
    unittest.main()
