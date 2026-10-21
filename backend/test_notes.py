from fastapi.testclient import TestClient
from app.main import app
from app.db.base import get_db
from app.models.user import User

client = TestClient(app)

def get_test_user():
    return User(id=1, email="test@example.com", is_active=True)

app.dependency_overrides[get_db] = get_db
# We can just override get_current_user to return a dummy user or existing user
from app.api.deps import get_current_user
app.dependency_overrides[get_current_user] = get_test_user

response = client.get("/api/v1/notes/")
print("Status Code:", response.status_code)
print("Response JSON:")
print(response.json())
