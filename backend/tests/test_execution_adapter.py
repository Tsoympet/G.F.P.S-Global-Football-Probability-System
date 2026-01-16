import unittest

from backend.execution_adapter import ExecutionRequest, MockExecutionAdapter


class ExecutionAdapterTests(unittest.TestCase):
    def test_mock_execution_adapter_returns_payload(self):
        adapter = MockExecutionAdapter()
        req = ExecutionRequest(
            fixture_id="123",
            market="Match Winner",
            outcome="home",
            odds=2.1,
            ev=0.12,
            meta={"league": "Test"},
        )
        result = adapter.execute_value_bet(req)
        self.assertEqual(result["status"], "queued")
        self.assertEqual(result["payload"]["fixture_id"], "123")


if __name__ == "__main__":
    unittest.main()
