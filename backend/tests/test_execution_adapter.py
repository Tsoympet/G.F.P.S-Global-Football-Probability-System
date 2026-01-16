import unittest

from backend.db import Base, engine, SessionLocal
from backend.execution_adapter import ExecutionRequest, DbExecutionAdapter
from backend.models import ExecutionOrder


class ExecutionAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    def tearDown(self):
        with SessionLocal() as db:
            db.query(ExecutionOrder).delete()
            db.commit()

    def test_db_execution_adapter_persists_order(self):
        adapter = DbExecutionAdapter()
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
        order_id = result["payload"]["id"]
        with SessionLocal() as db:
            row = db.get(ExecutionOrder, order_id)
            self.assertIsNotNone(row)
            self.assertEqual(row.fixture_id, "123")
            self.assertEqual(row.adapter, "db")


if __name__ == "__main__":
    unittest.main()
