import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.security.deps import get_current_user
from app.models.user import User

client = TestClient(app)

def override_get_current_user():
    return User(id=1, email="test@example.com", username="tester")

app.dependency_overrides[get_current_user] = override_get_current_user

class TutorAPITestCase(unittest.TestCase):
    def test_1_tutor_chat_without_document(self):
        res = client.post("/api/v1/tutor/session")
        self.assertEqual(res.status_code, 200)
        session_id = res.json()["id"]

        payload = {
            "question": "What is Python?",
            "session_id": session_id,
            "document_id": None
        }
        res_chat = client.post("/api/v1/tutor/chat", json=payload)
        self.assertEqual(res_chat.status_code, 200)
        self.assertTrue(len(res_chat.content) > 0)

    def test_2_tutor_history(self):
        res = client.get("/api/v1/tutor/history")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    def test_3_invalid_api_config_fallback(self):
        # We test that our mock logic works when API is invalid
        payload = {
            "question": "Test fallback",
            "session_id": None,
            "document_id": None
        }
        res = client.post("/api/v1/tutor/chat", json=payload)
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
