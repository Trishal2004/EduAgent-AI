import requests
import uuid

# We need a token first
auth_data = {
    "email": "test@example.com",
    "password": "password",
    "full_name": "Test User"
}
# register
res = requests.post("http://localhost:8000/api/v1/auth/register", json=auth_data)
# But wait, it requires email verification!
